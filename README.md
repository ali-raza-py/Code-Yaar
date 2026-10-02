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

Backend:

```bash
cd backend
python -m venv venv
# Activate venv, then:
pip install -r requirements.txt
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Copy the relevant `.env.example` to a local environment file and provide values only there. Do not commit secrets.

## Status

The repository has a working project foundation and existing application code, but no new product functionality is being introduced as part of this setup cleanup. See `docs/CURRENT-PROGRESS.md` and `docs/ARCHITECTURE.md` for the current record.