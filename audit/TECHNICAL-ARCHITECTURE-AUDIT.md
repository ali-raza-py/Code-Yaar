# CODE YAAR — TECHNICAL ARCHITECTURE AUDIT

> Audit document — generated 2026-10-31 by direct inspection of source,
> settings, routes and migrations. Credentials are never reproduced here;
> `.env` files are gitignored and only their *structure* (via `.env.example`)
> was examined.

## 1. System Topology

Two intentionally independent services (a decision recorded in Ali's PRD/ARCHITECTURE
and physically implemented by Abdullah's 2026-10-02 folder split):

```
Browser ── Next.js 16 App Router (:3000)
              │  REST JSON over http://localhost:8000/api  (NEXT_PUBLIC_API_URL)
              ▼
          Django 6.1 + DRF (:8000) ── SQLite (dev) / PostgreSQL (env-switchable)
              │                 └── SimpleJWT + HttpOnly refresh cookie
              ├── subprocess Python sandbox
              ├── reportlab/pillow/qrcode → PDF/PNG in local media storage
              └── Gmail SMTP (Django 6 MAILERS) for verification/reset mail
```

## 2. Backend (`backend/`)

### Apps
- **`config`** — settings (env-driven: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`,
  `ALLOWED_ORIGINS`, `SITE_URL`, `FRONTEND_URL`, JWT TTLs, throttle rates,
  HSTS/secure-cookie hardening when `DEBUG=False`), root URL conf, health
  endpoint at `/api/health/`.
- **`learning`** — 27 model classes spanning: identity (`UserProfile` +
  role groups synced on `post_migrate`), catalog (`CareerTrack`, `Course`,
  `Chapter`, `Lesson`, `Exercise`, `Hint`, `Resource`), progress
  (`Enrollment`, `LessonProgress`, `ExerciseAttempt`, `SnippetRun`, `Progress`),
  gamification (`XPTransaction`, `Achievement`, `UserAchievement` — XP awards
  DB-constrained against duplicates), build/practice (`Project`,
  `ProjectMilestone`, `Challenge`), certification registry (`Certification`,
  `UserCertification`), auth security (`EmailVerificationToken`,
  `PasswordResetToken`, `AuthenticationAuditLog` — tokens stored SHA-256-hashed,
  single-use, atomic consumption).
- **`certificates`** — `Certificate` (snapshot fields, status lifecycle
  active/revoked/superseded, `supersedes` self-FK, DB-level one-active-per
  learner+course unique constraint) + `CertificateEvent` append-only audit.

### Services
- `services/sandbox.py` + `language_adapter.py` — subprocess-isolated Python
  execution, 10 s timeouts, test-case-driven grading; ungradeable submissions
  record honest `pending` (covered by `HonestGradingIntegrityTest`).
- `services/auth.py` — registration/verification/reset flows with *honest*
  delivery reporting (`verification_email_sent` only when the SMTP transport
  actually accepted the message; render-only backends are detected and reported
  false). `mail_check` management command diagnoses DNS→TCP→STARTTLS→login.
- `services/completion.py`, `services/xp.py`, `services/achievements.py` —
  completion tracking, XP ledger, badge awarding.
- `badge_art.py` / `badge_share_art.py` / `branding.py` — deterministic
  server-rendered SVG/PNG medallion + share artwork with the brand logo.
- `certificates/pdf.py` / `png.py` / `qrutil.py` — landscape-A4 reportlab PDF
  with embedded QR → `{SITE_URL}/verify/certificate/{public_id}`, PNG
  link-preview renders for Open Graph.

### API surface (observed in `api_urls.py`, `auth_urls.py`, `certificates/urls.py`)
`/api/` — courses, tracks, lessons, exercises (+`/api/exercises/{id}/`),
attempts/runs, enrollments, progress, leaderboard, challenges, projects,
achievements, badges download, health; `/api/auth/` — 12 endpoints (register,
login, logout, token/refresh, csrf, me GET/PATCH, verify-email,
resend-verification, password-reset + confirm, change-password) with per-scope
throttling; `/api/certificates/…` — eligibility, issuance (412 breakdown when
ineligible, idempotent, `select_for_update`), owner-gated download, public
verify. BasicAuth removed from DRF defaults. Known wrinkle: duplicate
`certificates.urls` include under `api/` causes Django `urls.W005` warning
(documented, non-fatal).

### Authentication architecture (VERIFIED against `docs/AUTHENTICATION.md` + code)
Access JWT lives in frontend memory only; refresh JWT in `HttpOnly` cookie
`cy_refresh` with rotation + blacklist; double-submit CSRF on the two
cookie-authed endpoints using the *unmasked* cookie value (documented as
load-bearing); enforced email-verification gate (`AUTH_REQUIRE_EMAIL_VERIFICATION`,
auto-armed once SMTP has credentials); privilege-escalation fields rejected
with audit entries; role → Django-group RBAC (Students/Instructors/
Administrators).

### Content pipeline
`seed_academy` materialises 5 courses / 32 chapters / 45 lessons / 92 exercises
from structured Python data (`commands/academy/*.py`); idempotent, cascade-
deactivating, never deleting; `seed_courses` (legacy) and `seed_projects` also
present. DB: 10 learning migrations + 2 certificate migrations, `makemigrations
--check` clean per docs.

## 3. Frontend (`frontend/`)

- **Next.js 16 App Router, TypeScript, Tailwind v4**, 27 routes in three groups:
  `(public)` landing/about/courses/verify×3, `(auth)` 5 screens, `(app)` 13
  authenticated routes; `RequireAuth` guard on `(app)/layout.tsx` (UX only —
  API enforces independently).
- **Design system**: single token source in `globals.css` (`:root` + `.dark`,
  `@theme inline` aliases → governed utilities; ban-on-raw-hex convention
  enforced across live components); bimodal radius, surface semantics,
  difficulty/state palettes; `@media (hover:hover)`-gated hovers, global
  `:focus-visible` fallback, `prefers-reduced-motion` + `MotionProvider`;
  `100dvh` workspace.
- **Data access**: one typed client (`lib/api.ts`, ~1000+ lines) owning
  tokens/CSRF/refresh single-flight, `NO_REFRESH` endpoint set,
  `withTransportRetry` for sandbox calls during hot-restarts, blob downloads
  with auth headers; `lib/server-verify.ts` server-renders public verify pages
  against the real registry; `lib/share.ts` composes LinkedIn share URLs.
- **Performance architecture**: three.js/3D components lazy-loaded via
  `next/dynamic`; fonts self-hosted through `next/font` (Fraunces/Figtree/
  JetBrains Mono). A Lighthouse program (Performance 66 → 90+ target) ran on
  2026-10-31; its final score is not re-verified by this audit.
- **Editor/motion stack**: CodeMirror 6 (python/js/sql langs, `--syn-*`
  token theme), framer-motion, react-three-fiber subset.

## 4. Cross-cutting decisions (with evidence)

| Decision | Made by | Where recorded |
|---|---|---|
| Frontend/backend independent services | both (docs by Ali, split by Abdullah) | `docs/ARCHITECTURE.md` §1, §3 |
| PostgreSQL→SQLite-fallback now, Supabase deferred | Ali | ARCHITECTURE §7, README, memory |
| No custom-user swap (UserProfile instead) — avoids destructive migration | Ali's auth session | AUTHENTICATION.md header |
| No fabricated data anywhere; honest statuses | Ali | AI-CODING-RULES, task-202 session, `AnswerLeakageTest` |
| Original identity; reference patterns not copies | Ali | ARCHITECTURE §15, anti-cloning memory |
| Tokens never in localStorage | Ali's auth session | AUTHENTICATION.md §1 |
| `SITE_URL` must be a public domain for share previews | Ali | memory + README guidance |

## 5. Security posture observed

JWT rotation+blacklist, SHA-256-hashed one-time tokens, generic auth errors
(no account enumeration), rate throttles per auth scope, allow-listed public
verify payload, DB-level certificate uniqueness, owner-gated downloads, audit
logs for auth and certificate lifecycle, CSRF on cookie endpoints, HSTS/secure
cookies under `DEBUG=False`. No secrets committed — `.env` excluded via
`.gitignore`; only `.env.example` (structure, no values) is tracked.

## 6. Architecture risks / debts

1. Single-server assumptions: local media storage for certificates; no CDN.
2. `urls.W005` duplicate include (cosmetic, flagged in CURRENT-PROGRESS).
3. Python-only judge — C++/JS/git "execution" courses are concept-graded.
4. Client-side route guard causes brief loader flash on hard refresh (documented trade-off).
5. Unreferenced legacy UI code (`dc-*` survivors except learning-entry, `particle-logo`, parts of `components/3d`) retaining raw hex outside token governance.
6. No CI/CD — all verification is local-command based.
