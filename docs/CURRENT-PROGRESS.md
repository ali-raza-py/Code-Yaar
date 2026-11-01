# Code-Yaar Current Progress

This document is the source of truth for implementation status as observed on
2026-10-30. See `docs/COURSE-PLATFORM-IMPLEMENTATION.md` for the full 100-task
checklist and final report of the Master Academy implementation.

## Verified Current State

| Item | Status | Evidence |
|---|---|---|
| Django backend (DRF, JWT auth, CORS) | Verified | `backend/config`, 164 passing tests |
| Authentication (register/login/refresh/logout, email verification, SMTP mail, password reset, profile, RBAC) | Verified | `learning/auth_*`, `docs/AUTHENTICATION.md`; delivery is reported honestly (`verification_email_sent` / audit `delivered`), proven end-to-end against Gmail |
| One-command dev startup (API + app) | Verified | `scripts/dev.ps1`, `dev.cmd` |
| Five complete courses (Python, C++, Web, Git, DSA) | Implemented | `learning/management/commands/academy/` + `seed_academy` (32 chapters, 45 lessons, 92 exercises) |
| Idempotent content seeding | Verified | `SeedAcademyIntegrityTest` — re-run creates 0 duplicates |
| Server-side sandbox grading (Python) | Verified | subprocess sandbox with timeouts; honest-grading tests |
| Certificate engine (eligibility, issuance, PDF+PNG+QR, verify, revoke, reissue, audit) | Verified | `certificates` app, 19 tests |
| Public verification pages (canonical `/verify/certificate/{id}` + `/verify/badge/{id}`, legacy `/verify/{id}` resolver) | Verified | server-rendered, real-registry lookup, 404 + noindex for unknown ids |
| Certificate viewer (`/certificates/{id}`) — premium A4 artwork, fit/zoom, PDF/PNG/print, LinkedIn share, copy link | Implemented | `components/credentials/*`, `certificate-print-root` print CSS |
| Achievement badges — premium medallion artwork (SVG+PNG server-rendered), `/achievements` grid, per-badge PNG/SVG download, LinkedIn share, verification link | Implemented | `learning/badge_art.py`, `/api/badges/{id}/download/`, public `image.png` |
| Open Graph metadata + link-preview images on public verify pages | Verified | `certificates/verify/{id}/image.png`, `badges/verify/{id}/image.png` |
| Public verification page + My Certificates + claim flow | Implemented | `/verify/*`, `/certificates`, `/certificates/{id}`, course dashboard panel |
| Answer/solution non-leakage | Verified | `AnswerLeakageTest` |
| Health endpoint | Implemented | `GET /api/health/` |
| Production configuration surface | Implemented | env-driven DB/hosts/CORS/SITE_URL/HSTS in `settings.py` + `.env.example` |
| Administrator practical content management | Implemented | Admin-only CRUD APIs and `/learn/practicals/manage` for classes/courses, subjects, and practicals with publish controls |

## Backend Test Suite

- 164 tests across `learning` + `certificates`, green:
  `cd backend && python manage.py test certificates learning`
  (auth-gate behaviour has dedicated coverage in `tests_auth.py`, 76 tests; the
  general flow suites run with `AUTH_REQUIRE_EMAIL_VERIFICATION=False` lifted,
  matching the `tests_auth.AuthAPITestCase` convention).
- `python manage.py check` passes (one outstanding `urls.W005` warning: a
  second `include('certificates.urls')` was added to `learning/api_urls.py`
  while `config/urls.py` already includes it under the same `api/` prefix).
  `makemigrations --check` clean. The XP award
  constraint now serialises its `action__in` list through `sorted()`, so
  `makemigrations` no longer emits a remove/recreate pair on every run.

## Frontend Checks

- `tsc --noEmit` clean, ESLint clean, `next build` succeeds (25 routes incl.
  `/sign-in`, `/sign-up`, `/verify-email`, `/forgot-password`,
  `/reset-password`, `/certificates`, `/certificates/[id]`, `/achievements`,
  `/verify/certificate/[id]`, `/verify/badge/[id]` and the legacy
  `/verify/[publicId]` resolver).

## Remaining Gaps / Next Steps

- Multi-language code execution (C++, JS, git) is not sandboxed; those
  courses grade via server-side answer comparison, and the course content
  states this honestly.
- Some marketing/catalog sections still render static `src/data/` content.
- Certificate PDFs use local media storage; configure object storage before
  multi-server deployments.
- The legacy `seed_courses` command is superseded by `seed_academy`.

Production readiness is *configured* (env-driven settings, hardening when
`DEBUG=False`) but not yet *deployed* — see the production checklist in
`COURSE-PLATFORM-IMPLEMENTATION.md`.
