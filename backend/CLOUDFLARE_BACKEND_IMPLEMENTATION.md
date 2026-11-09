# Cloudflare Django Backend Compatibility POC

**Status: dependency install and Wrangler dry-run verified; local Worker
runtime and deployment remain unverified.** The reported Cloudflare build
failure occurred because the build ran `uv run pywrangler deploy` without
installing the CLI, and from outside the isolated Worker root. `workers-py`
is in the `dev` dependency group, and Pywrangler also refuses to run from the
backend root because the production `requirements.txt` is there. The Worker
project is isolated in `backend/cloudflare/`; the build must set that as its
root and install all groups before running Pywrangler.

The project selects Python 3.13 and Pillow 11.3.0, which resolves against the
matching Pyodide 0.28.3 index. The complete Worker dependency set and a clean
Wrangler dry-run have passed. Image upload and certificate handling pass on
CPython with Pillow 11.3.0, but Worker-runtime tests remain unverified. No
Worker has been deployed, no DNS/routes were changed, and no production
configuration or database was modified.

The first connected-build deployment then failed with Cloudflare error 10021
(`multipart: message too large`). Wrangler measured the staged Worker at
80,528 KiB uncompressed, above Cloudflare's 64 MiB Worker-size limit. The
application uses boto3 only through Django's S3 storage backend, but the
default Botocore wheel includes service models for hundreds of AWS services.
The staging script now retains Botocore's shared configuration and S3 model
only. This preserves the configured R2/S3 storage client while removing
unreferenced service metadata. A clean re-sync and rebuild then removed the
remaining generated `.po`, `.mo`, `.pyc`, `.pyo`, `__pycache__`, and
`*.dist-info` artifacts from the Worker bundle. The final dry-run now uploads
46,770.87 KiB uncompressed / 12,548.75 KiB gzip, well below Cloudflare's 64
MiB Worker-size limit, and it completes without the 10021 multipart error. The
Worker name is aligned to `code-yaar` to match the connected-build setting and
avoid name override warnings. The reduced bundle's boto3 S3 client and Django
S3Storage presigned-URL generation passed local checks.

The Worker project root is `backend/cloudflare/`, isolated from the
conventional `backend/requirements.txt`. Cloudflare Workers Builds must use
this root so Pywrangler can find its manifest without encountering the
production dependency file.

Build command:

```sh
uv sync --locked --all-groups && uv run --locked pywrangler sync && uv run --locked python prepare_app.py && cd dist && uv run --project .. --locked pywrangler deploy --dry-run --config wrangler.jsonc
```

Deploy command (only after deployment is approved):

```sh
cd dist && uv run --project .. --locked pywrangler deploy --config wrangler.jsonc
```

`workers-py` is a development-group dependency, so `uv sync --locked
--all-groups` explicitly installs it. The build stages the existing Django
modules into a clean `dist/` directory, then validates a dry-run there. The
deploy command runs from this staged directory so local virtual environments,
secrets, and build metadata cannot enter the Worker bundle.

Set Cloudflare Workers Builds' **Root directory** to `backend/cloudflare`
relative to the repository root. Do not include a leading `/` or trailing
slash. In particular, `/backend/cloudflare/` is not the path to enter. The
repository root is the directory containing the `backend` folder; the
`pyproject.toml`, `uv.lock`, and `wrangler.jsonc` files are inside
`backend/cloudflare/`.

The POC is separate from the existing Oracle deployment preparation:

- `cloudflare/worker.py` uses Cloudflare's documented Django WSGI adapter.
- `config/cloudflare.py` reads Django secrets from Worker bindings, takes
  PostgreSQL connection fields from the `HYPERDRIVE` binding, and configures
  persistent media through the R2 S3 API. This is configuration scaffolding,
  **not a completed Supabase/Hyperdrive integration**: there is no Hyperdrive
  ID or staging database binding, and no Worker database connection has been
  tested. Django's direct staging connection is verified separately below.
- `cloudflare/pyproject.toml` is an isolated Worker dependency set. It targets Python
  3.13+ as in Cloudflare's template, uses `psycopg` without the existing
  CPython-only `binary` extra, and excludes Gunicorn, Django Debug Toolbar, and
  PyMuPDF.
- `cloudflare/wrangler.jsonc` is a non-production config with no route and a placeholder
  Hyperdrive ID. It is intentionally not deployable until configured with an
  isolated non-production database.

The only application behavior change is `UserProfile.avatar_url()`: under the
Worker storage setting, it returns the configured remote storage URL instead of
constructing a local `/media/` API URL. Existing local/Oracle behavior and
legacy absolute avatar URLs are preserved.

## Compatibility choices

### Django WSGI

The Worker entrypoint follows Cloudflare's documented
[`workers.wsgi.entrypoint(application)` Django example](https://developers.cloudflare.com/workers/languages/python/packages/django/).
It sets `DEBUG=False` and disables dotenv loading before Django settings are
imported, so a local `.env` can never be used as Worker configuration.

### PostgreSQL and Hyperdrive

The database remains PostgreSQL. `config.cloudflare` maps the binding's
`host`, `port`, `user`, `password`, and `database` into Django's normal
PostgreSQL backend. The Worker project depends on the documented `psycopg`
driver, not `psycopg[binary]`; the latter requests a native CPython binary
wheel and is not included in the Worker dependency set. The connection uses
`sslmode=disable` to the Hyperdrive binding as in Cloudflare's Python driver
examples; Hyperdrive manages the origin connection. Django's persistent
connections are disabled (`CONN_MAX_AGE=0`) so per-isolate connections are not
reused. Existing `transaction.atomic()` and row-locking business logic is
unchanged.

Direct Django-to-Supabase staging connectivity and a source-authoritative data
sync have since been verified (details below). This is **not** Worker-to-
Supabase connectivity. Create and test a Hyperdrive configuration against the
intended non-production Supabase database before deployment. The placeholder
in `wrangler.jsonc` remains unresolved; no Hyperdrive ID or binding has been
connected or exercised.

### Secrets and other settings

Worker secrets are read through the documented `workers.env` API; no secret
values belong in `wrangler.jsonc`, `pyproject.toml`, source, or a committed
dotenv file.

| Worker secret name | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Django signing and session key |
| `EMAIL_HOST_PASSWORD` | SMTP authentication |
| `SANDBOX_RUNNER_TOKEN` | Authentication to an external execution service |
| `R2_ACCESS_KEY_ID` | R2 S3-compatible access key |
| `R2_SECRET_ACCESS_KEY` | R2 S3-compatible secret key |

Set non-secret Worker variables for allowed hosts, CORS/CSRF origins, site and
frontend URLs, SMTP host/user/port/TLS mode, the HTTPS runner URL, R2 S3
endpoint, and bucket name. The settings module fails closed when required
values or bindings are missing. The Hyperdrive database credentials are
provided by its binding rather than copied to Worker variables.

### Persistent files

The project currently uses Django filesystem storage for uploaded images and
certificate PDFs; Worker isolate disk is not durable. The POC selects a
separate Cloudflare R2 bucket through `django-storages`' S3 backend, with
signed object URLs. This is a persistent object service; it is not wired to
Supabase Storage because the repository has no Supabase Storage integration.
No bucket or access keys were created, no write/read/delete smoke test was run,
and no existing media was migrated. Existing files must be backed up and
migrated to the bucket before a cutover. Private certificate downloads must
continue through their permission-checked Django API.

## Pyodide, filesystem, and subprocess findings

Cloudflare packages must be pure Python, PyEmscripten wheels, or present in
Pyodide. A normal CPython wheel is not sufficient.

| Dependency / feature | POC treatment | Verification |
|---|---|---|
| Django, DRF, SimpleJWT, CORS headers | Included; Django served by official WSGI adapter | Existing API tests pass on CPython only; Worker package/runtime not exercised |
| `psycopg[binary]` from `requirements.txt` | Excluded. Worker project declares documented `psycopg` without the binary extra | Hyperdrive not available locally; no driver connection test |
| Pillow | Required by existing image upload/validation and generated PNGs; pinned to 11.3.0 for the Python 3.13 runtime | Complete dependency sync succeeds on Pyodide 0.28.3. Image formats and certificate PNG rendering still need a local Worker-runtime test |
| ReportLab and qrcode | Included because certificate APIs use them | Target-runtime PDF/QR generation and Free CPU use remain unverified |
| PyMuPDF | Excluded; optional document extraction is not part of Django request imports | Keep content extraction outside the Worker |
| `gunicorn`, `django-debug-toolbar` | Excluded; Worker uses its WSGI adapter and `DEBUG=False` | Not needed by this Worker |
| `django-storages[s3]` / boto3 | Included for R2 persistence | Package install, S3 signing and object I/O need a Worker/R2 test |
| Local media/static filesystem | Django default media storage is replaced with R2 | No local persistent disk is assumed; static asset delivery and packaged branding assets still need a separate smoke test |
| `subprocess`, `tempfile`, `shutil` | Used by `SubprocessSandbox` and the separate Docker runner, not intended for execution inside the Django Worker | The sandbox module contains local process/file code; learner code must never run in the Worker |

The `branding/logo.png` file and ReportLab's optional host-font lookup are
filesystem references. The PDF code can fall back to ReportLab core fonts, but
the logo asset must be included in the Worker bundle. Pywrangler packaging and
certificate generation have not yet verified this.

## Blocking incompatibilities and required next tests

1. **Workers Free CPU is not viable for authenticated Code Yaar traffic.**
   Cloudflare documents 10 ms CPU per HTTP request and 128 MB per isolate on
   Free. In the selected local Django environment, one default password check
   measured 921.88–968.75 ms process CPU over five runs (median 953.12 ms).
   That is CPython on this workstation, not a Pyodide measurement, but it
   demonstrates that password verification alone has no credible path to the
   10 ms Free budget. Cloudflare also notes authentication-heavy requests
   commonly take 10–20 ms. **Do not use the Free plan for this backend.** A
   Paid-plan Pyodide benchmark is still required; local CPython timings are not
   a substitute. The Wrangler config also explicitly sets `cpu_ms` to 10, so
   this limit would apply even on a paid account until deliberately changed.
2. **Pyodide dependency resolution is runtime-specific.** Pywrangler 1.17.9
   maps compatibility dates on or after 2026-09-08 to Python 3.14.2 and
   Pyodide index 314.0.7. That index has no usable Pillow wheel; changing the
   Pillow version alone does not fix that runtime. The Worker config now uses
   2026-09-07, which selects Python 3.13.2 and Pyodide 0.28.3, and pins Pillow
   11.3.0. In an isolated copy without `.env`, SQLite data, virtual
   environments, or the conventional production `requirements.txt`, Pywrangler
   resolved and installed the complete declared Worker dependency tree,
   including Pillow, ReportLab, qrcode, psycopg, Django, and boto3. The
   production requirements file was not modified. Runtime import, image
   decoding/validation, certificate PDF/PNG generation, and R2 I/O remain
   unverified and block deployment until tested.
3. **Challenge execution still needs an external runner deployment.** The
   production runner is a separate Docker service bound to `127.0.0.1`, while
   a Worker has no shared loopback with that host. The remote sandbox client
   now permits an HTTPS origin (without URL credentials, path, query, or
   fragment); it continues to reject remote plaintext HTTP and disables
   redirects. No HTTPS runner is available here, and Python Workers TLS
   transport and authenticated requests against it have not been tested.
   Never use the subprocess sandbox in the Worker.
4. **Cloudflare Hyperdrive remains unconfigured.** Supabase staging was
   synchronized from SQLite: 9,257 rows across 72 model-backed tables, with
   exact post-sync row-value verification. Django's normal settings now connect
   directly to that staging database and report no pending migrations. The
   Wrangler Hyperdrive ID is still a placeholder, so the Worker has not been
   connected to Supabase. Local Django connections do not test Hyperdrive,
   Pyodide psycopg, pooling, authentication, or APIs. Before deployment, run
   database read/write/rollback, authentication, and selected API checks
   through local Wrangler against staging only. Do not point tests at
   production or run production migrations.
5. **R2 and Pyodide package/runtime proof is pending.** There is no isolated
   R2 bucket/access key available here. Verify dependency resolution, Django
   startup, upload/download/delete, private certificate retrieval, logo
   loading, PNG validation, and certificate PDF generation under Pywrangler.
   Any native-only wheel or filesystem assumption that fails is a stop
   condition, not a reason to silently omit that endpoint.
6. **The existing production runner and storage configuration are not
   Cloudflare-ready.** The OCI runner/config files remain untouched. Static
   asset delivery, external SMTP connectivity, throttling/cache behavior, and
   scheduling need independent tests and Cloudflare-specific configuration.

## Local Django validation

The following ran with `PYTHON_DOTENV_DISABLED=1`, `DATABASE_URL` removed,
`DB_ENGINE=sqlite`, and Django's temporary test database. Test email was
forced to the in-memory backend. No production database was contacted:

```text
manage.py test config.tests learning.tests_auth
  learning.tests_challenges learning.tests_storage certificates.tests --verbosity 1
Ran 114 tests in 161.668s
OK
```

These tests cover readiness SQL, registration/login/token flows, challenge
read/write and XP idempotency, certificate APIs/transactions, and database
rollback behavior on local SQLite. The suite also executes local fixture code
through the existing CPython subprocess sandbox; that is test behavior only
and is not part of the Worker runtime. After the HTTPS runner URL policy was
added, a second focused run of `learning.tests_sandbox_runner config.tests
learning.tests_storage` passed 18/18.

## Supabase staging schema and data verification

On 2026-11-08, the staging project reference was verified against the Supabase
pooler username before connecting. Credentials were not printed, and
production settings/data were not used.

- `migrate --check`: passed; zero unapplied staging migrations.
- `makemigrations --check --dry-run`: no model changes missing migration files.
- Schema comparison: all 72 managed Django model tables and 794 expected
  columns exist in the 73-table public schema. No table was created manually.
- The source-authoritative transfer copied **9,257 rows across 72 model-backed
  tables** in a PostgreSQL transaction, preserving primary keys and resetting
  sequences. JSON values use Django's psycopg JSONB adapter.
- A read-only post-transfer verification compared every copied row to SQLite:
  **9,257 rows matched exactly**, with no row or column mismatches. Users,
  groups, courses, and the auth-user sequence were independently checked.
- A consistent, reopen-verified snapshot export of the prior staging contents
  (73 tables, 9,984 rows) exists in the session's private files. It is not a
  PostgreSQL-native dump and a restore was not tested.
- Staging `django_migrations` history (75 rows) was preserved rather than
  replaced by SQLite's stale history. The SQLite-only `authtoken_token` row
  was excluded because there is no corresponding current Django model,
  migration, or staging table.
- The local `.env` had an unparseable `DATABASE_URL`; only that malformed
  setting was disabled, leaving the verified discrete staging `DB_*` values
  in place. Django's normal settings now pass `check`, `migrate --check`, and
  a read-only ORM connectivity check.

This verifies the direct Django-to-Supabase staging connection; it does
**not** connect the Cloudflare Worker through Hyperdrive. The Hyperdrive
binding ID remains a placeholder, and no Worker database request has been
tested.

## Safe continuation gate

Do not deploy or configure DNS while the Worker build is blocked. Before
considering a deployment:

1. Create isolated Supabase staging data and a Hyperdrive config for it.
2. Configure Worker secrets using Cloudflare's secret manager; do not put
   values in config files or `.dev.vars` committed to source.
3. Run `uv run pywrangler dev` against staging, then test database read/write,
   transaction rollback/commit, authentication, and critical APIs.
4. Resolve the Pillow wheel blocker without dropping image/certificate
   behavior, then prove a complete Pyodide package sync and Worker startup.
5. Configure a Paid-plan CPU limit that meets application needs and benchmark
   actual Pyodide requests. The current Wrangler limit is 10 ms, matching the
   Free plan cap; raising it requires a suitable plan and explicit config
   change. Keep 10 ms as the Free-plan failure threshold.
6. Deploy an independently reviewed HTTPS runner endpoint and test signed
   execution requests, then rerun the challenge API tests.
7. Only after every blocker is cleared, separately authorize any production
   migration, deployment, or DNS change.

## Official references

- [Cloudflare Django on Python Workers (WSGI adapter and secrets)](https://developers.cloudflare.com/workers/languages/python/packages/django/)
- [Cloudflare Hyperdrive with Python Workers (psycopg, binding, concurrency)](https://developers.cloudflare.com/hyperdrive/examples/python-workers/)
- [Cloudflare Python package compatibility](https://developers.cloudflare.com/workers/languages/python/packages/)
- [Workers Free/Paid limits and CPU timing](https://developers.cloudflare.com/workers/platform/limits/)
- [R2 S3 API compatibility](https://developers.cloudflare.com/r2/api/s3/api/)
