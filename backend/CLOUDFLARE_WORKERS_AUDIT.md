# Code Yaar backend deployment audit

> **Superseded compatibility notes:** This audit predates Cloudflare's
> first-party Django WSGI adapter and Python Hyperdrive documentation for
> `psycopg`. Its claims that Django WSGI and psycopg/Hyperdrive are unsupported,
> and its "do not deploy" decision, are stale. The current isolated PoC and
> remaining verified blockers are in
> [CLOUDFLARE_BACKEND_IMPLEMENTATION.md](./CLOUDFLARE_BACKEND_IMPLEMENTATION.md).

**Archived status:** this audit originally recommended against Cloudflare based
on the adapter and database-driver documentation available at that time. The
adapter and driver claims were superseded by Cloudflare's documented Django
WSGI and Python Hyperdrive support. The remaining assessment and live blockers
are recorded in
[CLOUDFLARE_BACKEND_IMPLEMENTATION.md](./CLOUDFLARE_BACKEND_IMPLEMENTATION.md).

## What is in this repository

- Django settings module: `config.settings`
  ([settings.py](./config/settings.py)).
- CLI: [manage.py](./manage.py); WSGI: `config.wsgi.application`
  ([wsgi.py](./config/wsgi.py)); ASGI: `config.asgi.application`
  ([asgi.py](./config/asgi.py)). The settings select WSGI and the root URL
  config is `config.urls` ([urls.py](./config/urls.py)).
- Django applications: `learning` and `certificates`, plus Django admin,
  authentication, sessions, messages, static files, DRF, SimpleJWT with token
  blacklist, CORS headers, and debug toolbar in debug mode.
- The API includes health, registration/login/logout, email verification and
  password reset, courses/curriculum, enrollment/progress, assessments and
  coding submissions, XP/achievements/leaderboards, profiles/portfolio,
  competitions, admin endpoints, and certificates. There are 40 learning
  migration files and two certificate migration files, including parallel
  branches and merge migrations in the learning migration graph.
- The middleware stack includes Django security, CORS, sessions, common,
  CSRF, authentication, the learning app's maintenance middleware, messages,
  and clickjacking protection. DRF uses SimpleJWT and session authentication.
  CORS credentials are enabled; origins are read from `ALLOWED_ORIGINS`,
  while `CSRF_TRUSTED_ORIGINS` is configured separately.
- Database configuration accepts `DATABASE_URL` (parsed by `dj-database-url`),
  or discrete PostgreSQL settings, and otherwise falls back to local SQLite.
  PostgreSQL defaults to TLS and a 600-second persistent connection age.
- Email is configured through Django 6.1's `MAILERS`; the default backend is
  console, and SMTP settings are used only when the SMTP backend is selected.
  Static assets gather under `STATIC_ROOT`; uploaded media uses the default
  filesystem backend at `MEDIA_ROOT`. The URL config serves media only in
  debug mode; no durable media backend or production static-file server is
  configured here.
- The repository declares no Supabase client or Supabase Storage integration.
  The root [README](../README.md) says Supabase is deferred and not active;
  this conflicts with the deployment brief. The code can be configured for PostgreSQL, but the
  repository alone does not establish that production is currently on Supabase.
  No production URL was read and no database connection was attempted.
- The selected local virtual environment contains additional packages not
  listed in [requirements.txt](./requirements.txt) (including `numpy`, `onnxruntime`,
  `networkx`, `psutil`, and `pymupdf4llm`). They are not thereby application
  dependencies; do not copy the full local environment into a Worker bundle.
- Existing local tests cover learning, authentication, challenges, emails,
  publishing, administration, portfolios, badges, and certificates. The
  application has explicit idempotency/transaction coverage for XP, challenge
  submission replay, and certificate issuance.
- The backend has management commands for operations such as publishing
  scheduled courses and seeding content, but no Celery/RQ-style task runner or
  durable background-job integration is declared.
- A backend source scan found no Supabase SDK/storage calls or outbound HTTP
  client integration. SMTP and the externalized code-execution boundary are
  the relevant network/service integrations in the inspected code.

## Cloudflare Python Workers compatibility

Cloudflare Python Workers run Pyodide (CPython compiled to WebAssembly) in V8
isolates. A Python Worker is entered through an asynchronous `fetch` handler;
Cloudflare's documented setup uses `pywrangler`, a `pyproject.toml`, and the
`python_workers` compatibility flag. Cloudflare's package policy supports pure
Python packages, PyEmscripten wheels, and packages already included in Pyodide.
That is not equivalent to accepting ordinary CPython wheels.

| Dependency or feature | Assessment for this repository |
|---|---|
| Django 6.1 | Pure Python portions may package, but this project is configured for synchronous WSGI and the synchronous ORM. Cloudflare documents a `fetch` handler, not a Django WSGI/ASGI adapter. Pyodide's `threading` module is nonfunctional, which also prevents treating Django's normal sync/async adaptation as a drop-in server. Not verified as an application runtime. |
| Django REST Framework | Predominantly Python; packageability is plausible, but it does not supply an HTTP/WSGI server or make Django's request/database stack compatible. |
| psycopg 3 + `psycopg[binary]` | Blocking issue. The declared binary extra is for native CPython platforms. Cloudflare's Hyperdrive PostgreSQL driver documentation covers JavaScript/TypeScript drivers (`pg`, Postgres.js) and Rust `postgres`; it does not document psycopg or a Python ORM-compatible PostgreSQL transport. Passing a Hyperdrive connection string to Django does not implement that transport. |
| `dj-database-url` | Python URL/config parsing only. It can parse a string, but cannot create a usable Worker PostgreSQL driver or obtain the per-request Hyperdrive binding by itself. |
| SimpleJWT / PyJWT | Python authentication logic may package. Refresh-token rotation and blacklist depend on Django's database, so remain blocked by the database/ORM path. No `cryptography` dependency is declared or imported by this backend. |
| `cryptography` | Not a direct backend dependency and not required by the inspected authentication configuration. If it is introduced later, its exact WebAssembly wheel and algorithm support must be verified; ordinary native wheels are not assumed to work. |
| `django-cors-headers` | Python middleware may package. It does not replace correct Worker request adaptation or the production origin configuration. |
| `python-dotenv` | Python configuration helper, not a production secret mechanism. Current settings load `backend/.env`; Cloudflare secrets and bindings are exposed through Worker bindings, not automatically translated into Django's import-time `os.environ` settings. |
| `django-debug-toolbar` | Development-only in the current settings; must not be enabled in production. No reason to bundle it in a Worker deployment. |
| Pillow | Native image functionality is required by `ImageField` validation and generated PNGs. The declared dependency does not request or verify a PyEmscripten build. Treat as unverified until the exact package can be installed and exercised in the target runtime. |
| ReportLab | Required for certificate PDFs and uses font/filesystem behavior; the normal package is not evidence of a compatible PyEmscripten build. PDF generation is unverified and is a poor fit for the Free CPU/memory budget. |
| qrcode | Python QR generation is a plausible pure-Python portion, but PNG generation in this project uses Pillow and does not resolve its compatibility issue. |
| PyMuPDF (`pymupdf`) | Native PDF engine dependency; the requirements comment places it in content-extraction tools, not the normal request path. No compatible Worker build is established. Keep the tool outside the Worker bundle. |
| Subprocess code sandbox | Incompatible. Coding challenges execute learner programs using `subprocess`, temporary directories, and optional C++ compilation ([sandbox.py](./learning/services/sandbox.py)). Workers do not provide this host process/compiler model. Substituting simulated execution would remove core functionality and is not acceptable. |
| Email | The configured production option is Django SMTP, which uses a socket-based SMTP transport. The console backend is the default when not configured. A Worker would need a real HTTPS email-provider integration; switching to it is a separate behavior/integration change, not a settings-only deployment. |
| Local media/static files | Not durable. Pyodide exposes an in-memory filesystem that is lost when an isolate is destroyed and is not shared across isolates. The project uses Django's default filesystem storage for uploaded images and certificate PDFs. |

The existing functionality that cannot presently be carried over as-is includes
database-backed authentication and ORM endpoints, concurrent integrity-sensitive
XP/submission/certificate operations, real code execution, uploaded media and
PDF persistence, and configured SMTP delivery.

## Supabase and Hyperdrive

Hyperdrive supports PostgreSQL databases, including Supabase, and is available
on Workers Free and Paid plans. A Worker accesses it through a binding such as
`env.HYPERDRIVE.connectionString`; the binding configuration ID is not a
database URL. The documented PostgreSQL examples use supported Worker drivers,
not `psycopg`.

Consequently, there is no verified implementation here that connects
`config.settings.DATABASES['default']` and Django's ORM through Hyperdrive. A
custom JavaScript database bridge would not be a drop-in Django backend: Django
expects synchronous Python driver operations, transactions, savepoints, and
row-lock semantics. Replacing those operations with an asynchronous JS driver
would require a new, extensively tested database backend and would risk
changing the existing transaction guarantees. Do not set `DATABASE_URL` to a
Hyperdrive connection string as a workaround.

Keep Supabase PostgreSQL as the primary database. Run this Django application
on conventional CPython hosting and connect through a Supabase direct/session
pooler URL with TLS and an appropriately bounded connection policy. Hyperdrive
is unnecessary for that architecture because its binding is available only
inside a Worker. Apply Django migrations from a controlled CPython release job
against the intended database after backup and review; no migration was run
during this audit.

## Recommended production architecture

1. Keep the existing Django code and ORM on a maintained CPython container or
   managed Python service. Retain the existing Supabase PostgreSQL database.
2. Put Cloudflare DNS/proxy/WAF in front of that service for
   `api.codeyaar.tech`; terminate HTTPS, set `ALLOWED_HOSTS` to the API host,
   configure the actual frontend in `ALLOWED_ORIGINS` and
   `CSRF_TRUSTED_ORIGINS`, and enable secure cookies/forwarded-proto behavior.
   Do not route the database connection through a Worker.
3. Configure durable object storage for uploads and generated PDFs. No storage
   backend is configured in this repository. Use a tested S3-compatible
   backend (for example R2 from conventional Python hosting) or explicitly
   integrate Supabase Storage if that is the existing production system.
   Migrate existing files and references deliberately; Worker local disk is not
   an option.
4. Keep code execution in a separately isolated sandbox service. Do not execute
   learner-submitted programs in the Django process or a Worker. The current
   `SubprocessSandbox` is not a hardened multi-tenant boundary, so production
   sandbox isolation is also a separate operational requirement.
5. Use a transactional email provider through a supported transport. If SMTP
   is retained, run it from conventional Python hosting. For scheduled
   management commands, use a scheduler/queue outside the request handler.

A Cloudflare Worker could be considered later as a small edge proxy to an
externally hosted Django service, but it would not host Django or make
Hyperdrive usable by Django. It adds a hop and is not required for the proposed
DNS/proxy setup.

## Configuration and security notes

The existing settings use `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`,
`DATABASE_URL`, `ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, and `EMAIL_HOST*`;
they do not read the proposed `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, or
`CORS_ALLOWED_ORIGINS` names. `FRONTEND_URL`, `BACKEND_URL`, and `SITE_URL`
also affect email and certificate links. Keep production credentials in the
hosting platform's secret manager; never put them in Wrangler `vars`, source,
or a committed dotenv file.

For production, explicitly set a strong `SECRET_KEY`, `DEBUG=False`,
`ALLOWED_HOSTS=api.codeyaar.tech`, HTTPS frontend/API origins, CSRF trusted
origins, secure refresh/session/CSRF cookies, database TLS, and real email
credentials. The current fallback for `SECRET_KEY` is a development key and
`DEBUG` defaults to true, so neither default is safe for production. Existing
throttle and session behavior also needs a shared production cache rather than
per-isolate/in-process state if deployed across multiple instances.

## Cloudflare plan constraints and cost

According to the current Cloudflare limits/pricing pages:

- Workers Free: 100,000 requests per day, 10 ms CPU per HTTP request, and
  128 MB per isolate. Python's Pyodide initialization/package footprint and
  Django request work make this a particularly poor fit for a 10 ms CPU cap.
- Workers Paid: $5/month minimum, including 10 million requests and 30 million
  CPU milliseconds per month; extra requests are listed at $0.30 per million
  and extra CPU at $0.02 per million milliseconds. The per-isolate memory limit
  remains 128 MB.
- Hyperdrive Free: 100,000 database statements per day. Its documented
  per-configuration origin pool is approximately 20 connections on Free;
  long transactions can hold connections and exhaust a pool. Hyperdrive Paid
  is included in Workers Paid without an additional Hyperdrive charge.

These are platform prices, not an estimate of Supabase, the Python service,
storage, email, sandboxing, or domain costs. A reliable deployment of this
existing application is not zero-cost just because the Worker tier is free.

## Validation and deployment decision

- Repository configuration and dependency list were inspected; there is no
  existing Wrangler file or Python Worker entrypoint.
- The active Supabase URL/credentials and production resources were not
  inspected or tested. No database connection, migration, or deployment was
  attempted.
- Cloudflare's official Python Workers, package, standard-library, FFI,
  Hyperdrive PostgreSQL, Hyperdrive pricing/limits, secrets, and Workers
  pricing/limits documentation was reviewed:
  - <https://developers.cloudflare.com/workers/languages/python/>
  - <https://developers.cloudflare.com/workers/languages/python/packages/>
  - <https://developers.cloudflare.com/workers/languages/python/stdlib/>
  - <https://developers.cloudflare.com/workers/languages/python/ffi/>
  - <https://developers.cloudflare.com/hyperdrive/examples/connect-to-postgres/>
  - <https://developers.cloudflare.com/hyperdrive/platform/pricing/>
  - <https://developers.cloudflare.com/hyperdrive/platform/limits/>
  - <https://developers.cloudflare.com/workers/platform/pricing/>
  - <https://developers.cloudflare.com/workers/platform/limits/>
  - <https://developers.cloudflare.com/workers/configuration/secrets/>
- **Decision:** no `wrangler.jsonc`, Worker adapter, or Hyperdrive settings were
  added. They would imply compatibility the audit did not establish and would
  not preserve the current database, coding, media, PDF, and email features.
  Do not point `api.codeyaar.tech` at a Python Worker for this backend.
- Existing Django tests are run separately on an isolated local SQLite test
  database. Their result does not certify Pyodide/Worker compatibility or
  production Supabase connectivity.
