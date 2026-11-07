# Backend Deployment — OCI Always Free Pilot

## Status

**Prepared, not deployed.** OCI provisioning, a read-only Supabase connectivity check, and the backend DNS change were authorized, but this environment has no OCI CLI/configuration and could not resolve the public API domain. No OCI resources or DNS records were changed. The existing local Supabase configuration passed a read-only `SELECT 1`; no credentials were displayed or added. No migrations have been run; they still require separate explicit approval.

The approved pilot target is an OCI Ampere A1 VM running conventional Linux/CPython, Django under Gunicorn, Caddy for HTTPS and static/media delivery, Supabase PostgreSQL as the database, and a separately running Docker-based code-execution service. Cloudflare Workers is not used for this backend.

## Why OCI for the $0 pilot

OCI is a practical fit for the stated zero-cost constraint because the application can run in a normal CPython process, can connect to PostgreSQL over TLS, and can keep persistent media on a mounted volume. The code runner can use Docker isolation without putting the Docker socket in the Django process.

OCI documents Always Free A1 capacity of up to **2 OCPUs and 12 GB RAM total**, with up to **200 GB total block volume**. This is quota-limited capacity, not a reservation or SLA. A1 capacity may be unavailable in the home region; Oracle can reclaim idle Always Free instances under its published utilization policy. Account verification may require a payment card. Usage outside Always Free quotas can incur charges.

Expected OCI infrastructure cost is **$0/month only while all resources remain within Always Free quotas**. This excludes the existing Supabase plan, domain registration, and any usage outside OCI free quotas. No paid resources or services have been selected. Keep billing alerts enabled and verify the account's free-tier eligibility before provisioning.

## Provider comparison

| Provider | Free/eligibility facts | Fit for this backend |
|---|---|---|
| OCI Always Free A1 | Up to 2 OCPUs, 12 GB RAM and 200 GB total block volume in the home region; capacity is not guaranteed and idle instances can be reclaimed. | Best match for a strict $0 conventional CPython pilot, persistent local media and a separate Docker runner. Accept single-VM availability/reclamation risk. |
| Azure App Service | The F1 plan is $0 with shared compute, 60 CPU minutes/day, 1 GB RAM and 1 GB storage. Microsoft's pricing page says the free plan has no SLA and is not supported for production. Azure for Students provides a $100 credit for 12 months, not an indefinite free server. | Suitable for trials or student-credit-backed work, not a durable $0 production commitment for this app and code runner. |
| PythonAnywhere Free | One web app and two consoles, but outbound internet is restricted to specific HTTP(S) sites. | Not selected: the backend needs PostgreSQL connectivity to Supabase over the database protocol/port, not just HTTP(S) allowlisted access. |
| Render Free | Free web services sleep after 15 idle minutes, can take about a minute to wake, and have ephemeral filesystems; free services cannot attach persistent disks. Render says not to use free instances for production. | Useful for previews, not suitable for this always-on API, local media, and code runner. |
| Railway Free | $0 subscription with $1/month free usage credit; per-service defaults include 0.5 GB RAM, 1 vCPU and 0.5 GB volume. Usage beyond the credit is billed. | Better CPython compatibility than Workers, but the small usage credit and resource envelope do not make a dependable $0 production guarantee for Django plus isolated code execution. |
| Cloudflare Python Workers | The repository-specific compatibility findings are documented in [CLOUDFLARE_WORKERS_AUDIT.md](./CLOUDFLARE_WORKERS_AUDIT.md). | Not selected: the current Django/PostgreSQL/psycopg and subprocess code-runner architecture is not a drop-in Python Worker deployment. |

Official references:

- [OCI Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)
- [Azure App Service Linux pricing and F1 limitations](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/)
- [Azure for Students](https://azure.microsoft.com/en-us/free/students/)
- [PythonAnywhere pricing and free-account limits](https://www.pythonanywhere.com/pricing/)
- [Render free plan limitations](https://render.com/docs/free)
- [Railway plans and pricing](https://docs.railway.com/reference/pricing/plans)
- [OCI Email Delivery overview](https://docs.oracle.com/en-us/iaas/Content/Email/Concepts/emailoverview.htm)

## Audit findings

- Django settings module: `config.settings`; WSGI entry point: `config.wsgi.application`.
- The local effective database configuration is PostgreSQL on a Supabase host, using discrete `DB_*` settings. This confirms configuration only; **live connectivity and credentials have not been tested**.
- Django uses `DEBUG` from the environment, allows local hosts by default, and has configurable CORS/CSRF. Those development defaults are not safe production configuration.
- Django's base settings store uploads under local `MEDIA_ROOT`. The production settings below use a persistent OCI volume. Existing user/course/project image fields are served from `/media/`; the Caddy configuration blocks direct access to stored certificate PDFs, whose download API already enforces owner/staff permissions.
- Certificate download and public-preview APIs render their files through Django; the certificate PDF is not served as a public static file.
- Email is configured through Django's `MAILERS` settings. Local email credentials and successful delivery are unverified. Production settings require SMTP credentials and email verification.
- `/api/health/` is a liveness endpoint only. `/api/health/ready/` has been added as a read-only `SELECT 1` database readiness probe. It does not expose connection details.
- Existing learner-code execution currently has a local subprocess implementation. The production settings select the new separate Docker runner; it is not safe to expose the existing host subprocess runner as a public production service.
- The three portfolio test failures were traced to maintenance state surviving test transaction rollback. The focused maintenance and portfolio regression set passed **38/38** on an isolated local SQLite test database. The complete test suite has not been rerun.

## Deployment layout

The prepared files are in `deploy/oracle/`:

- `codeyaar-api.service` — Gunicorn service; does not receive Docker socket access.
- `codeyaar-sandbox-runner.service` — separate runner process with the Docker group and a loopback-only listener.
- `sandbox.Dockerfile` — Python 3.13 and C++ toolchain for learner code.
- `Caddyfile` — HTTPS reverse proxy for `api.codeyaar.tech`, static assets and public images.

The runner is intentionally constrained: containers have no network, no Linux capabilities, a read-only root filesystem, a read-only source mount, a 256 MB memory limit, a half-CPU limit, a process limit, a 10-second wall-clock ceiling, and bounded output. The runner is authenticated over loopback. These controls need validation on the selected OCI Linux image before public traffic is enabled. Keep Docker patched; membership in the `docker` group is effectively root-equivalent, so only the dedicated runner account may belong to it.

Media files remain on `/srv/codeyaar/media`; this avoids an unplanned migration of existing files to a new storage service. Caddy serves only the known public image upload directories and returns 404 for other `/media/` paths. Certificate files under `/media/certificates/` therefore remain private and should be downloaded only through the authenticated certificate API.

## Production environment variables

Do not commit a populated environment file. Store the API environment in `/etc/codeyaar/api.env` with owner/group and permissions that allow only root and the `codeyaar` service account to read it. Store runner-only settings in `/etc/codeyaar/sandbox-runner.env`, readable only by root and `codeyaar-runner`.

Required API environment variable names:

| Purpose | Names |
|---|---|
| Django security | `DJANGO_SECRET_KEY` (or `SECRET_KEY`), `DJANGO_ALLOWED_HOSTS` (or `ALLOWED_HOSTS`), `SITE_URL`, `FRONTEND_URL` |
| Supabase PostgreSQL | `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_SSLMODE`, optional `DB_CONN_MAX_AGE` |
| Browser security | `CORS_ALLOWED_ORIGINS` (or existing `ALLOWED_ORIGINS`), `CSRF_TRUSTED_ORIGINS` |
| SMTP | `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` or `EMAIL_USE_SSL`, `DEFAULT_FROM_EMAIL` |
| Isolated code runner | `SANDBOX_RUNNER_TOKEN`, optional `SANDBOX_RUNNER_URL` |
| Persistent files/logging | optional `MEDIA_ROOT`, `STATIC_ROOT`, `LOG_LEVEL` |

Production always forces `DEBUG=False`; no `DJANGO_DEBUG` value can enable debug mode. Use the existing Supabase database and its current host, database name, user and port. Set `DB_SSLMODE=require`. Do not change the database provider. If Supabase network controls require a pooler, use the Supabase-recommended connection mode; set `DB_CONN_MAX_AGE=0` for transaction pooling, otherwise production defaults to 60 seconds with health checks. Allow the VM's egress IP in Supabase only after explicit approval.

Configure `ALLOWED_HOSTS` with the API hostname and loopback names used by local health checks. Use HTTPS origins only in `ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`; include the deployed frontend origin when known. Configure the SMTP provider's required sender/domain authentication before requiring verification emails.

HTTPS redirects, secure cookies, and one-year HSTS are configured. HSTS `includeSubDomains` and preload are deliberately disabled until ownership and HTTPS readiness of every subdomain have been verified.

Generate one random runner token of at least 32 characters out of band and place the same value in the API and runner environment files. Never put it in the repository, a command-line argument, or deployment documentation.

## Preparation and deployment commands

These are **operator-run instructions for a later approved deployment**, not commands executed in this session:

1. Provision an eligible Always Free A1 VM in the account's home region. Confirm the selected OS architecture is ARM64 and the instance has only Always Free resources attached.
2. Install a supported Linux distribution, Docker Engine, Caddy, Python, and systemd. Create dedicated `codeyaar` and `codeyaar-runner` accounts; add only `codeyaar-runner` to the Docker group.
3. Check out the repository under `/opt/codeyaar`, create `/opt/codeyaar/venv`, and install `backend/requirements.txt`. A clean ARM64 install has not yet been verified.
4. Create `/srv/codeyaar/media` and `/srv/codeyaar/sandbox` with ownership and permissions for the respective service accounts. Do not put credentials in either directory.
5. Create the two protected environment files described above, then install the supplied systemd units and Caddyfile. Do not enable the services until configuration checks pass.
6. Build the runner image from the backend directory:

   ```sh
   docker build --platform linux/arm64 \
     -f deploy/oracle/sandbox.Dockerfile \
     -t codeyaar-sandbox:latest .
   ```

7. With the production environment file available to the service account, run:

   ```sh
   python manage.py check --deploy
   python manage.py collectstatic --noinput
   ```

8. Review migrations without applying them:

   ```sh
   python manage.py showmigrations
   python manage.py migrate --plan
   ```

   Take and verify a Supabase backup before any schema change. Do not run `migrate` until the plan and backup have been reviewed and the operator explicitly approves.

9. Start the runner and API services, validate their logs and local readiness, then point the approved `api.codeyaar.tech` DNS record at the VM. Caddy obtains HTTPS certificates after DNS and inbound ports 80/443 are working.

Production commands should use `DJANGO_SETTINGS_MODULE=config.production`. The systemd unit sets this explicitly. No migration runs automatically at service startup.

## Verification checklist

Not yet run against a deployed service:

- `GET /api/health/` — liveness only.
- `GET /api/health/ready/` — database readiness and read-only `SELECT 1`.
- Runner health — authenticated `GET http://127.0.0.1:8765/health`.
- Production Django tests, API authentication, registration, email verification, password reset, courses, progress, quizzes, challenge grading, XP/leaderboard transactions, certificates, profiles/uploads, and admin permissions.
- SMTP delivery, browser CORS/CSRF/cookie behavior, public media URLs, and certificate access controls.
- Clean Linux ARM64 dependency installation and real Docker execution tests.
- A read-only `SELECT 1` using the existing backend `.env` Supabase PostgreSQL configuration succeeded from this Windows workspace. This verifies connectivity from this environment only, not from an OCI VM.

The runner's focused unit tests are in `learning/tests_sandbox_runner.py`; they validate payload limits, transport authentication, result conversion, child-environment secret filtering, and required Docker isolation flags without executing learner code on the host. **11/11 runner tests and 2/2 readiness-probe tests passed** with an isolated local SQLite test database. **38/38 portfolio and maintenance regression tests passed**, including the three previously failing portfolio cases. The production `manage.py check --deploy --settings=config.production` exited successfully with dummy values and a deliberately unreachable database hostname; it made no live database connection. It emitted only the expected `security.W005` and `security.W021` warnings because HSTS subdomains and preload remain disabled until domain readiness is verified. Pylance reported no errors in the changed Python files. A real container smoke test is still required on the OCI host before enabling challenge execution.

## Domain, backups and rollback

`api.codeyaar.tech` is configured as the intended Caddy site, but domain ownership and DNS access have not been verified. No DNS changes have been made.

Back up Supabase using the existing Supabase backup/PITR facilities available to the account, and regularly test a restore to a non-production project. Back up `/srv/codeyaar/media` independently; a database backup does not include these local files. Keep a known-good application release and the previous service/config files so rollback can redeploy the previous code and restart the API/runner without changing database state. Do not reverse migrations automatically; restoration of database state requires a separately reviewed recovery plan.

Rollback procedure:

1. Disable new traffic at Caddy or point the DNS record back to its prior target.
2. Stop the affected systemd service. Keep the prior release and media volume intact.
3. Restore the last known-good application release and service configuration, then restart and verify liveness/readiness.
4. If a reviewed migration was applied, stop and assess compatibility; restore from the approved backup only under an explicit recovery decision. Do not run speculative reverse migrations against production.

## Remaining limitations

- OCI account access and a VM are unavailable from this environment; the authorized provisioning could not proceed. No DNS changes were made, and public DNS resolution of `api.codeyaar.tech` could not be verified here.
- SMTP delivery, the VM's Supabase connectivity/allowlist, and a production deployment URL remain unverified.
- The ARM64 dependency installation, production Django tests, Docker kernel/cgroup support, and runner container execution remain unverified.
- OCI Always Free capacity and availability are not guaranteed; the service has no production SLA and may be reclaimed under the published idle-instance policy.
- A single VM is a pilot, not high availability. VM loss affects the API, media volume and runner. Keep independent database and media backups.
- Code execution is CPU- and concurrency-limited and shares the VM's finite resources. Large-scale or long-running grading needs a queue and separately scalable runner fleet rather than increasing limits on the API host.
- Stage 2/frontend deployment has **not** started and remains blocked until Stage 1 is verified and separately approved.
