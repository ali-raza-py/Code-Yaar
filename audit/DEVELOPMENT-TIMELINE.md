# CODE YAAR — DEVELOPMENT TIMELINE

> Audit document — reconstructed 2026-10-31 from three synchronized sources:
> git commit dates (author + push date), GitHub API records, and the accessible
> Qoder conversation cache. Evidence gaps are stated explicitly, not smoothed over.

## Accessible-evidence disclaimer

The Qoder transcript cache for this workspace contains **15 sessions from
2026-10-29 to 2026-10-31 only**. Work evidenced in git during 2026-09-13 →
2026-10-02 clearly happened, but the assistant sessions that produced it are
**not accessible on this machine** (different tool per `cline` checkpoint
objects, cache rotation, or another machine). Attributions for that window rest
on git authorship of bulk pushes plus the founder's own statement about pushing
implemented work in batches.

## Timeline

### 2026-09-10 — Product documents drafted (PRD "Last updated" header)
Ali Raza prepares PRD / architecture / roadmap / AI-coding-rules material.

### 2026-09-13 — Repository birth
- `5f94cbf` **Ali Raza — "docs"**: first commit; the entire `docs/` governance set (PRD, ARCHITECTURE, MVP-ROADMAP, CURRENT-PROGRESS, AI-CODING-RULES).
- `476e21c` **M. Abdullah — "Initialize Code Yaar learning app"**: first runnable code — Django scaffold (`config/` project, empty `learning` app, server-rendered home templates).

### 2026-09-13 → 2026-09-25 — The hidden build sprint (no transcript)
Between two commits, an entire platform appears in Ali's push: Next.js app with
14 routes (dashboard, learn workspace with CodeMirror editor, challenges,
leaderboard, projects, profile, settings, auth screens, marketing landing with
3D/motion components, light/dark theme), plus a Django learning domain
(Course/Chapter/Lesson/Exercise models, DRF API, seed_courses, Python sandbox
with language adapter). This is the classic bulk-push pattern Ali described.

### 2026-09-25 — `c6d6634` **Ali Raza — "update frontend"**
The above lands, alongside ~30 QA screenshots (hero/catalog/dashboard/learn/
projects/challenges/leaderboard/profile/settings) documenting per-page browser
verification — evidence of a hands-on product-owner QA loop.

### 2026-10-02 — Parallel development & merge day
- `d1dd1f6` + `94318a1` **Ali Raza — "fixed authentication and ui", "updation"**: landing page, learning entry, footer, learn page tweaks.
- `8c92456` **Abdullah — "iNIIT"**: `.gitignore` hardening (own branch).
- `498174a` **Abdullah** merges Ali's line into his branch.
- `003fa6f` **Abdullah — "Cleaner folder structure and enhanced UI"**: the
  `backend/` + `frontend/` split via renames, LICENSE, README rewrite, env
  examples, initial migration placement (+ small sidebar/layout/CSS tweaks).
- `786f8e0`, `fb56a3c` **Abdullah** navbar-fix commits on
  `fix/stabilize-and-redesign` — verified no-op diffs (generated files only).
- `f92485c` **PR #1 merged** by Abdullah — the repo's only pull request.

### 2026-10-02 → 2026-10-29 — Second hidden work window (no transcript)
By 10-29 the project already contains the auth screens and workspace referenced
in that week's sessions; exact session records are unavailable.

### 2026-10-29 — Qoder transcripts begin (all sessions initiated by Ali Raza)
- `a76c9019`: startup failure debugging ("npm run dev not working"); demo
  account decision (`demo@codeyaar.dev`).
- `699d475c`: continued startup-readiness fixes.
- `e6fa6520` (spans 10-29→10-30): **reference-site research program**
  (DataCamp — Cloudflare-blocked, inferred — GeeksforGeeks, LeetCode, Programiz,
  HackerRank) and the multi-phase design-token redesign; directive: keep the
  DataCamp-style identity, "polish according to phase".

### 2026-10-30 — The integrity & platform day
- `task-202`: **Hardcoded Content Audit & Replacement** (~11.8k-char program
  authored by Ali) + "Work Faster" execution protocol — fake stats, mock data
  and placeholder content removed in favor of live APIs.
- `e6fa6520` closes **Phase 5** (todos 41–50): responsive/accessibility/contrast
  pass, lint debt zeroed.
- `70523d7e`: **Master Academy 100-task program** executed (backend audit,
  config hardening, certificate data model, 5 courses / 32 chapters / 45
  lessons / 92 exercises, frontend cert integration, security tests) →
  commit `c1e5dc6` "Fix th ui and authentication and added courses" (03:39).
- `06b68913`, `f9a6fb98`, `944dde92`, `c988cb28`, `d39d039f`, `24931dbb`:
  **Django authentication completion**, "failed to fetch" CORS diagnosis,
  **email-verification fix** (Gmail 2FA/App Password, `mail_check`, honest
  delivery flags), one-command `dev.cmd` launcher, sandbox-call retry logic.
  → commit `abbace7` "Fixed Backend implemen django authentication and added
  courses" (15:09). `cline` checkpoint objects (stashes) from this day prove
  AI-assisted iteration between the two pushes.
- `345344c1` starts: **Certificate bug fix + premium redesign** program.

### 2026-10-31 (overnight → morning) — Credentials, badges, brand
- `fab68387`, `87b4158f`, `fc65df5e`, `98d5a54d`: premium certificate &
  LinkedIn achievement-sharing implementation (PNG/QR renderers, badge medallion
  art, verify pages, OG images, share links, `credentials/` components);
  **Lighthouse performance program** (66 → target 90+); **site-wide typography
  redesign** (Fraunces/Figtree/JetBrains Mono); LinkedIn preview failures
  diagnosed as localhost-`SITE_URL`; sidebar smart-collapse QA (`fc65df5e` +
  `.tmp-nav-*.png` series).
- `b1c69f4` "Changes" (01:49), `c99fadb` "Fixed Achievements, courses and
  typography" (01:58), `ab57ab2` "Logo changes" (02:37) — all Ali; pushed to
  GitHub the same morning; local `main` == `origin/main`, clean tree.

## Velocity observations

- Two "hidden" multi-day implementation windows (09-13→09-25, 10-02→10-29) are
  real work periods with commit-level but not session-level evidence.
- 2026-10-30→10-31 was the densest 48 hours: auth system, academy content,
  certificates, badges, DX tooling and branding all shipped in 3 pushes.
- All 15 accessible sessions share one user (Ali) and a consistent method:
  precise written programs → autonomous execution → verification → honest docs.
