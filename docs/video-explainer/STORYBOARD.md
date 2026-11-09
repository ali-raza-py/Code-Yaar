# STORYBOARD — Code Yaar Launch Film (58 seconds, 1920×1080, 30fps)

Concept: **A+ — "The Launch Film"** (see CREATIVE-DIRECTION.md).
Every product frame comes from the verified route list in RESEARCH.md.
Timeline math: 7 + 5 + 10 + 10 + 8 + 10 + 8 = **58s** (2s handles reserved inside transitions).

Global look: navy-charcoal field (`#0f1d32` sampled from site), white tight-tracked
type, mint eyebrow labels in mono uppercase, product footage inside soft-shadowed
browser panels with ≤5% drift. Music: minimal ambient-electronic, steady pulse.

---

## SCENE 1 — THE PROBLEM (0:00 – 0:07)

| Field | Spec |
|---|---|
| Visual | Black. A single browser tab glow (no readable UI, no fake UI — deliberately just an out-of-focus rectangle of bluish light + slow scroll-blur). Alternative (zero-AI): animated dark gradient with film grain and a slow vignette pulse. |
| On-screen text | 0:01 `Watching tutorials feels like learning.` 0:04 `Until you have to build.` (white, 56px, center, word-groups fade in sequentially) |
| Voiceover | "Most people learn to code by watching. And watching *feels* like learning — until it's time to build something." |
| Assets | A1 grain-overlay (Fusion-generated) **or** optional Kling cinematic shot (prompt P1 in AI-VIDEO-PROMPTS.md) |
| Animation | Text: opacity 0→100, y +12px→0, ease-out 0.5s, hold, fade. Grain drifts 3% right. |
| Editing | Start on pure black 0.5s before anything. Nothing else moves — restraint is the hook. |
| Transition out | 12-frame dip to black, then the logo beat lands. |
| Sound | Low room tone; a faint, tired mouse-click at 0:03 (once). Music enters AFTER the dip, with the logo. |

## SCENE 2 — BRAND REVEAL (0:07 – 0:12)

| Field | Spec |
|---|---|
| Visual | Logo reveal on navy. `frontend/public/logo-light.png` mark scales 96→100%, matte-revealed left→right; wordmark "Code Yaar" fades up beneath; eyebrow line types in mono: `THINK. BUILD. EVOLVE.` (this exact style exists on the live hero). |
| On-screen text | `Code Yaar` + `THINK. BUILD. EVOLVE.` |
| Voiceover | "This is Code Yaar." |
| Assets | A2 logo PNG (transparent), A3 eyebrow text layer |
| Animation | Logo mask wipe 0.6s ease-in-out; tagline: mono letters 30ms stagger; 1px mint underline draws left→right under the logo. |
| Editing | Hold the full lockup ≥1.5s before cutting — let the brand register. |
| Transition out | Hard cut to product (energy shift). |
| Sound | Sub-boom + soft shimmer on reveal; keyboard-tick x3 on tagline stagger; music drops into a steady pulse. |

## SCENE 3 — LEARN (0:12 – 0:22)

| Field | Spec |
|---|---|
| Visual | Real product, live-recorded: `/tracks` scrolls showing track cards → click a track → course page `/learn/[slug]` with chapters/lessons list. Two panels max on screen; incoming panel slides 40px left over the outgoing one. |
| On-screen text | Eyebrow `01 · LEARN` (mint, mono). Headline: `Structured tracks. Real computer science.` (do NOT put "AI" anywhere) |
| Voiceover | "Structured tracks take you from your very first program to full computer science — school-board curriculum and career paths, laid out step by step." |
| Assets | A4 screen recording: tracks scroll + course open (OBS, choreographed cursor) |
| Animation | Browser panel enters with 4% scale overshoot-free settle (0.5s); scroll happens *inside* the recording, not as an effect; cursor highlighted with a subtle 20%-white halo circle. |
| Editing | Trim dead mouse travel ruthlessly — constant gentle motion inside the panel. |
| Transition out | Panel slide: Learn panel exits right as Practice panel enters left, 8-frame overlap. |
| Sound | Two soft "page whoosh" layers under the panel swap; UI click synced exactly to the recorded click frame. |

## SCENE 4 — PRACTICE (0:22 – 0:32) — the credibility peak

| Field | Spec |
|---|---|
| Visual | The hero moment, all real: inside a lesson at `/learn/[slug]`, a Python code block gets 2 lines typed → **Run** clicked → real console output appears (sandbox executes Python/C++ — verified). Cut to a multiple-choice assessment item; correct option is picked; the post-submit explanation appears. |
| On-screen text | Eyebrow `02 · PRACTICE`. Headline: `Write real code. Get answers that explain themselves.` |
| Voiceover | "But you never just read here. You write code and run it right in the browser — and every question you answer comes back with feedback that actually explains it." |
| Assets | A5 recording: typing + Run + output (Python, short program like a loop printing 1–5); A6 recording: MCQ exercise + explanation reveal |
| Animation | Zoom into the code editor to ~140% when typing starts (smooth 0.6s push), zoom out on output appearance. Blink caret is real, from the recording. |
| Editing | The run→output beat must land on a music hit. If typed recording looks messy, re-record with the exact 6-line script in ASSET-CHECKLIST.md (keeps takes consistent). |
| Transition out | Cut on the output line — instant, confident. |
| Sound | Mechanical-keyboard taps (low, tasteful), mouse click on Run, a small "result" tick when output renders; subtle positive chime (NOT cartoonish) on correct answer. |

## SCENE 5 — BUILD (0:32 – 0:40)

| Field | Spec |
|---|---|
| Visual | Quick real-UI pair: a challenge at `/challenges/[slug]` (problem + code workspace), then `/projects` showing project cards — one card hover to show milestones. (Both verified working. If a challenge looks empty at record time, cover the beat with `/learn/practicals` instead.) |
| On-screen text | Eyebrow `03 · BUILD`. Headline: `Skills that end up as things you've made.` |
| Voiceover | "Skills turn into proof — challenges you've solved, projects you can actually show." |
| Assets | A7 recording: challenge workspace; A8 recording: projects grid |
| Animation | Same panel language; grid gets a 3% parallax push on entry; card hover from live recording (no fake cursor effect). |
| Editing | Fastest scene — two shots, no third. |
| Transition out | Slide-over, same as Scene 3→4. |
| Sound | Whoosh + pulse continues; terminal-style "solved" blip on challenge shot. |

## SCENE 6 — TRACK PROGRESS (0:40 – 0:50)

| Field | Spec |
|---|---|
| Visual | Three real beats, one panel each, ~3s each: (a) `/dashboard` with course progress; (b) `/leaderboard` with XP + streak columns, gentle scroll; (c) **certificate** `/certificates/[id]` preview → PDF/PNG render moment, then quick flash of the public `/verify/certificate/[id]` page (the "anyone can verify" differentiator — fully working, QR + registry). |
| On-screen text | Eyebrow `04 · EVOLVE`. Headline: `XP, streaks, leaderboards — and credentials anyone can verify.` |
| Voiceover | "Every lesson, every run earns XP — streaks, levels, a live leaderboard. And when you finish, a certificate anyone can actually verify." |
| Assets | A9 dashboard recording; A10 leaderboard recording; A11 certificate page + PDF download recording; A12 verify-page screenshot |
| Animation | Certificate: panel scales 92→100% with shadow bloom (the "money shot" — hold 3s); mint underline draws beneath "verify" as the verify page appears. |
| Editing | Do NOT animate fake XP counters — the real dashboard numbers from the demo account are enough. Never show PII of real users on leaderboard (use demo/fictional-name accounts or blur). |
| Transition out | 16-frame cross-dissolve to black-navy (the one permitted dissolve). |
| Sound | Music strips back after certificate beat — space for the close. Soft paper/registry "stamp" texture under the certificate (subtle). |

## SCENE 7 — CLOSE (0:50 – 0:58)

| Field | Spec |
|---|---|
| Visual | Navy field. Logo lockup returns, larger. Tagline resolves as three words, one beat each: `Think.` `Build.` `Evolve.` Then URL line fades in: `codeyaar.dev` (the domain used across app emails/tests; confirm final production domain before render). |
| On-screen text | `Code Yaar` / `Think. Build. Evolve.` / URL |
| Voiceover | "Code Yaar. Think. Build. Evolve." (three ~0.8s gaps matching the word beats) |
| Assets | A2 logo (reused), A13 end-card type composition (Canva or Fusion) |
| Animation | Each word: 10px rise + fade, 0.4s, 0.8s apart; final hold 2.0s static — end on stillness, not motion. |
| Editing | No logo spins, no strobes. Confidence = holding the frame. |
| Transition out | Fade to black over 20 frames. |
| Sound | One final low boom under "Evolve."; reverb tail decays into silence; no sudden music cut. |

---

## Consistency rules for the edit

- One easing signature everywhere: cubic ease-out 0.4–0.6s entrances; nothing elastic.
- Cursor: large OS cursor + white halo, movements recorded slow and straight; re-record
  any wobbly take. Never speed-ramp a cursor.
- All product footage recorded at 1920×1080 browser (100% zoom unless a zoom-push says
  otherwise), dark theme, same demo account, same browser chrome hidden
  (F11/fullscreen-window mode with a rebuilt chrome bar in-panel for cleanliness).
- Text never overlaps live UI text: headlines live in the navy margin around panels.
- 58s total must not exceed 60s after audio latency; conform the mix to −14 LUFS
  (see VOICEOVER.md).
