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

## 15. Design System and Visual Governance

The frontend implements a token-governed design system. Component code references semantic tokens exclusively; raw hex values and Tailwind palette classes (`gray-*`, `rose-*`, etc.) are not permitted in live components or pages.

### Token Architecture (`frontend/src/app/globals.css`)

- **Raw tokens** are declared once in `:root` (brand palettes, editor syntax colors, sidebar shell, forest marketing palette) and flipped for dark mode in `.dark`.
- **Semantic aliases** are exposed to Tailwind v4 through the `@theme inline` block, generating governed utilities: `bg-card`, `text-cta`, `border-danger/30`, `bg-difficulty-easy-soft`, `text-tone-amber-fg`, and so on. One token name drives text/background/border usages of the same concept.
- **Surface semantics**: `--surface-base`, `--surface-elevated`, `--surface-interactive`, `--surface-recessed` + translucent-white dark-mode layering (LeetCode pattern) so components never hardcode a surface color.
- **Bimodal radius scale**: `--radius-tool` (2px, editor/IDE chrome), `--radius-card` (12px, cards/panels), `--radius-pill` — exposed as `rounded-tool`, `rounded-card`, `rounded-pill`.
- **State semantics**: `--state-success/warning/danger/info` plus `--difficulty-easy/medium/hard`, unified so `--challenge-*` aliases flow from core tokens and dark mode needs no per-feature overrides.
- **Editor theme**: CodeMirror 6 token colors map to `--syn-*` and `--editor-*` CSS variables; the editor chrome, gutter, active line, and selection are theme-driven.

### Guarded Interaction Utilities

- All custom CSS `:hover` rules are wrapped in `@media (hover: hover)`; Tailwind `hover:` variants are media-gated by v4 itself. No stuck transforms on touch devices.
- A global zero-specificity `:where(…):focus-visible` outline fallback guarantees a visible keyboard ring on every interactive element; the `.focus-ring` utility and `focus-visible:ring-*` variants override it where a styled ring is desired.
- `@media (prefers-reduced-motion: reduce)` disables CSS animations/transitions; a root-level `MotionProvider` (`framer-motion` `MotionConfig reducedMotion="user"`) covers JS-driven animations.
- `.workspace-full-height` uses `100dvh` for mobile-chrome-safe layout.

### Reference-Inspired Patterns (not copies)

Visual direction was researched from DataCamp (navy + green CTA identity, gamification: XP badges, streaks, progress rings), GeeksforGeeks (hairline-border zero-shadow content cards), LeetCode (dark-mode translucent layering, dense breakpoint-aware layouts, difficulty color semantics), Programiz (collapsible course sidebar drawer, in-lesson runnable code blocks), and HackerRank (workspace toolbar conventions). All implementations are original Code Yaar code using the token system above; no proprietary assets, branding, text, or source were copied.

### Assumptions and Documented Exceptions

- **DataCamp was Cloudflare-blocked** during research; its patterns were inferred from publicly indexed screenshots and the other four inspected sites. The navy + green-CTA palette was retained per explicit product direction and polished into governed tokens.
- **Tap targets**: primary mobile actions use ≥44px (`min-h-11`); compact secondary controls (segmented tabs, inline chips) use ≥36px, which meets WCAG 2.5.8 (24px minimum) while preserving density.
- **Dead marketing code**: `components/marketing/dc-*.tsx` (except `learning-entry.tsx`), `particle-logo.tsx`, and `components/3d/*` are currently unreferenced by any route. They retain legacy raw hex and are excluded from governance until either wired into a page (then tokenized) or removed.
- **Mock data**: the workspace lesson/exercise flow now calls live API endpoints; no endpoint shapes were changed by the redesign (backward compatibility constraint honored).
- **Pre-existing lint debt**: fully resolved at the end of Phase 5 — `npm run lint` reports zero errors and zero warnings. Legacy pages (`profile`, `settings`, the course dashboard, the public course landing, and the projects list/detail) were additionally tokenized during the final QA pass, so every live route now consumes the governed semantic tokens and is dark-surface safe. The async-data pattern adopted for `react-hooks/set-state-in-effect` compliance: state-first `useCallback` loaders invoked from effects through a deferred `await`, with cancellation flags for competing loads.
