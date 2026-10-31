# CODE YAAR — PROJECT OVERVIEW

> Audit document — generated 2026-10-31 from repository evidence, GitHub API data,
> local git history, project documentation and accessible Qoder conversation
> transcripts. This file lives in `audit/` and does not modify or replace `docs/`.

## 1. What Code Yaar Is

Code Yaar (repo name `Code-Yaar`) is an AI-native computer-science learning
platform for students and beginner-to-intermediate developers. The product
promise is **Learn → Build → Prove**, summarized by the tagline
**"Think. Build. Evolve."**

- **Founder & CEO / primary product developer:** Ali Raza (GitHub: `ali-raza-py`, commit author "Ali Raza").
- **Backend developer:** M. Abdullah Hussain (GitHub: `abdullah-dev-5`).

The live repository is **https://github.com/ali-raza-py/Code-Yaar**.
(The URL `https://github.com/aliraza110-bulb/Code-Yaar` returned HTTP 404 on the
GitHub API during this audit and appears not to exist; all GitHub findings below
refer to `ali-raza-py/Code-Yaar`.)

## 2. What the Platform Does Today (verified in code)

| Capability | Where it lives |
|---|---|
| Course catalog: 5 seeded courses (Python, C++, Web, Git/GitHub, DSA) — 32 chapters, 45 lessons, 92 exercises | `backend/learning/management/commands/academy/`, `seed_academy` |
| Interactive lesson workspace with a real Python code editor and sandboxed execution/grading | `frontend/src/components/learning/workspace/*`, `backend/learning/services/sandbox.py` |
| Full authentication: register/login/JWT, enforced email verification, password reset, profile, RBAC groups | `backend/learning/auth_*.py`, `docs/AUTHENTICATION.md`, `frontend/src/app/(auth)/*` |
| Certificate engine: eligibility rules, transactional issuance, PDF + PNG + QR, public verification, revoke/reissue, audit trail | `backend/certificates/*` |
| Achievement badges: server-rendered medallion artwork (SVG/PNG), `/achievements` grid, downloads, LinkedIn share | `backend/learning/badge_art.py`, `badge_share_art.py`, `frontend/src/app/(app)/achievements/page.tsx` |
| Public verification pages with Open Graph link-preview images | `frontend/src/app/(public)/verify/*`, `backend/certificates/png.py` |
| Gamification: XP, streaks, levels, leaderboard, challenges, projects | `backend/learning/models.py`, `frontend/src/app/(app)/*` |
| Token-governed design system with light/dark mode and a custom font pairing (Fraunces / Figtree / JetBrains Mono) | `frontend/src/app/globals.css`, `frontend/src/app/layout.tsx` |
| One-command Windows dev launcher (`dev.cmd` starts API :8000 + app :3000) | `dev.cmd`, `scripts/dev.ps1` |

## 3. Technology Stack (as observed)

| Layer | Technology | Evidence |
|---|---|---|
| Frontend | Next.js (App Router) + React + TypeScript + Tailwind CSS v4 | `frontend/package.json` |
| Editor / motion / 3D | CodeMirror 6, framer-motion, three.js (react-three) | dependencies + `components/motion`, `components/3d` |
| Backend | Django 6.x + Django REST Framework + Simple JWT | `backend/config/settings.py`, `requirements.txt` |
| Database | SQLite for local dev; PostgreSQL selectable via env; Supabase **deferred** | `backend/.env.example`, `docs/ARCHITECTURE.md` §7 |
| Code execution | Subprocess sandbox with timeouts (Python only) | `backend/learning/services/sandbox.py` |
| Certificates | reportlab (PDF), pillow (PNG), qrcode (QR) | `backend/certificates/pdf.py`, `png.py`, `qrutil.py`, `requirements.txt` |
| Email | Django 6 `MAILERS` over Gmail SMTP (STARTTLS, App Password) — credentials in gitignored `.env`, not committed | `docs/AUTHENTICATION.md` §4 |
| Testing | Django test suite: 165 `def test_` methods across `learning` (67), `learning/tests_auth` (76), `certificates` (22); docs record 164 passing | static count + `docs/CURRENT-PROGRESS.md` |

## 4. Repository Layout

- `backend/` — Django project: `config/`, `learning/` (main app), `certificates/` (credential app), management commands, migrations.
- `frontend/` — Next.js app: 27 routes under `src/app/` split into `(public)`, `(auth)`, `(app)` route groups; `src/components/` grouped by domain (auth, credentials, layout, learning, marketing, motion, 3d, ui, challenges).
- `docs/` — PRD, ARCHITECTURE, AUTHENTICATION, MVP-ROADMAP, CURRENT-PROGRESS, COURSE-PLATFORM-IMPLEMENTATION, AI-CODING-RULES.
- `scripts/` + root `dev.cmd` — unified development launcher.
- `audit/` — this investigation's reports (new; nothing else was added or modified).

## 5. Project Status in One Paragraph

The platform has grown far past the "foundation stage" described in the older
README/PRD wording: a working full-stack learning product exists with real
courses, a sandbox, complete JWT auth with email verification, a certificate
and badge system with premium artwork, and a tokenized design system. Backend
tests, `tsc`, ESLint and `next build` are reported green as of 2026-10-30.
Production readiness is **configured but not deployed** — no hosting, CI/CD or
object storage exists yet, and several roadmap features (AI mentorship,
multi-language judging, community/mentorship) remain unimplemented.

## 6. Evidence Sources Used in This Audit

1. **Qoder conversation transcripts** — 15 sessions found under the Qoder project
   cache (`conversation-history/`), spanning 2026-10-29 → 2026-10-31, all with
   user (Ali Raza) instructions extracted. Sessions before 2026-10-29 are not
   present in this cache — that limitation is stated in the timeline report.
2. **Local git history** — 15 unique commits + cline AI-assistant checkpoint objects.
3. **GitHub REST API** — commits, branches (`main`, `fix/stabilize-and-redesign`), PR #1 (only PR, authored and merged by abdullah-dev-5), zero issues, remote matched to local HEAD.
4. **Source-code inspection** — every backend module, 100+ frontend files, migrations, seeders, test suites.
5. **Project documentation** — the seven files in `docs/`, treated as claims to verify, not as proof.
