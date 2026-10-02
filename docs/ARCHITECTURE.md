# Code-Yaar Architecture

## 1. Architecture Overview

The repository has a separated full-stack foundation. The existing frontend is a Next.js/TypeScript application under `frontend/`; the existing backend is a Django project under `backend/`. Product architecture beyond this separation remains subject to the documented proposals and decisions below.

The product architecture is **TBD**. Any future architecture must be derived from approved product scope and documented here after implementation.

## 2. Current Technology Stack

The current project structure evidences the following stack:

| Area | Current status | Evidence |
|---|---|---|
| Language/runtime | Python, TypeScript | `backend/` and `frontend/` |
| Frontend framework | Next.js, React, TypeScript | `frontend/package.json` |
| Backend framework | Django | `backend/manage.py` |
| Database | PostgreSQL planned | Environment-based backend settings |
| Database hosting | TBD | No hosting decision is recorded |
| Build tooling | npm and Next.js | `frontend/package.json` |
| Testing | TBD | No release-level test strategy is recorded |

## 3. Repository Structure

The repository is organized as follows:

- `backend/` owns Django, Python dependencies, settings, and backend assets.
- `frontend/` owns Next.js, TypeScript, npm dependencies, and frontend assets.
- `docs/` owns product and engineering documentation.
- Root files own repository-wide instructions, ignore rules, and licensing.

The two application directories are independent and are developed with their own toolchains.

## 4. Application Flow

No request, route, user action, or application entry point exists in the repository to trace. Application flow is TBD.

## 5. Frontend Architecture

The frontend implementation exists under `frontend/`. Its product scope and production readiness remain under review.

## 6. Backend Architecture

The Django project and existing backend modules exist under `backend/`. Further API and domain decisions remain documented as proposals until approved.

## 7. Data Layer

### Database Decision

Current:
Local PostgreSQL

Future:
Supabase - deferred

The backend reads local PostgreSQL settings from `backend/.env`. Supabase is intentionally deferred and is not an active dependency, configuration, hosted database, or storage provider in the current development environment.

## 8. Authentication and Authorization

Authentication and authorization decisions are not finalized. Existing code must not be treated as production-ready security architecture.

## 9. External Integrations

No external integrations are evidenced. Providers, APIs, analytics, email, payments, AI services, and other integrations are TBD.

## 10. Deployment

Deployment configuration, hosting, CI/CD, and containerization remain TBD. Production readiness cannot be claimed.

## 11. Security Considerations

Security requirements, secret management, authentication, authorization, input validation, data protection, logging, and incident handling must be defined before implementation and release.

## 12. Architectural Decisions

The repository separation decision is recorded by the `backend/` and `frontend/` ownership boundaries. Future decisions should document context, alternatives, decision, and consequences before the relevant implementation is added.

## 13. Known Technical Debt

The primary known gaps are product scope, automated verification, production configuration, and deployment readiness. Existing application code should be treated as pre-existing work, not as a completed MVP.

## 14. Future Architecture

Future architecture is **Proposed** and must remain separate from current architecture. It may need to support:

- A learner-facing experience for the approved MVP.
- Content, practice, project, and proof-of-work domain boundaries where justified.
- Feedback and progression workflows if included in scope.
- Privacy-conscious handling of learner data.
- AI assistance only after its role, data boundaries, and evaluation are approved.

No framework, database, hosting provider, integration, or deployment pattern should be selected as fact until a product and engineering decision is made and implemented.
