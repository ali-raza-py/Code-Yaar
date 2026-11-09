# Code-Yaar

Code-Yaar is a full-stack learning platform for practical computer-science
skills, built around the Sindh Board school curriculum (Classes 9 and 11) and
career tracks. Learners take structured courses with lessons, exercises, and
code exercises graded in a server-side sandbox, earn XP, streaks, and
achievement badges, climb the leaderboard, and finish courses with verifiable
PDF/PNG certificates carrying QR codes and public verification pages.

## Repository Layout

- `backend/` — Django 6 project: REST API (DRF + JWT auth), the `learning`
  and `certificates` apps, course content seeding, sandbox grading,
  certificate generation, and email delivery.
- `frontend/` — Next.js 16 (App Router) + TypeScript + Tailwind CSS 4 web app:
  courses, lessons, practical workspaces, dashboards, achievements, profiles,
  certificates, and public verification pages.
- `docs/` — product, architecture, roadmap, and engineering documentation.
- `textbooks/` — Sindh Board CS textbook sources used to verify curriculum content.
- `tools/` — Python helper scripts (PDF extraction/rendering, QA and patch utilities).
- `scripts/dev.ps1` — the one-command dev launcher behind `dev.cmd`.

The frontend and backend are intentionally independent.

## Tech Stack

| Layer | Technology |
|---|---|
| API | Django 6.1, Django REST Framework, SimpleJWT, django-cors-headers |
| Database | SQLite (default for local dev) or PostgreSQL, chosen via `backend/.env` |
| Certificates | ReportLab (PDF), Pillow (PNG), qrcode (QR verification) |
| Web app | Next.js 16, React 19, TypeScript, Tailwind CSS 4, CodeMirror editor |
| Auth | JWT access + rotating refresh tokens, email verification, password reset, RBAC |

## Database Decision

Current: SQLite is the default for local development; PostgreSQL is used when
configured through `backend/.env` (`DB_ENGINE=postgres` with `DB_NAME`, etc.).

Future: Supabase is intentionally deferred and is not an active dependency or
configuration.

## Development

Create a Python virtual environment at the repository root (`.venv/`), then
run the API and the web app together (Windows PowerShell):

```powershell
.\dev.cmd              # API on :8000, app on :3000
.\dev.cmd -Setup       # first run: also install Python and npm dependencies
.\dev.cmd -BackendPort 8001 -FrontendPort 3001
```

The script applies migrations, starts Django
in a separate "Code Yaar API" window so console emails (verification and reset
links) stay readable, waits until `/api/health/` answers, then starts
`next dev`. `Ctrl+C` in the original window stops both. Because
`ALLOWED_ORIGINS` and `FRONTEND_URL` are derived from the ports actually used,
`localhost` and `127.0.0.1` both work.

To run the servers separately:

Backend:

```bash
cd backend
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm run dev
```

Copy the relevant `.env.example` to a local environment file and provide values only there. Do not commit secrets.

If the app reports `Failed to fetch`, the browser could not reach the API: start
it with `.\dev.cmd`, and confirm `ALLOWED_ORIGINS` in `backend/.env` lists the
exact origin in the address bar (`localhost` and `127.0.0.1` are different
origins). See `docs/AUTHENTICATION.md` for the full setup.

Course content is seeded idempotently from the backend:

```bash
cd backend
python manage.py seed_academy   # also: seed_badges
```

## Testing & Verification

```bash
# Backend — 251+ tests across learning + certificates
cd backend
python manage.py test certificates learning

# Frontend — type check, lint, production build
cd frontend
npx tsc --noEmit
npm run lint
npm run build
```

## Status

The platform is functional end to end: five complete courses (Python, C++,
Web, Git, DSA) with chapters, lessons, and exercises; admin-managed practical
content; progress analytics; a badge registry; in-app notifications; profile
management; and the certificate engine with public verification. See
`docs/CURRENT-PROGRESS.md` and `docs/ARCHITECTURE.md` for the current record,
and `docs/MVP-ROADMAP.md` for what remains.
