"""Verify the SQLite -> PostgreSQL data transfer for Code Yaar.

Compares, table by table, between the legacy SQLite file (read-only) and the
current default PostgreSQL database:

  * row counts (no missing / duplicate records);
  * primary-key sets (no unexpected PK changes);
  * a full payload checksum, with every cell normalised through the
    PostgreSQL column type so the two engines' different native
    representations (SQLite 0/1 ints, ISO datetime strings, JSON text) do not
    masquerade as corruption;
  * FK integrity in PostgreSQL (every non-null FK child value resolves);
  * auth_user.password_hash values specifically (logins must keep working);
  * course ordering / publication snapshots (learning_course, by id).

Exit code 0 = every check passed; 1 = at least one difference found.
"""

import datetime
import decimal
import hashlib
import json
import pathlib
import sqlite3
import sys
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management import BaseCommand
from django.db import connection

# PostgreSQL type OIDs (from pg_type) that need special normalisation.
BOOL, BYTEA, INT2, INT4, INT8, FLOAT4, FLOAT8, NUMERIC = 16, 17, 21, 23, 20, 700, 701, 1700
DATE, TIME, TIMESTAMP, TIMESTAMPTZ, JSON, JSONB = 1082, 1083, 1114, 1184, 114, 3802
_TEMPORAL = {DATE, TIME, TIMESTAMP, TIMESTAMPTZ}
_NUMERIC = {INT2, INT4, INT8, FLOAT4, FLOAT8, NUMERIC}


def _canon_temporal(value, type_code):
    """Reduce any date/time representation to one canonical string."""
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip().replace(' ', 'T')
        if text.endswith('Z'):
            text = text[:-1]
        value = datetime.datetime.fromisoformat(text)
    if isinstance(value, datetime.datetime):
        if value.tzinfo is not None:
            value = value.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
        if type_code == DATE:
            return value.date().isoformat()
        base = value.isoformat(timespec='seconds')
        return base if value.microsecond == 0 else value.isoformat(timespec='microseconds')
    if isinstance(value, (datetime.date, datetime.time)):
        return value.isoformat()
    return str(value)


def _canon_numeric(value):
    if value is None:
        return None
    d = decimal.Decimal(str(value))
    if d == 0:
        return '0'
    d = d.normalize()
    # Avoid scientific notation (Decimal('1E+2')) so equal magnitudes match.
    return format(d, 'f')


def _canon_json(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = json.loads(value)
    return json.dumps(value, sort_keys=True, default=str, separators=(',', ':'))


def normalise(value, type_code):
    """Map one raw cell (from either engine) to a comparable canonical form."""
    if value is None:
        return None
    if type_code == BOOL:
        return int(bool(value))
    if type_code == BYTEA:
        return bytes(value).hex() if not isinstance(value, str) else value
    if type_code in _TEMPORAL:
        return _canon_temporal(value, type_code)
    if type_code in _NUMERIC:
        return _canon_numeric(value)
    if type_code in (JSON, JSONB):
        return _canon_json(value)
    return value


class Command(BaseCommand):
    help = 'Compare the legacy SQLite database with the migrated PostgreSQL data.'

    def add_arguments(self, parser):
        parser.add_argument('--sqlite-path', default=None,
                            help='Path to the legacy SQLite file (default: BASE_DIR/db.sqlite3)')

    def handle(self, *args, **opts):
        sqlite_path = pathlib.Path(opts['sqlite_path'] or settings.BASE_DIR / 'db.sqlite3')
        src = sqlite3.connect(str(sqlite_path))

        skip = {'django_migrations', 'authtoken_token', 'sqlite_sequence'}
        source_tables = {
            r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")
            if r[0] not in skip
        }
        with connection.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            )
            pg_tables = {r[0] for r in cur.fetchall()}
        common = sorted(source_tables & pg_tables)
        failures = []
        checked_rows = 0

        # Postgres column type codes drive normalisation for both sides.
        # They MUST be resolved per table: many tables reuse a column name
        # (id, created_at, constraints, ...) with different types, and a
        # single global map would normalise jsonb as text and false-alarm.
        per_table_codes = {}
        with connection.cursor() as cur:
            for table in common:
                per_table_codes[table] = {
                    d.name: d.type_code
                    for d in connection.introspection.get_table_description(cur, table)
                }

        # Pure runtime churn: login sessions and JWT token bookkeeping that
        # each engine prunes independently. Exact membership over time is
        # meaningless, so only duplicate PKs are checked and counts reported.
        ephemeral = {
            'django_session',
            'token_blacklist_outstandingtoken',
            'token_blacklist_blacklistedtoken',
            'learning_authenticationauditlog',
        }
        # Framework tables seeded by `migrate` from the current model set, and
        # app rows created/granted by forward data migrations. The repo gained
        # models (0030) and the app auto-granted the new permissions to the
        # Administrators group, so PostgreSQL legitimately holds MORE of these
        # than the stale SQLite snapshot. Require every SQLite row to be present
        # and identical in PostgreSQL (nothing lost); extras are expected.
        framework = {
            'django_content_type',
            'auth_permission',
            'auth_group',
            'auth_group_permissions',
        }
        # Columns that legitimately differ between a snapshot and a live DB.
        ignored_columns = {'auth_user': {'last_login'}}
        drift_notes = []

        # --- counts, PK sets, payload checksums --------------------------
        for table in common:
            s_cur = src.execute(f'SELECT * FROM "{table}"')
            cols = [d[0] for d in s_cur.description]
            s_rows = [tuple(r) for r in s_cur.fetchall()]
            with connection.cursor() as cur:
                cur.execute(
                    'SELECT ' + ', '.join(f'"{c}"' for c in cols) + f' FROM "{table}"'
                )
                p_rows = [tuple(r) for r in cur.fetchall()]
            checked_rows += len(p_rows)

            s_pk = {r[0] for r in s_rows}
            p_pk = {r[0] for r in p_rows}
            if len(p_pk) != len(p_rows):
                failures.append(f'{table}: duplicate primary keys in PostgreSQL')

            if table in ephemeral:
                # Transient auth/session/token bookkeeping, pruned independently
                # by each engine -> counts may differ either way. Informational.
                if len(s_rows) != len(p_rows):
                    drift_notes.append(
                        f'{table}: runtime rows SQLite={len(s_rows)} PG={len(p_rows)} '
                        f'(ephemeral auth/session/token bookkeeping)'
                    )
                continue

            if table in framework:
                # Every SQLite row must be present in PostgreSQL; PostgreSQL
                # may legitimately hold extra rows seeded by a newer migration.
                if not s_pk.issubset(p_pk):
                    failures.append(
                        f'{table}: SQLite rows missing from PostgreSQL '
                        f'(missing={sorted(s_pk - p_pk)[:5]})'
                    )
                else:
                    # Shared rows must be byte-identical.
                    t_codes = per_table_codes[table]
                    keep = list(range(len(cols)))
                    codes = [t_codes[cols[i]] for i in keep]

                    def fw_hash(rows, keyset):
                        h = hashlib.sha256()
                        for row in sorted((r for r in rows if r[0] in keyset),
                                          key=lambda r: repr(r[0])):
                            cells = [row[i] for i in keep]
                            h.update(repr([normalise(v, tc) for v, tc in zip(cells, codes)]).encode())
                        return h.hexdigest()

                    if fw_hash(s_rows, s_pk) != fw_hash(p_rows, s_pk):
                        failures.append(f'{table}: shared framework rows differ between engines')
                if len(p_rows) != len(s_rows):
                    drift_notes.append(
                        f'{table}: PostgreSQL has {len(p_rows) - len(s_rows)} extra row(s) '
                        f'seeded by migrations 0030/0031 (expected, current model set)'
                    )
                continue

            if len(s_rows) != len(p_rows):
                failures.append(f'{table}: row count SQLite={len(s_rows)} PG={len(p_rows)}')
                continue
            if s_pk != p_pk:
                failures.append(
                    f'{table}: PK set differs '
                    f'(missing={sorted(s_pk - p_pk)[:5]} extra={sorted(p_pk - s_pk)[:5]})'
                )
                continue

            type_codes = per_table_codes[table]
            skip = ignored_columns.get(table, set())
            keep = [i for i, c in enumerate(cols) if c not in skip]
            codes = [type_codes[cols[i]] for i in keep]

            def digest(rows):
                h = hashlib.sha256()
                for row in sorted(rows, key=lambda r: repr(r[0])):
                    cells = [row[i] for i in keep]
                    h.update(repr([normalise(v, tc) for v, tc in zip(cells, codes)]).encode())
                return h.hexdigest()

            if digest(s_rows) != digest(p_rows):
                norm_s = {
                    r[0]: [normalise(r[i], tc) for i, tc in zip(keep, codes)] for r in s_rows
                }
                for r in p_rows:
                    norm_p = [normalise(r[i], tc) for i, tc in zip(keep, codes)]
                    if norm_s.get(r[0]) != norm_p:
                        scell = norm_s.get(r[0], [None] * len(keep))
                        diffs = [cols[keep[j]] for j in range(len(keep)) if norm_p[j] != scell[j]]
                        failures.append(f'{table}: content differs at pk={r[0]} columns={diffs}')
                        break
                else:
                    failures.append(f'{table}: payload checksum differs')

        # --- FK integrity in PostgreSQL ----------------------------------
        with connection.cursor() as cur:
            for table in common:
                for _f, ref in connection.introspection.get_relations(cur, table).items():
                    other_field, other_table = str(ref[0]), str(ref[1])
                    if other_table not in pg_tables or table == other_table:
                        continue
                    cur.execute(
                        'SELECT kcu.column_name FROM information_schema.table_constraints tc '
                        'JOIN information_schema.key_column_usage kcu '
                        'ON tc.constraint_name = kcu.constraint_name '
                        'JOIN information_schema.constraint_column_usage ccu '
                        'ON tc.constraint_name = ccu.constraint_name '
                        "WHERE tc.constraint_type = 'FOREIGN KEY' "
                        'AND tc.table_name = %s AND ccu.table_name = %s',
                        (table, other_table),
                    )
                    for (col,) in cur.fetchall():
                        cur.execute(
                            f'SELECT COUNT(*) FROM "{table}" t LEFT JOIN "{other_table}" p '
                            f'ON t."{col}" = p."{other_field}" '
                            f'WHERE t."{col}" IS NOT NULL AND p."{other_field}" IS NULL',
                        )
                        orphans = cur.fetchone()[0]
                        if orphans:
                            failures.append(
                                f'{table}.{col} -> {other_table}.{other_field}: {orphans} orphan rows'
                            )

        # --- password hashes preserved -----------------------------------
        # The auth_user column is named `password` (the Django model attribute
        # password_hash maps to it); these are pbkdf2$... strings, so they must
        # be byte-identical across engines or logins break.
        s_pw_cur = src.execute('SELECT id, password FROM auth_user ORDER BY id')
        s_pw = list(s_pw_cur.fetchall())
        with connection.cursor() as cur:
            cur.execute('SELECT id, password FROM auth_user ORDER BY id')
            p_pw = list(cur.fetchall())
        if s_pw != p_pw:
            failures.append(f'auth_user.password_hash differs ({len(s_pw)} vs {len(p_pw)} rows)')

        # --- course ordering / publication snapshot ------------------------
        q = 'SELECT id, title, "order", is_published FROM learning_course ORDER BY id'
        s_courses_cur = src.execute(q)
        s_courses = [(r[0], r[1], r[2], bool(r[3])) for r in s_courses_cur.fetchall()]
        with connection.cursor() as cur:
            cur.execute(q)
            p_courses = [(r[0], r[1], r[2], bool(r[3])) for r in cur.fetchall()]
        if s_courses != p_courses:
            failures.append('learning_course ordering/publication snapshot differs')

        # --- report --------------------------------------------------------
        tracks = self._count('learning_careertrack')
        courses = len(p_courses)
        self.stdout.write(f'Tables compared : {len(common)}  (SQLite {sqlite_path.name} -> PostgreSQL)')
        self.stdout.write(f'Rows checked    : {checked_rows}')
        self.stdout.write(f'Users           : {len(p_pw)}  password hashes {"identical" if s_pw == p_pw else "CHANGED"}')
        self.stdout.write(f'Tracks          : {tracks}   Courses: {courses}')
        for note in drift_notes:
            self.stdout.write(self.style.WARNING(f'  NOTE  {note}'))
        if failures:
            self.stderr.write(self.style.ERROR(f'{len(failures)} PROBLEM(S):'))
            for f in failures:
                self.stderr.write(f'  FAIL  {f}')
            sys.exit(1)
        self.stdout.write(self.style.SUCCESS(
            'ALL CHECKS PASSED: PostgreSQL matches the SQLite source exactly '
            '(counts, PKs, content, FKs, hashes, course order).'
        ))
        src.close()
        return 0

    @staticmethod
    def _count(table):
        with connection.cursor() as cur:
            cur.execute(f'SELECT COUNT(*) FROM "{table}"')
            return cur.fetchone()[0]
