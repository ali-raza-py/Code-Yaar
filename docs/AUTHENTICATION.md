# Authentication

How Code Yaar authenticates people, why it is built this way, and what to
change when you deploy it.

- Backend: Django 6.1 + Django REST Framework + Simple JWT
- Frontend: Next.js App Router, single auth provider, no token in storage
- Identity: Django's built-in `auth.User` extended by `learning.UserProfile`
  (no custom user model swap — that would have required a destructive migration)

---

## 1. Token model

| Token | Where it lives | Lifetime | Readable by JS |
| --- | --- | --- | --- |
| Access (JWT) | Frontend memory only | 15 min | Yes, but only in memory |
| Refresh (JWT) | HttpOnly cookie `cy_refresh` | 7 days | No |

Why:

- A long-lived token in `localStorage` is readable by any script that manages to
  run on the page. Keeping the access token in a module-scoped variable means an
  XSS payload cannot lift a durable credential.
- The refresh token is `HttpOnly`, so JavaScript cannot read it. It is sent
  automatically because every API call uses `credentials: 'include'`.
- Refresh tokens **rotate** on every use (`ROTATE_REFRESH_TOKENS`) and the
  previous one is **blacklisted** (`BLACKLIST_AFTER_ROTATION`). A stolen refresh
  token is therefore usable at most once.

### CSRF

DRF's `APIView` is CSRF-exempt, so the two endpoints that authenticate **with a
cookie** (`token/refresh/`, `logout/`) perform the double-submit check
themselves: the `csrftoken` cookie must literally equal the `X-CSRFToken`
header (`constant_time_compare`).

The frontend bootstraps the pair from `GET /api/auth/csrf/`, which returns the
cookie's own value — **not** Django's masked token. `django.middleware.csrf.get_token()`
returns a masked variant, so comparing it against the raw cookie value would
always fail. That detail is load-bearing; do not "simplify" it.

Bearer-authenticated endpoints do not need CSRF: a cross-site request cannot set
an `Authorization` header.

---

## 2. Endpoints

All routes are mounted under `/api/auth/` and require JSON bodies.

| Method | Path | Auth | Body | Success |
| --- | --- | --- | --- | --- |
| GET | `csrf/` | public | — | `200 {csrfToken}` + `csrftoken` cookie |
| POST | `register/` | public | `full_name, username, email, password, confirm_password` | `201 {access, token_type, expires_in, user, verification_email_sent}` + refresh cookie. When `AUTH_REQUIRE_EMAIL_VERIFICATION` is on, only `{user, verification_email_sent}` — no session until the link is used |
| POST | `login/` | public | `identifier` (email or username) + `password` | `200 {access, token_type, expires_in, user}` + refresh cookie; `403 {detail, code: "email_not_verified", email, can_resend}` when the gate is on and the address is unverified |
| POST | `logout/` | cookie + CSRF | — | `200 {detail}` and the refresh cookie is cleared |
| POST | `token/refresh/` | cookie + CSRF | — | `200 {access, token_type, expires_in}`; refresh stays in the cookie |
| GET | `me/` | Bearer | — | `200` user + profile payload |
| PATCH | `me/` | Bearer | any of `username, email, first_name, last_name, full_name, bio, avatar, institution, education_level, github_url, linkedin_url` | `200` updated payload + `email_changed`, `verification_email_sent` |
| POST | `verify-email/` | public | `token` | `200 {detail, user}`; repeating a link for an already-verified account answers `200 {code: "already_verified"}` |
| POST | `resend-verification/` | optional Bearer | `email` (omit when signed in) | `200 {detail}` — generic |
| POST | `password-reset/` | public | `email` | `200 {detail}` — generic |
| POST | `password-reset/confirm/` | public | `token, password, confirm_password` | `200 {detail}` |
| POST | `change-password/` | Bearer | `current_password, new_password, confirm_password` | `200 {detail, access, expires_in}` + new refresh cookie |

### `GET /auth/me/` payload

```jsonc
{
  "user": { "id": 4, "username": "ada", "email": "ada@example.com",
            "first_name": "Ada", "last_name": "Lovelace", "full_name": "Ada Lovelace",
            "date_joined": "2026-10-30T09:00:00Z", "role": "student",
            "email_verified": false },
  "profile": { "avatar": "", "bio": "", "institution": "", "education_level": "",
               "github_url": "", "linkedin_url": "", "xp_points": 0, "streak_days": 0,
               "level": 1, "last_active_at": null, "created_at": "..." },
  // flat duplicates keep older pages working without a second request
  "avatar": "", "bio": "", "role": "student", "email_verified": false,
  "xp_points": 0, "streak_days": 0, "level": 1, "last_active_at": null
}
```

### Errors

DRF's standard shape, with field keys matching the request body:

```json
{ "email": ["An account with this email address already exists."] }
```

Token failures additionally carry a stable code:

```json
{ "detail": "This verification link has expired. Request a new one.", "code": "token_expired" }
```

`code` is one of `token_expired`, `token_used`, `token_invalid`.

Login and password-reset never reveal whether an account exists: both return one
generic message for unknown and known identifiers alike.

---

## 3. Privilege rules

- Registration always creates a **student**: `is_staff`, `is_superuser` and
  `profile.role` are pinned server-side, whatever the request contains.
- `PATCH /auth/me/` rejects `role`, `is_staff`, `is_superuser`, `is_active`,
  `permissions`, `groups`, `user_permissions` and `password` with `400` and
  writes an `AuthenticationAuditLog` entry (`privilege_escalation_blocked`).
- Roles resolve to Django groups, synced on `post_migrate` by
  `learning.apps.LearningConfig`:

| Group | Permissions |
| --- | --- |
| `Students` | view-only across learning models |
| `Instructors` | student view perms + add/change where relevant |
| `Administrators` | every learning and certificate permission |

The sync is additive — it never strips permissions an operator granted by hand.

---

## 4. Email flows

- Verification links: `{FRONTEND_URL}/verify-email?token=…` (24 h)
- Password reset links: `{FRONTEND_URL}/reset-password?token=…` (60 min)
- Only a SHA-256 hash of each token is stored. Issuing a new token marks the
  older unused ones as used, so a resend invalidates the previous link.
- Tokens are single-use; consuming one is atomic
  (`select_for_update`) and returns `ok | invalid | expired | used`.
- Delivery goes through Django 6's `MAILERS['default']`. `backend/.env` ships
  configured for **Gmail SMTP** (`smtp.gmail.com`, port `587`, STARTTLS). The
  password must be a 16-character Google **App Password** — Google stopped
  accepting account passwords for SMTP — so `EMAIL_HOST_PASSWORD` has to be
  filled in before the first send. Until it is, sending fails and the API
  reports `verification_email_sent: false` (the account is still created).
- `python manage.py mail_check <address>` prints the resolved transport and
  sends a real test message through the exact same path as the auth emails, and
  translates SMTP errors (bad password, blocked port, wrong TLS) into a hint.
- For offline work set `EMAIL_BACKEND` back to
  `django.core.mail.backends.console.EmailBackend`: the message, including the
  link, is then printed to the API window and nothing leaves the machine.
- Verification is enforced at sign-in while `AUTH_REQUIRE_EMAIL_VERIFICATION`
  is on: a correct password on an unverified account returns `403
  email_not_verified` and the sign-in screen offers a resend. Registration
  likewise issues no session in that mode, so an account never carries tokens
  before its address is confirmed.

---

## 5. Frontend integration

```
src/lib/api.ts                  token/CSRF/refresh plumbing + every endpoint
src/hooks/use-auth.tsx          AuthProvider: user, profile, signIn/signUp/signOut
src/components/auth/require-auth.tsx   RequireAuth, RedirectIfAuthenticated
src/components/auth/form-field.tsx     shared labelled input + error rendering
src/app/(auth)/sign-in | sign-up | forgot-password | reset-password | verify-email
src/app/(app)/settings          account, public profile, password, preferences
```

Rules that keep this coherent:

1. **Nothing outside `lib/api.ts` touches a token.** Components call `useAuth()`
   or the endpoint helpers, never `fetch` with an `Authorization` header.
2. **One refresh at a time.** A 401 triggers `refreshAccessToken()`, which
   shares a single in-flight promise. Parallel refreshes would rotate the token
   against itself and invalidate the session.
3. **No refresh loops.** `NO_REFRESH` lists endpoints whose own 401 is final
   (`login`, `register`, `token/refresh`, `password-reset`, `verify-email`, …).
4. **Session restore is cheap.** A boolean `cy_has_session` hint records that
   this browser signed in before, so first-time visitors make zero auth
   requests on load.
5. **Guards are UX, not security.** `RequireAuth` wraps `(app)/layout.tsx` and
   redirects to `/sign-in?next=…`; the API rejects unauthenticated requests
   regardless of what the browser renders.

`proxy.ts` is intentionally a pass-through: the refresh cookie is scoped to the
API origin, so a proxy on the frontend origin can never read it.

---

## 6. Environment variables

Backend (`backend/.env`):

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | dev placeholder | Django signing key — set a real one in production |
| `DEBUG` | `True` | `False` enables secure cookies and HSTS |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Host header allow-list |
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` when `DEBUG` | CORS allow-list for the SPA (comma separated) |
| `CSRF_TRUSTED_ORIGINS` | — | Extra trusted origins (comma separated) |
| `SITE_URL` | `http://localhost:3000` | Public site origin, used in certificate links |
| `FRONTEND_URL` | `SITE_URL` | Base for verification and reset links |
| `BACKEND_URL` | `http://127.0.0.1:8000` | Base for server-side callbacks |
| `JWT_ACCESS_TOKEN_MINUTES` | `15` | Access lifetime |
| `JWT_REFRESH_TOKEN_DAYS` | `7` | Refresh lifetime |
| `AUTH_REFRESH_COOKIE_SECURE` | `not DEBUG` | Must be `True` over HTTPS |
| `AUTH_REFRESH_COOKIE_SAMESITE` | `Lax` | Set to `None` (+ Secure) only for a cross-site frontend |
| `AUTH_REQUIRE_EMAIL_VERIFICATION` | auto | Unset: on once SMTP has a password (a login gate with no deliverable mail would lock everyone out). `True`/`False` forces it. When on, unverified accounts cannot sign in and `IsEmailVerified` endpoints reject them; staff are exempt |
| `AUTH_EMAIL_VERIFICATION_TTL_HOURS` | `24` | Verification link lifetime |
| `AUTH_PASSWORD_RESET_TTL_MINUTES` | `60` | Reset link lifetime |
| `EMAIL_BACKEND` | console backend | `backend/.env` selects `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` | — | SMTP transport, only read for the SMTP backend. Gmail: `smtp.gmail.com`, `587`, `True`, App Password |
| `DEFAULT_FROM_EMAIL` | `Code Yaar <no-reply@codeyaar.dev>` | Sender address |
| `THROTTLE_AUTH_*` | see `settings.py` | Per-scope rate limits |

Django 6 configures email through `MAILERS`; the legacy `EMAIL_*` **settings**
are rejected when `MAILERS` is defined. Transport options therefore live under
`MAILERS['default']['OPTIONS']` and are only added for the SMTP backend, because
console/locmem backends reject unknown options.

Frontend (`frontend/.env.local`):

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 7. Local development

One command starts both servers from the repository root:

```powershell
.\dev.cmd              # API on :8000, app on :3000
.\dev.cmd -Setup       # first run: install Python and npm dependencies
.\dev.cmd -BackendPort 8001 -FrontendPort 3001
```

What it does: copies `.env.example` → `.env` / `.env.local` when missing, runs
`manage.py check` and `migrate`, starts Django in a separate **Code Yaar API**
window (so server output stays readable), polls `/api/health/` until it answers,
verifies that the API returns `Access-Control-Allow-Origin` for the app origin,
then runs `next dev`. `Ctrl+C` stops both; the API process tree is terminated
with the frontend. See `scripts/dev.ps1` for flags and behaviour.

Running them by hand:

```powershell
# Backend
cd backend
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_courses        # demo@codeyaar.dev / demo123 (pre-verified)
python manage.py runserver
```

```powershell
# Frontend (second terminal)
cd frontend
npm install
npm run dev
```

Verification and reset emails are sent over SMTP using `backend/.env`. When they
stop arriving, run `python manage.py mail_check` from `backend/` to see the
resolved transport (password masked) and whether the gate is armed, then
`python manage.py mail_check --connect` to prove DNS, TCP, STARTTLS and the SMTP
login without sending anything, and finally
`python manage.py mail_check you@gmail.com` to send a real message. Failures are
reported with the exception and the setting most likely responsible. The seeded
demo account is pre-verified and bypasses the verification gate.

### "Failed to fetch"

That message is the browser hiding a transport or CORS failure. In order:

1. Is the API running? `http://127.0.0.1:8000/api/health/` must return
   `{"status": "ok"}`. Nothing on port 8000 is the most common cause.
2. Does `ALLOWED_ORIGINS` in `backend/.env` contain the origin in the address
   bar exactly? `http://localhost:3000` and `http://127.0.0.1:3000` are
   different origins, and an unlisted one gets a `200` preflight with no
   `Access-Control-*` header at all.
3. Restart the backend after changing CORS settings — they are read at startup.

`scripts/dev.ps1` performs checks 1 and 2 on every start and warns when the
header is missing.

### Migrations

```powershell
cd backend
python manage.py makemigrations --check --dry-run   # must report "No changes"
python manage.py migrate
```

`0005_userprofile_education_level_and_more` adds the profile fields and the three
auth models. It is additive — no existing table or column is dropped.

Note that `auth.User.email` is **not** unique at the database level (the built-in
model cannot be changed without a destructive swap). Uniqueness is enforced on
every write path: registration, profile update, and admin validation all reject
an address already in use, case-insensitively. If you later introduce a custom
user model, add the constraint there.

---

## 8. Tests

```powershell
cd backend
python manage.py test learning.tests_auth -v 2   # 67 dedicated auth tests
python manage.py test learning                   # 127 tests in total
python manage.py check                           # configuration sanity
```

The auth suite covers registration validation, duplicate username/email,
password strength, login by email or username, generic failures, manual
throttle enforcement, `/me/` reads and updates, privilege-escalation rejection,
email-change re-verification, verification tokens (happy path, expiry, reuse),
password reset (generic response, single use, session revocation), logout and
refresh rotation, and checks that no response body ever contains a refresh token.

Frontend:

```powershell
cd frontend
npx tsc --noEmit
npm run lint
npm run build
```

---

## 9. Deployment checklist

- [ ] `DEBUG=False` and a real `SECRET_KEY`
- [ ] `ALLOWED_HOSTS` and `ALLOWED_ORIGINS` list only your real origins
- [ ] Served over HTTPS so `AUTH_REFRESH_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` are on
- [ ] `EMAIL_BACKEND` points at SMTP with valid credentials
- [ ] `FRONTEND_URL` is the public frontend origin (reset/verify links)
- [ ] `AUTH_REQUIRE_EMAIL_VERIFICATION` set to the policy you actually want
- [ ] `python manage.py check --deploy` reviewed
- [ ] Do not enable `CORS_ALLOW_ALL_ORIGINS` and do not disable CSRF

---

## 10. Known constraints

- **Email verification is opt-in.** `AUTH_REQUIRE_EMAIL_VERIFICATION` defaults to
  `False` so existing accounts and the demo keep working. Flip it to `True` once
  every account is verified; the `IsEmailVerified` permission is already wired to
  enroll, submit and certificate issuance.
- **Session revocation is per-token, not per-user.** Logout and password change
  blacklist outstanding refresh tokens; an access token already issued stays valid
  until it expires (≤ 15 minutes). That is the trade-off of stateless JWTs.
- **The route guard runs on the client.** A hard refresh on a protected page shows
  a brief loader while the refresh cookie is exchanged for an access token.
