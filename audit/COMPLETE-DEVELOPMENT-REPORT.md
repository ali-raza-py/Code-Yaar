# CODE YAAR — DEVELOPMENT HISTORY & TEAM CONTRIBUTION REPORT

*Audit compiled 2026-10-31. Companion documents in this folder carry the full
detail; this report is the executive synthesis. Sources: the live GitHub
repository (`ali-raza-py/Code-Yaar`), local git history, direct source
inspection, project documentation, and 15 accessible Qoder AI-assistant
conversation transcripts (2026-10-29 → 2026-10-31).*

---

## A. Project Overview

Code Yaar ("Think. Build. Evolve.") is an AI-native computer-science learning
platform for students and beginner-to-intermediate developers, built around the
**Learn → Build → Prove** loop founded in Ali Raza's PRD. Today it is a working
full-stack product: Next.js 16 / TypeScript / Tailwind v4 frontend, Django 6.1 /
DRF / SimpleJWT backend, a real Python code sandbox, five seeded university-style
courses, complete JWT authentication with enforced email verification, and a
verifiable certificate + achievement-badge system designed for LinkedIn sharing.
It is **not yet deployed**; production settings are configured but hosting, CI/CD
and the platform's headline AI-mentorship feature remain future work.
(Full detail: `CODE-YAAR-PROJECT-OVERVIEW.md`, `TECHNICAL-ARCHITECTURE-AUDIT.md`.)

## B. Ali Raza — Founder & CEO / Primary Product Developer

Ali is, on every available measure, the builder of this product. His work
partitions into five domains:

1. **Product leadership.** Authored the founding documents on day zero
   (PRD, ARCHITECTURE, MVP-ROADMAP, AI-CODING-RULES, CURRENT-PROGRESS) and kept
   them evidence-based ever since. Wrote the four large engineering programs
   that shaped the codebase: the Hardcoded-Content Audit (killed all fabricated
   data), the 100-task Master Academy program (5 courses, 32 chapters, 45
   lessons, 92 exercises + certificate engine), the Django auth/email-verification
   fix spec, and the Premium Certificate & LinkedIn Sharing redesign. Set the
   anti-clone visual-identity policy after commissioning independent research of
   DataCamp/GeeksforGeeks/LeetCode/Programiz/HackerRank.
2. **Frontend.** Every one of the 27 routes exists in a tree he pushed. Owns
   the token-governed design system (light/dark semantics, difficulty/state
   palettes, focus rings, reduced motion), the Fraunces/Figtree/JetBrains-Mono
   typography system, the lesson workspace (CodeMirror editor, output panel,
   runnable blocks), all auth screens, certificate/badge/verify UIs, marketing
   pages and the 3D/motion layer.
3. **Backend & full-stack integration.** The auth subsystem (JWT in-memory +
   rotating HttpOnly refresh cookie, CSRF scheme, verification gate, RBAC,
   audit log, `mail_check`), the entire `certificates` app (transactional
   issuance, PDF/PNG/QR rendering, revoke/reissue, public verification),
   achievement/badge artwork renderers, `seed_academy` content, branding
   pipeline, settings hardening, and the typed API client with retry
   resilience — all entered via his commits and are traceable to his sessions.
4. **Debugging & QA.** Transcripts show him reproducing and specifying fixes
   for: npm/dev-server startup, "Failed to fetch" CORS, empty-`SECRET_KEY`
   crash, verification emails not sending (Google 2FA/App Password), sandbox
   calls failing during hot restarts, certificate "Download failed", LinkedIn
   previews broken on localhost, badge/certificate artwork clipping, sidebar
   collapse behavior — each closed with tests or screenshot evidence.
5. **DX & operations.** Built the one-command `dev.cmd`/`scripts/dev.ps1`
   launcher with health-polling and CORS self-checks, established stale-process
   cleanup conventions, documented SMTP diagnostics and the deployment checklist.

## C. Abdullah — Backend Developer

M. Abdullah Hussain (`abdullah-dev-5`) made two genuine, date-confirmed
contributions and little else that evidence can support:

- **VERIFIED:** the initial Django project scaffold (2026-09-13, `476e21c`) —
  settings, URLs, WSGI/ASGI, `manage.py`, the empty `learning` app and its
  server-rendered starter templates. The repository's oldest code.
- **VERIFIED:** the repository-structuring program (2026-10-02, `003fa6f`,
  PR #1) — the `backend/`+`frontend/` split still in use, `.gitignore` rules,
  `LICENSE`, README rewrite, `.env.example` scaffolding, and the project's only
  PR workflow.
- **LIKELY:** minor early sidebar/layout/`globals.css` tweaks inside `003fa6f`.
- **NOT SUPPORTED:** his "enhanced UI" commit claim — those files were already
  in Ali's 2026-09-25 push; his two navbar-fix commits are no-op diffs touching
  only generated artifacts. No auth, certificate, sandbox, content or
  migration work appears in any commit he authored, and no in-code attribution
  to him exists anywhere in the live tree. No transcripts or documents from
  Abdullah were accessible, so unpushed local work can be neither confirmed nor
  excluded.
(Full detail and methodology: `ABDULLAH-CONTRIBUTIONS.md`.)

## D. Feature-by-Feature Breakdown

See `FEATURE-IMPLEMENTATION-STATUS.md` — 38 tracked items across product,
backend, frontend, integration/DX and not-implemented categories, each with
files, developer, evidence source and VERIFIED / LIKELY / UNCONFIRMED /
NOT-IMPLEMENTED confidence.

## E. Technical Architecture

Two independent services: Next.js App Router frontend consuming a JSON API;
Django + DRF backend with 30 model classes across `learning` + `certificates`,
subprocess Python sandbox, reportlab/pillow/qrcode credential rendering,
Django-6 `MAILERS` over Gmail SMTP, SQLite-dev/PostgreSQL-env database, and a
tokenized Tailwind v4 design system. Security posture is unusually disciplined
for a student startup: rotating refresh tokens, hashed single-use email tokens,
privilege-escalation auditing, answer-leakage and honest-grading test suites,
DB-enforced certificate uniqueness. Full diagram and risk list:
`TECHNICAL-ARCHITECTURE-AUDIT.md`.

## F. Development Timeline

- **2026-09-10/13** — Ali writes the founding docs; Abdullah scaffolds Django.
- **09-13 → 09-25** — "hidden sprint": whole frontend + learning backend appear in Ali's bulk push `c6d6634` (with ~30 QA screenshots).
- **10-02** — Abdullah merges/restructures into `backend/`+`frontend/`, PR #1 (the only PR); Ali lands auth/UI fixes.
- **10-02 → 10-29** — second undocumented work window (transcripts unavailable).
- **10-29 → 10-31** — fully evidenced: startup fixes, reference research, design-token phases, hardcoded-content audit, 100-task Academy build, auth/email-verification completion, dev launcher, certificate/badge premium system, performance & typography programs, brand-logo integration — 5 pushes, ending with `main` synced to GitHub on 10-31.
(Full narrative: `DEVELOPMENT-TIMELINE.md`.)

## G. Remaining Work

**Product:** AI mentorship (the "AI-native" promise — zero code exists today),
real Build→Prove project submission workflow, community/mentorship decisions,
monetization.
**Engineering:** multi-language judging (C++/JS/git sandboxes), deployment
(hosting, CI/CD, `check --deploy` review), object storage for certificates,
public `SITE_URL` (LinkedIn/QR previews fail on localhost), Lighthouse 90+
verification, removal of unreferenced legacy components (`dc-*` survivors,
`particle-logo`, unused 3D), the `urls.W005` warning, DB migration from SQLite
demo data, contact page, and re-running the test suite in CI.
(Tech debt detail: `TECHNICAL-ARCHITECTURE-AUDIT.md` §6.)

## H. Final Contribution Summary

**Ali Raza** — Founder, product owner, de-facto full-stack lead and designer.
He conceived the product, wrote every governing document, and brought
essentially the entire working platform (frontend, auth, certificates,
badges, content pipeline, sandbox integration, DX tooling) into the repository
across 8 bulk pushes, directing AI coding assistants with detailed written
engineering programs and personally driving debugging and QA. His authorship of
the 2026-09-25 → 10-02 code is *established by git evidence of what appeared in
his pushes*, though the exact assistant sessions from that period are not
accessible; a slice of earliest frontend experimentation (3D/motion era) is
best classified UNCONFIRMED at line level.

**M. Abdullah Hussain** — Backend developer whose *verifiable* contribution is
the Django project bootstrap and the repository/architecture-of-folders work
plus the PR workflow. The platform's substantive backend systems (models/API,
auth, certificates, sandbox, content) cannot be attributed to him on any
available evidence. Any further claim either way would be invention.

**Method note:** all attributions above derive from converging evidence
(commit contents vs. transcripts vs. source vs. docs), not commit counts,
commit-message text (one message was directly disproven), or percentages.
Nothing in `docs/`, source, or GitHub was modified by this audit; it added
only this `audit/` folder.
