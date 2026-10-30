# Course Platform Implementation — Checklist & Final Report

This document tracks the 100 implementation tasks from the
**CODE YAAR — MASTER ACADEMY IMPLEMENTATION PROMPT**, phase by phase, and
closes with the verification report of what was actually built and tested.

Legend: `[x]` verified done in this repository · `[~]` partially done / noted
below · `[ ]` not done.

---

## Phase A — Audit & Baseline (1–10)

- [x] 1. Read the full master prompt and enumerate every requirement.
- [x] 2. Audit the existing backend (models, views, serializers, sandbox).
- [x] 3. Audit the existing frontend (API client, routes, mock data).
- [x] 4. Audit docs (PRD, architecture, progress) against reality.
- [x] 5. Run `manage.py check` — no issues.
- [x] 6. Run `makemigrations --check --dry-run` — no missing migrations.
- [x] 7. Run the backend test suite to capture the baseline (42 tests; 21 errors + 1 failure found).
- [x] 8. Reproduce the `SECRET_KEY=` empty-value crash in `.env` handling.
- [x] 9. Fix: `os.getenv('SECRET_KEY') or <dev fallback>` so an empty env var cannot crash cookie signing.
- [x] 10. Fix: debugging exercises without test cases now grade against the authored solution instead of silently returning pending (sandbox routing).

## Phase B — Foundation & Configuration (11–20)

- [x] 11. Media storage configured for certificate PDFs (`MEDIA_URL`, `MEDIA_ROOT`).
- [x] 12. `SITE_URL` setting drives verification links and QR codes.
- [x] 13. `CERTIFICATE_DEFAULT_PASSING_SCORE` env-configurable.
- [x] 14. Health endpoint `GET /api/health/` returns `{"status": "ok"}`.
- [x] 15. `certificates` app registered in `INSTALLED_APPS`.
- [x] 16. Certificate URLs wired into the root API config.
- [x] 17. `STATIC_ROOT` configured for `collectstatic`.
- [x] 18. `.env.example` documents SITE_URL, CERT_PASSING_SCORE and production extras.
- [x] 19. PDF dependencies installed and pinned in `requirements.txt` (reportlab, qrcode, pillow).
- [x] 20. Database layer verified: SQLite for dev, PostgreSQL selected via env.

## Phase C — Data Model (21–32)

- [x] 21. `Course.certification_enabled` toggle.
- [x] 22. `Course.certification_passing_score` per-course threshold.
- [x] 23. `Course.require_all_lessons` rule flag.
- [x] 24. `Course.require_final_assessment` rule flag.
- [x] 25. `Exercise.is_final_assessment` flag for assessment items.
- [x] 26. `Certificate` model: `public_id`, `credential_id`, owner/enrollment FKs.
- [x] 27. Certificate content snapshots (student name, course title, score, policy version).
- [x] 28. Certificate status lifecycle: active / revoked / superseded.
- [x] 29. `supersedes` self-FK linking re-issued certificates to originals.
- [x] 30. Conditional unique constraint: one **active** certificate per learner+course.
- [x] 31. `CertificateEvent` append-only audit trail (issued/downloaded/revoked/reissued/corrected).
- [x] 32. Migrations generated and applied; admin registered with revoke/reissue actions.

## Phase D — API Layer (33–46)

- [x] 33. `GET /api/me/certificates/` — learner's own certificates.
- [x] 34. `GET /api/courses/{slug}/certificate/eligibility/` — real progress vs. rules.
- [x] 35. `POST /api/courses/{slug}/certificate/issue/` — server-verified issuance.
- [x] 36. Issuance returns 412 with requirement breakdown when not eligible.
- [x] 37. Issuance is transactional + `select_for_update` — duplicate-safe under concurrency.
- [x] 38. Issuance is idempotent — a second call returns the existing certificate.
- [x] 39. `GET /api/certificates/{public_id}/download/` — owner/staff only (403 otherwise).
- [x] 40. Downloads recorded in the audit trail.
- [x] 41. `GET /api/certificates/verify/{public_id}/` — public, AllowAny, 404 when unknown.
- [x] 42. Public payload is privacy-safe (no email, user id, scores breakdown, admin notes).
- [x] 43. Revoked → `valid: false` + `revoked: true`; superseded → `valid: false`.
- [x] 44. Eligibility never trusts client input — recomputed from DB every call.
- [x] 45. Missing learner-facing exercise detail route registered (`GET /api/exercises/{id}/`).
- [x] 46. Serializers verified to omit `solution_code`, `test_cases`, `hidden_tests`, `is_correct`.

## Phase E — Five Complete Courses (47–64)

Content lives in `learning/management/commands/academy/` as structured data and
is materialised by `python manage.py seed_academy` (idempotent; 5 courses,
32 chapters, 45 lessons, 92 exercises; never deletes — retired content is
deactivated).

- [x] 47. Course 1 — **Python Programming Foundations** (7 modules + final assessment, runnable sandbox-graded code exercises).
- [x] 48. Course 2 — **C++ Programming Fundamentals** (6 modules; graded honestly via MCQ/output-prediction/fill-blank — no fake C++ execution).
- [x] 49. Course 3 — **Web Development Foundations: HTML, CSS & JavaScript** (5 modules + portfolio project).
- [x] 50. Course 4 — **Git and GitHub Fundamentals** (4 modules; command workflows).
- [x] 51. Course 5 — **Problem Solving and Data Structures in Python** (5 modules; sandbox-executed code exercises).
- [x] 52. Every course has: tracks → course → chapters/modules → lessons → exercises → final assessment.
- [x] 53. Every lesson carries objective, markdown body, duration, XP and knowledge checks.
- [x] 54. Every course ends with a ≥5-item final assessment flagged `is_final_assessment`.
- [x] 55. Code exercises only exist where the sandbox really executes them (Python).
- [x] 56. Exercise mix includes code, MCQ, output prediction, debugging and fill-blank.
- [x] 57. Lessons include expected outputs, common mistakes and explanations.
- [x] 58. `seed_academy` re-run is safe (0 created / all updated on second run).
- [x] 59. Seeder re-points courses to the right track instead of colliding on slug.
- [x] 60. Seeder cascades deactivation to stale lessons/exercises (no orphan graded items).
- [x] 61. Certificate service ignores content inside deactivated chapters.
- [x] 62. Course XP/hours derived from real content (no fabricated stats).
- [x] 63. Seeded data verified against the certificate eligibility service.
- [x] 64. Demo learner (`demo@codeyaar.dev`) created by the seeder for manual verification.

## Phase F — Frontend Integration (65–80)

- [x] 65. Typed API client extended with `certificates` namespace (api.ts).
- [x] 66. `CertificateSummary`, `CertificateEligibility`, `PublicVerification` TS types.
- [x] 67. `/certificates` page — learner's certificate list with status badges.
- [x] 68. Authenticated PDF download via blob (token header), not a bare link.
- [x] 69. `/verify/[publicId]` public page — valid / revoked / superseded / not-found states.
- [x] 70. Course dashboard shows a server-driven **Certificate panel** (requirements, score).
- [x] 71. "Claim my certificate" button calls the issuing API; 412 refreshes requirement state.
- [x] 72. Sidebar navigation includes Certificates.
- [x] 73. No client-side eligibility logic — all decisions come from Django.
- [x] 74. Empty/loading/error states per existing conventions.
- [x] 75. `tsc --noEmit` clean.
- [x] 76. ESLint clean on all touched files.
- [x] 77. `next build` succeeds (routes `/certificates` and `/verify/[publicId]` present).
- [~] 78. Course catalog marketing pages still read from static `data/` files for some mock sections; live course API powers learn/dashboard/catalog where wired.
- [x] 79. Verification links from certificates deep-link into the public verify page.
- [x] 80. No fabricated counts introduced into the frontend.

## Phase G — Certificates Engine (81–90)

- [x] 81. Eligibility service: enrollment, lesson completion, final-assessment threshold.
- [x] 82. Assessment score = passed items / total items, from server-graded attempts only.
- [x] 83. Transactional issuance re-verifies eligibility inside the transaction.
- [x] 84. Certificate PDF: landscape A4, brand header, learner, course, score, dates, credential id.
- [x] 85. QR code embedded in the PDF pointing at `{SITE_URL}/verify/{public_id}/`.
- [x] 86. PDF stored on the certificate; regeneration on demand if missing at download time.
- [x] 87. PDF failure cannot undo the DB record (issuance stays verifiable).
- [x] 88. Revocation with mandatory reason + audit event.
- [x] 89. Corrected reissue supersedes the original (never two active rows).
- [x] 90. Admin: read-only event inlines; revoke/reissue actions; immutable audit.

## Phase H — Security & Integrity (91–96)

- [x] 91. BasicAuthentication removed from DRF defaults.
- [x] 92. Production hardening when `DEBUG=False`: HSTS, secure cookies, nosniff; optional `SECURE_PROXY_SSL_HEADER`; `CSRF_TRUSTED_ORIGINS` from env.
- [x] 93. Answer-leakage tests: MCQ detail hides `is_correct`; output-prediction answers never shipped; code specs kept; solutions/tests hidden.
- [x] 94. Honest-grading tests: ungradeable submissions can never return `correct`.
- [x] 95. Privacy tests: public verify response restricted to a field allow-list; revoked fails verification.
- [x] 96. Seed-integrity test: `seed_academy` is idempotent and every course ships ≥5 final items.

## Phase I — Verification & Deployment Readiness (97–100)

- [x] 97. Full backend suite green: **67 tests, 0 failures** (48 learning + 19 certificates).
- [x] 98. `manage.py check` clean; no missing migrations (`makemigrations --check`).
- [x] 99. Frontend type-check, lint and production build green.
- [x] 100. `.env.example` + this report document production configuration.

---

# Final Report

## What was delivered

**Five complete, real courses** (Python, C++, HTML/CSS/JS, Git/GitHub,
Problem Solving/DSA) stored as structured content in the `academy/` package
and seeded idempotently by `manage.py seed_academy` — 32 chapters, 45
lessons, 92 exercises, each course ending in a 5-item final assessment.
Only Python exercises execute in the real sandbox; every other course is
graded honestly through server-side answer comparison, and the course text
says so — nothing claims simulated execution.

**A verifiable certificate system** (`certificates` app): per-course
configurable policy (enable, passing score, lesson/assessment requirements),
transactional duplicate-safe issuance that re-checks everything server-side,
professional landscape-A4 PDFs with QR codes pointing at the public
`/verify/{public_id}` page, owner-restricted authenticated downloads,
admin-driven revocation and corrected re-issuance with an append-only audit
trail, and a privacy-safe public verification API + page.

**Frontend integration**: typed API client, `/certificates` hub with blob
downloads, `/verify/[publicId]` public page with valid/revoked/superseded/
not-found states, and a server-driven certificate panel on every course
dashboard including a "Claim my certificate" flow.

## Integrity guarantees (tested)

- Learners can never self-issue: 401 without auth, 412 with requirement
  breakdown when ineligible, issuance locked and idempotent.
- Quiz answers, solutions and grading tests never reach the client
  (`AnswerLeakageTest`), and output-prediction answers are withheld even as
  `expected_output`.
- Submissions that can't be auto-evaluated are recorded honestly as pending —
  never as fake passes (`HonestGradingIntegrityTest`).
- Public verification exposes only a fixed allow-list of fields.
- One active certificate per learner+course enforced **at the database level**;
  reissue supersedes instead of deleting.

## Known limitations / next steps

- Non-Python languages (C++, JS, git) are concept-graded; a multi-language
  judge (e.g. containerised compilers) is the natural next phase.
- Some marketing/catalog sections still use static frontend data (task 78).
- Certificate PDFs live on local media storage; a storage backend (S3 etc.)
  should be configured when deploying to multiple servers.
- `seed_courses` (the older seeder) is superseded by `seed_academy`; keep it
  only as historical content source until removed.

## How to run

```bash
# backend
cd backend
python manage.py migrate
python manage.py seed_academy        # idempotent — safe to re-run
python manage.py test                # 67 tests
python manage.py runserver           # API on :8000, admin at /admin/

# frontend
cd frontend
npm run dev                          # :3000, reads NEXT_PUBLIC_API_URL
```

Production checklist: set `SECRET_KEY`, `DEBUG=False`, real `ALLOWED_HOSTS`,
`SITE_URL=https://your.domain`, `ALLOWED_ORIGINS`, PostgreSQL env vars,
`USE_X_FORWARDED_PROTO=True` behind TLS termination, run `collectstatic`,
serve `/media` (or switch to object storage).
