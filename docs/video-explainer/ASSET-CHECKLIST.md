# ASSET CHECKLIST — Everything the Film Needs

Asset IDs match STORYBOARD.md. Folder convention: `assets/video-explainer/{01-screen,02-brand,03-audio,04-graphics}` (create outside the repo or in a scratch drive; do not commit raw video to git).

## 0. Pre-flight (do these first)

- [ ] Run the app locally (`scripts/dev.ps1` / `dev.cmd`) or use the deployed site — pick ONE environment and never mix footage between them.
- [ ] Log in as the seeded demo learner (`demo@codeyaar.dev` — password in `backend/learning/management/commands/seed_academy.py`) so every screen has realistic progress data.
- [ ] Enroll the demo account in 2–3 courses and complete enough lessons that dashboards/leaderboard/certificate screens look *lived-in* (real XP, at least one earned certificate if eligibility allows — do not fake one).
- [ ] Browser: clean profile, dark theme, zoom 100%, bookmarks bar hidden, extensions hidden, notifications silenced (Focus Assist / Do Not Disturb), OS cursor set to large.
- [ ] Resolution: 1920×1080 display (or record windowed 1920×1080 region on larger displays). Same window size for every take.

## 1. Screen recordings (OBS, 1080p, 30 or 60fps, CRF ~18)

| ID | Shot | Route | Action to perform | Target length of take |
|---|---|---|---|---|
| A4 | Tracks browse | `/tracks` → `/tracks/[slug]` → `/learn/[slug]` | Slow scroll, hover 2 cards, click one, scroll lesson list | 40s |
| A5 | Code run (hero) | `/learn/[slug]` (Python Foundations → any loop lesson) | Type exactly: `for i in range(1, 6):` / `    print(i)` in the runnable block → click Run → wait for output 1–5 | 45s, 3 takes |
| A6 | Assessment + feedback | same course, any MCQ exercise | Read, pick correct option, submit, reveal explanation | 40s |
| A7 | Challenge | `/challenges/[slug]` | Show prompt, one edit, Run/Test | 30s |
| A8 | Projects | `/projects` | Scroll grid, hover/click one project | 25s |
| A9 | Dashboard | `/dashboard` | Slow scroll over progress cards | 20s |
| A10 | Leaderboard | `/leaderboard` | Scroll 1 screen; **verify no real-user names you don't want shown; blur or use staging data** | 20s |
| A11 | Certificate | `/certificates` → `/certificates/[id]` | Open preview, click PDF download, show rendered document | 40s |
| A12 | Verification | `/verify/certificate/[id]` | Paste/land on verify result page | 15s |
| A13b| Landing beauty pass | `/` | Slow scroll of hero + leaderboard preview section (dark navy = brand plate for free) | 30s |

Recording rules: rehearse each choreography 2× before rolling; move the mouse in slow
straight lines; pause 1s before/after every action; never scroll backward; record 2–3
takes, keep the best per shot.

## 2. Brand assets

- [ ] A2 — `frontend/public/logo-light.png` (+ `logo-dark.png` for light variants); export a ≥1000px-wide transparent PNG; also SVG from `favicon.svg` if crispness needed in Fusion.
- [ ] A3 — Tagline lockup type layer (`THINK. BUILD. EVOLVE.` in the site's mono style — check `globals.css` font stack; use the same webfont or an identical metric fallback).
- [ ] A1 — Grain/vignette overlay: generate in Fusion (no download needed).
- [ ] Color chips sampled LIVE from the running site: navy background, mint accent, headline white. Save as `.drx`/still + a PNG swatch strip. (No invented hex.)
- [ ] Screenshot stills (Canva source material): hero, tracks card, lesson, exercise, dashboard, leaderboard, certificate, verify — 1920×1080 PNG each, cropped variants as needed.

## 3. Audio assets

- [ ] VO_01…VO_07 — one file per scene (TTSMaker or human), 48 kHz WAV, per VOICEOVER.md.
- [ ] MUS_bed — Pixabay "ambient minimal pulse", 90–100 BPM, WAV/high-bitrate MP3.
- [ ] SFX set (Pixabay): sub-boom ×1, soft whoosh ×2, keyboard taps ×1 clip, mouse click ×1, UI result tick ×1, subtle success chime ×1, terminal blip ×1.
- [ ] License archive folder: screenshots of each download page / license (proof of commercial rights).

## 4. Graphics / compositing plates

- [ ] Navy gradient background plate 1920×1080 (Fusion or Canva) — the film's "studio".
- [ ] Browser-chrome bar overlay (drawn: 3 dots + address pill, dark, no URL text needed) — a *frame* for footage, never a fake interface.
- [ ] Panel shadow preset + corner radius matched to site (12px at 1:1).
- [ ] Eyebrow/headline text style presets (Resolve Text+ or Canva brand kit): mono mint eyebrow, white 56px headline, tracking −2%.
- [ ] Optional: P1/P2 Fusion abstract plates (per AI-VIDEO-PROMPTS.md) or Kling clips if approved.

## 5. QC sheet before final render

- [ ] Every product frame traceable to the checklist in §1 (nothing mocked).
- [ ] No "AI" wording, no quiz-engine claims, no Class XII / competition screens.
- [ ] Passwords/emails/tokens invisible in any URL bar or toast (recording was made with hidden chrome; double-check 100% zoom).
- [ ] Real third-party names blurred on leaderboard, or staging data used.
- [ ] Total runtime ≤ 60s; audio −14 LUFS / −1 dBTP; text safe-zones respected for YouTube (5%) and Instagram (14%).
