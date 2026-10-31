# CODE YAAR — ALI RAZA CONTRIBUTIONS

> Audit document — generated 2026-10-31. Ali Raza is the Founder & CEO and, on the
> evidence below, the dominant developer of the platform. He worked extensively
> with AI coding assistants (Qoder transcripts from 2026-10-29 onward, plus
> `cline` checkpoint git objects from 2026-10-30). "Contribution" here means
> product direction, specification, review and pushing work into the codebase —
> not necessarily hand-typed lines of code.

## 1. Evidence Base

- **Git:** 8 of 15 unique commits are authored by "Ali Raza" (`ali-raza-py`), and
  they contain the large majority of the product's code (see §2).
- **Qoder conversations:** 15 accessible sessions (2026-10-29 → 2026-10-31), all
  driven by Ali's prompts — feature specs, bug reports with screenshots/errors,
  implementation prompts, and "continue" directives.
- **Docs:** `docs/` was created and is maintained by Ali (first commit `5f94cbf`).
- **Memory records:** the workspace's long-term memories preserve ~40 project
  decisions/conventions formed during these sessions (design tokens, email
  verification workflow, retry mechanism, port cleanup, etc.).

## 2. Chronological Account of Ali's Work

### Phase 1 — Product foundation (2026-09-13, commit `5f94cbf` "docs")
Authored the entire governing documentation set:
- `docs/PRD.md` — vision (Learn → Build → Prove), personas, goals, requirements.
- `docs/ARCHITECTURE.md` — stack decisions, PostgreSQL-now/Supabase-deferred, later extended with the full token-governed design-system spec.
- `docs/MVP-ROADMAP.md` — phased roadmap with strict status vocabulary.
- `docs/AI-CODING-RULES.md` — engineering guardrails for AI agents (no invented
  status, honest verification, minimal change) — an early, unusual level of AI
  governance for a student startup.
- `docs/CURRENT-PROGRESS.md` — evidence-based status ledger, kept updated since.

### Phase 2 — Building the actual platform, pushed in bulk (2026-09-25 → 2026-10-02, commits `c6d6634`, `d1dd1f6`, `94318a1`)
As Ali stated, large amounts of work were committed together rather than per task.
His pushes introduced, in one tree:
- The **entire Next.js frontend**: `(app)` routes — dashboard, learn catalog,
  lesson workspace, course dashboard, challenges, leaderboard, projects,
  profile, settings; `(public)` marketing landing with hero/sections, footer,
  about page; the early DataCamp-inspired `dc-*.tsx` marketing components;
  motion system (particles, parallax, magnetic buttons, reveal, 3D scene
  wrappers with three.js); CodeMirror-based code editor; xp-badge; skeletons;
  app sidebar/shell; theme hook (light/dark).
- The **core Django backend** beyond the initial scaffold: `learning` models
  (Course/Chapter/Lesson/Exercise/Enrollment/LessonProgress/ExerciseAttempt…),
  DRF `api_views.py`/`api_urls.py`, `seed_courses`, and the **Python code
  sandbox** with `language_adapter` services.
- Dozens of QA screenshots committed at the time (later cleaned up) show Ali
  personally drove browser-based verification of every page.

### Phase 3 — Reference-driven redesign & integrity program (2026-10-29 → 2026-10-30, Qoder sessions; landed via commits `c1e5dc6`, `abbace7`)
This phase is documented unusually well because the transcripts survive:
- **Session `a76c9019` (10-29):** project would not start (`npm run dev`);
  Ali diagnosed startup readiness and asked for a demo account
  (`demo@codeyaar.dev`) to be seeded — debugging and DX work.
- **Session `e6fa6520` (10-29/30):** Ali directed independent research of
  DataCamp, GeeksforGeeks, LeetCode, Programiz and HackerRank, then a
  multi-phase visual redesign ("keep the DataCamp pattern, polish per phase")
  producing the **token-governed design system** in `globals.css` (semantic
  tokens, dark-mode surface layering, difficulty/state palettes, bimodal
  radius scale, focus-visible rings, reduced-motion, `100dvh` workspace).
  Phase 5 tasks (todos 41–50): responsive polish, ARIA/focus accessibility,
  contrast verification, elimination of lint debt across legacy pages.
- **Session `task-202` (10-30):** the ~11.8k-character **"Complete Hardcoded Content
  Audit & Replacement"** prompt authored by Ali — removing fake data
  ("10K+ learners", fabricated testimonials in `data/tracks.ts`, deleted in
  `abbace7`), replacing mock functionality with real API-driven behavior, and
  a "Work Faster — Execution Protocol" for batched, honest implementation.
- **Session `70523d7e` (10-30):** execution of the **Master Academy
  implementation prompt** (attached as pasted text) — the 100-task program
  recorded in `docs/COURSE-PLATFORM-IMPLEMENTATION.md`: audit/baseline,
  configuration hardening (`SECRET_KEY` empty-value crash fix, health
  endpoint, media storage, `SITE_URL`), certificate data model, 5 complete
  courses with 32 chapters / 45 lessons / 92 exercises (`academy/*` +
  `seed_academy`), frontend certificate integration, security/integrity
  tests (answer leakage, honest grading, privacy, seed idempotency). Ali's
  follow-up "complete things that are incomplete" drove the remaining tasks.
- **Session `06b68913` (10-30):** the **Django authentication completion &
  email-verification fix**. Ali reported real production bugs — "failed to
  fetch" CORS/API unreachability, verification mail not sending — enabled
  Google 2FA/App Password, and pushed a precise fix spec ("NO FLUFF… debug,
  complete and fix the existing email verification"). Result: JWT
  access-in-memory + HttpOnly rotating refresh cookie, CSRF double-submit,
  enforced verification gate, password reset, privilege-escalation blocking,
  `AuthenticationAuditLog`, `mail_check` management command, and
  `docs/AUTHENTICATION.md` (379 lines, authored in Ali's push `abbace7`).
- **Sessions `24931dbb`, `c988cb28`, `d39d039f`, `f9a6fb98` (10-30):**
  one-command dev startup (`dev.cmd` / `scripts/dev.ps1` with health-poll,
  CORS self-check, `-Force` stale-process cleanup), the API **transport-retry
  mechanism** (`withTransportRetry`) for code-run calls during Django
  hot-restarts, and sign-in connectivity debugging.

### Phase 4 — Credentials, achievements, branding polish (2026-10-31, commits `b1c69f4`, `c99fadb`, `ab57ab2`)
- **Session `345344c1` + `fab68387` (10-30/31):** Ali authored the **"Certificate
  System: Bug Fix + Premium Visual Redesign"** and **"Premium Certificate &
  LinkedIn Achievement Sharing Redesign"** prompts — fixing "Download failed"
  and rebuilding certificates as shareable, premium artifacts. Delivered in
  `b1c69f4`: `certificates/png.py`, `qrutil.py`, `badge_art.py`,
  `badge_share_art.py`, `services/achievements.py`, the `credentials/`
  component suite (`certificate-artwork`, `certificate-preview`,
  `credential-actions`, `verify-view`), `/certificates/[id]` viewer, canonical
  `/verify/certificate/[id]` + `/verify/badge/[id]` pages, Open Graph
  link-preview images, `lib/share.ts` LinkedIn sharing, `lib/server-verify.ts`.
- **Session `fab68387` (10-31):** site-wide **typography redesign** (Fraunces /
  Figtree / JetBrains Mono in `layout.tsx`, commit `c99fadb`); LinkedIn
  preview failures diagnosed as a localhost-`SITE_URL` issue (memory +
  README guidance record the public-domain requirement); Ali supplied the
  brand logo (screenshot attachment) and directed its use everywhere →
  commit `ab57ab2` "Logo changes" (`backend/branding.py`, `branding/logo.png`,
  logo integrated into PDF/PNG/badge renderers and `frontend/public/brand/`).
- **Session `fc65df5e` / sidebar QA (10-31):** smart sidebar collapse/expand
  behavior verified with the `.tmp-nav-*.png` screenshot series.

## 3. Summary by Category

| Category | Ali Raza's verified work |
|---|---|
| Product | PRD, MVP roadmap, positioning ("Learn → Build → Prove"), anti-clone visual-identity policy, honest-data integrity rules, 100-task Academy program spec, hardcoded-content audit program |
| Frontend | All 27 routes; design system & tokens; light/dark mode; typography system; motion/3D layer; workspace UI (editor, output, exercise, lesson, sidebar); auth screens; certificate/badge UI; marketing pages; accessibility & responsive polish |
| Full-stack integration | Typed API client (`lib/api.ts`), token/CSRF/refresh plumbing, retry logic, blob downloads, form handling on auth screens, server-driven certificate panels |
| Backend (authored in his pushes) | `certificates` app (models/views/services/pdf/png/qr/admin/tests), auth system (`auth_views/serializers/urls`, `services/auth.py`, permissions, `mail_check`), `seed_academy` + 5 course content modules, achievements/XP services, sandbox integration refinements, branding renderer, settings hardening, migrations 0002–0010 |
| Testing & verification | 165 test methods in the tree he pushed; AnswerLeakage/HonestGrading/Privacy/SeedIntegrity suites; browser QA screenshot campaigns; test-run log committed (`backend_test_run.txt`) |
| DX & ops | `dev.cmd` + `scripts/dev.ps1` launcher, `.env.example` documentation, Gmail SMTP configuration, port-cleanup conventions, README rewrite, `docs/CURRENT-PROGRESS.md` upkeep |
| Documentation | Everything in `docs/` except project-level context authored with assistants |

## 4. Honest Caveats

- Pre-2026-10-29 assistant sessions (the 09-25→10-02 implementation window) are
  **not in the accessible transcript cache**; attribution for that code rests on
  git authorship of Ali's bulk pushes plus the user's own statement that he
  pushed his implemented work himself. This is LIKELY-to-VERIFIED depending on
  the item, and is marked per-feature in `FEATURE-IMPLEMENTATION-STATUS.md`.
- Ali's commits also carried restructuring work by Abdullah (his `c6d6634`
  tree was built on Abdullah's scaffold); commit boundaries do not equal
  task boundaries — the explicit reason this audit exists.
- Because AI assistants generated substantial code under Ali's direction,
  "who wrote each line" is not meaningfully attributable; what *is* attributable
  is specification, review, integration, debugging and acceptance — all
  consistently in Ali's sessions.
