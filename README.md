# Code-Yaar

Code-Yaar is a proposed platform for helping learners learn practical software skills, build projects, and prove what they can do. The repository is currently at the foundation/setup stage; product scope and workflows remain documented proposals.

## Repository Layout

- `backend/` contains the Django project and Python dependencies.
- `frontend/` contains the TypeScript/Next.js project and npm dependencies.
- `docs/` contains product, architecture, roadmap, and engineering documentation.

The frontend and backend are intentionally independent.

## Database Decision

Current: Local PostgreSQL for development, configured through `backend/.env`.

Future: Supabase is intentionally deferred and is not an active dependency or configuration.

## Development

Run the API and the web app together (Windows PowerShell):

```powershell
.\dev.cmd              # API on :8000, app on :3000
.\dev.cmd -Setup       # first run: also install Python and npm dependencies
.\dev.cmd -BackendPort 8001 -FrontendPort 3001
```

The script applies migrations, starts Django in a separate "Code Yaar API"
window so console emails (verification and reset links) stay readable, waits
until `/api/health/` answers, then starts `next dev`. `Ctrl+C` in the original
window stops both. Because `ALLOWED_ORIGINS` and `FRONTEND_URL` are derived from
the ports actually used, `localhost` and `127.0.0.1` both work.

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

## Status

The repository has a working project foundation and existing application code, but no new product functionality is being introduced as part of this setup cleanup. See `docs/CURRENT-PROGRESS.md` and `docs/ARCHITECTURE.md` for the current record.