"""Controlled SQLite -> PostgreSQL data transfer for the Code Yaar database.

Copies every user table from the legacy SQLite file into the configured
default (PostgreSQL) database in foreign-key dependency order, preserving
primary keys exactly. Postgres-only bookkeeping tables (django_migrations)
are left untouched; django_contenttypes and django_permissions are refreshed
in place because the target schema is created by the same migrations, so their
rows are identical in meaning but may differ in surrogate key.

Usage:
    python manage.py migrate_sqlite_to_postgres            # copy + reset sequences
    python manage.py migrate_sqlite_to_postgres --dry-run  # counts only, no writes
    python manage.py migrate_sqlite_to_postgres --only auth_user,certificates_certificate

The SQLite source path defaults to BASE_DIR/db.sqlite3 and can be overridden
with --sqlite-path. The source file is opened read-only and never written.
"""

import json
import pathlib
import sqlite3
import sys

from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import connection, transaction


# Transfer order: providers before dependents. Django's content apps first,
# then learning/certificates in FK-dependency order (parents listed before
# children; tables omitted here fall through to the alphabetical tail).
TRANSFER_ORDER = [
    'django_content_type',
    'auth_permission',
    'auth_group',
    'auth_group_permissions',
    'auth_user',
    'django_session',
    'django_admin_log',
    'token_blacklist_outstandingtoken',
    'token_blacklist_blacklistedtoken',
    'learning_userprofile',
    'learning_careertrack',
    'learning_course',
    'learning_course_categories',  # m2m through table
    'learning_chapter',
    'learning_lesson',
    'learning_exercise',
    'learning_hint',
    'learning_resource',
    'learning_enrollment',
    'learning_lessonprogress',
    'learning_exerciseattempt',
    'learning_snippetrun',
    'learning_xptransaction',
    'learning_achievement',
    'learning_userachievement',
    'learning_userachievement_unlocked_courses',  # m2m through table
    'learning_usernotification',
    'learning_announcement',
    'learning_announcement_recipients',  # m2m through table
    'learning_platformupdate',
    'learning_platformupdate_affected_courses',  # m2m through table
    'learning_emailcampaign',
    'learning_emailcampaignrecipient',
    'learning_platformsetting',
    'learning_maintenancesettings',
    'learning_notificationemaillog',
    'learning_project',
    'learning_project_collaborators',  # m2m through table
    'learning_projectmilestone',
    'learning_portfolio',
    'learning_follow',
    'learning_studentproject',
    'learning_projectimage',
    'learning_challenge',
    'learning_practicalclass',
    'learning_practicalsubject',
    'learning_practical',
    'learning_practicalprogress',
    'learning_practicalbookmark',
    'learning_learningactivity',
    'learning_challengesubmission',
    'learning_competition',
    'learning_competitionregistration',
    'learning_registrationformfield',
    'learning_competitionteam',
    'learning_competitionteammember',
    'learning_competitionsubmission',
    'learning_competitionresult',
    'learning_progress',
    'learning_certification',
    'learning_usercertification',
    'learning_skill',
    'learning_userskill',
    'learning_emailverificationtoken',
    'learning_passwordresettoken',
    'learning_authenticationauditlog',
    'certificates_certificate',
    'certificates_certificateevent',
]


class Command(BaseCommand):
    help = 'Copy all data from the legacy SQLite file into the default PostgreSQL database.'

    def add_arguments(self, parser):
        parser.add_argument('--sqlite-path', default=None,
                            help='Path to the legacy SQLite file (default: BASE_DIR/db.sqlite3)')
        parser.add_argument('--dry-run', action='store_true',
                            help='Report per-table row counts without writing anything')
        parser.add_argument('--only', default=None,
                            help='Comma-separated table names to restrict the transfer')

    def handle(self, *args, **opts):
        sqlite_path = pathlib.Path(opts['sqlite_path'] or settings.BASE_DIR / 'db.sqlite3')
        if not sqlite_path.exists():
            self.stderr.write(f'SQLite source not found: {sqlite_path}')
            sys.exit(1)

        # `file:` URIs mishandle Windows drive-letter paths, so connect
        # normally and never execute a write against the source here.
        src = sqlite3.connect(str(sqlite_path))
        src.row_factory = sqlite3.Row

        # Tables that exist in the Postgres target schema.
        with connection.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
            target_tables = [r[0] for r in cur.fetchall()]
        target_set = set(target_tables)

        # Tables that hold data in the SQLite source (skip sqlite_ internals).
        source_tables = [
            r['name'] for r in src.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'"
            )
        ]
        source_set = set(source_tables)

        skip = {
            'django_migrations',
        }
        # vestigial tables left in SQLite by apps that are no longer installed
        # have no PostgreSQL counterpart by design and must not fail the drift check
        source_only_ok = {'authtoken_token'}
        restrict = set(opts['only'].split(',')) if opts['only'] else None

        ordered = [t for t in TRANSFER_ORDER if t in target_set and t in source_set]
        leftovers = sorted((target_set & source_set) - set(ordered) - skip)
        plan = [t for t in ordered + leftovers if t not in skip and (not restrict or t in restrict)]

        missing_in_target = sorted(source_set - target_set - source_only_ok)
        if missing_in_target:
            self.stderr.write(
                'Refusing to continue: SQLite tables with no PostgreSQL counterpart '
                f'(schema drift): {missing_in_target}'
            )
            sys.exit(1)

        if opts['dry_run']:
            total = 0
            for table in plan:
                n = src.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                total += n
                self.stdout.write(f'{table:55s} {n:8d}')
            self.stdout.write(self.style.MIGRATE_HEADING(f'dry-run: {total} rows across {len(plan)} tables'))
            return 0

        # Topological order over the Postgres FK graph so parents are
        # populated before children; TRANSFER_ORDER breaks any ties.
        # FK edges come from Django's own introspection, one table at a
        # time: {field: (other_field, other_table, on_delete)}.
        plan_set = set(plan)
        edges = []
        with connection.cursor() as cur:
            for child in plan:
                for _field, ref in connection.introspection.get_relations(cur, child).items():
                    parent = str(ref[1])
                    if parent != child and parent in plan_set:
                        edges.append((child, parent))
        incoming = {t: set() for t in plan}
        outgoing = {t: set() for t in plan}
        for child, parent in edges:
            incoming[child].add(parent)
            outgoing[parent].add(child)
        rank = {t: TRANSFER_ORDER.index(t) if t in TRANSFER_ORDER else len(TRANSFER_ORDER)
                for t in plan}
        topo, ready = [], sorted((t for t in plan if not incoming[t]), key=lambda t: rank[t])
        visited = set()
        while ready:
            table = ready.pop(0)
            if table in visited:
                continue
            visited.add(table)
            topo.append(table)
            for child in sorted(outgoing[table], key=lambda t: rank[t]):
                incoming[child].discard(table)
                if not incoming[child]:
                    ready.append(child)
                    ready.sort(key=lambda t: rank[t])
        if len(topo) != len(plan):
            cycle = sorted(set(plan) - visited)
            self.stderr.write(f'Refusing to continue: FK cycle among tables {cycle}')
            sys.exit(1)
        plan = topo

        inserted_total = 0
        with transaction.atomic():
            # Children first (reverse FK order) so clears never violate a
            # constraint; the schema was just created by migrate, so targets
            # hold at most migration-seeded rows (content types, permissions).
            with connection.cursor() as cur:
                for table in reversed(plan):
                    cur.execute(f'DELETE FROM "{table}"')

            fields = connection.introspection.get_table_description
            # Per-table defaults for columns that exist in PostgreSQL but not
            # in the stale SQLite snapshot (added by a migration applied after
            # the backup). Values come from the model field's own default, so
            # they exactly match what the ORM would store for a new row - no
            # fabricated content. jsonb columns receive a JSON literal string.
            model_by_table = {m._meta.db_table: m for m in apps.get_models()}
            with connection.cursor() as cur:
                bool_type_code = next(
                    code for code, field in connection.introspection.data_types_reverse.items()
                    if field == 'BooleanField'
                )
            json_type_codes = {
                code for code, field in connection.introspection.data_types_reverse.items()
                if field in ('JSONField',)
            }

            def target_columns(table):
                with connection.cursor() as cur:
                    return [(d.name, d.type_code, d.is_autofield)
                            for d in fields(cur, table)]

            jobs = []
            for table in plan:
                src_cols = [d[0] for d in src.execute(f'SELECT * FROM "{table}"').description]
                src_set = set(src_cols)
                pg_cols = target_columns(table)
                bool_idx = {n for n, tc, _ in pg_cols if tc == bool_type_code and n in src_set}

                # Columns PostgreSQL needs but SQLite never had (skip the pk).
                model = model_by_table.get(table)
                extra = []  # (col, default_value)
                for name, tc, is_pk in pg_cols:
                    if name in src_set or is_pk:
                        continue
                    field = next(
                        (f for f in (model._meta.fields if model else [])
                         if f.attname == name), None
                    )
                    if field is not None and not getattr(field, 'null', False):
                        value = field.get_default()
                    elif tc in json_type_codes:
                        value = {}
                    else:
                        value = None  # nullable FK / timestamp / text column
                    if tc in json_type_codes:
                        value = json.dumps(value)
                    extra.append((name, value))

                cols = src_cols + [name for name, _ in extra]
                defaults = [v for _, v in extra]
                insert_rows = []
                for r in src.execute(f'SELECT * FROM "{table}"'):
                    coerced = [bool(r[c]) if c in bool_idx and r[c] is not None else r[c]
                               for c in src_cols]
                    insert_rows.append(tuple(coerced + defaults))

                col_list = ', '.join(f'"{c}"' for c in cols)
                placeholders = ', '.join(['%s'] * len(cols))
                jobs.append((table, insert_rows,
                             f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders})'))

            inserted_total = 0
            for table, rows, insert_sql in jobs:
                if rows:
                    with connection.cursor() as cur:
                        cur.executemany(insert_sql, rows)
                # Align Postgres sequences with the copied explicit PKs so the
                # next application INSERT cannot collide with a migrated row.
                with connection.cursor() as cur:
                    pk = next((d.name for d in fields(cur, table) if d.is_autofield), None)
                if pk:
                    with connection.cursor() as cur:
                        cur.execute(
                            'SELECT setval(pg_get_serial_sequence(%s, %s), '
                            'COALESCE((SELECT MAX("' + pk + '") FROM "' + table + '"), 0) + 1, false)',
                            (f'public.{table}', pk),
                        )
                inserted_total += len(rows)
                self.stdout.write(f'{table:55s} {len(rows):8d}')

        # The repository is under active development: a migration applied to
        # PostgreSQL after the SQLite snapshot (0030) introduced new models
        # whose content types / permissions are not in the copied rows. Running
        # `migrate` now fires Django's post-migrate hooks, which create ONLY
        # the missing content types + permissions (appended ids) and leave the
        # copied ids - referenced by admin logs and permissions - untouched.
        call_command('migrate', run_syncdb=True, verbosity=0)
        self.stdout.write(self.style.MIGRATE_HEADING(
            'Re-ran migrations to append content types / permissions for models '
            'added since the SQLite snapshot.'
        ))

        self.stdout.write(self.style.SUCCESS(
            f'Transferred {inserted_total} rows across {len(plan)} tables into PostgreSQL.'
        ))
        src.close()
        return 0
