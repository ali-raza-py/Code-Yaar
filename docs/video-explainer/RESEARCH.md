# RESEARCH — Code Yaar Product Inspection & Feature Verification

> Phase 1 deliverable of the explainer-video project. Everything in this file was
> verified against the actual repository (`c:\Users\HP\Code-Yaar`) on 2026-11-06.
> **Rule: the video may only show what is marked FULLY WORKING here.**

---

## 1. Brand facts (verified from source)

| Item | Verified value | Source |
|---|---|---|
| Name | Code Yaar (page title also appears as "Code-Yaar") | `frontend/src/app/layout.tsx`, `(public)/page.tsx` |
| Tagline | **Think. Build. Evolve.** | `layout.tsx` metadata; rendered as eyebrow text in hero — `components/marketing/learning-entry.tsx` L35 |
| Homepage H1 | **"Learn computer science by building with it."** | `learning-entry.tsx` L37–39 |
| Homepage sub-copy | "Code Yaar is an AI-native computer science education platform: structured tracks, hands-on lessons, real projects and challenges…" | `learning-entry.tsx` L40–42 |
| Landing sections | Tracks ("Find a path that leads somewhere"), Featured courses, The Code-Yaar loop ("Progress you can feel in your hands"), Leaderboard ("Where does your name sit?"), Certificates ("Certificates anyone can verify") | `learning-entry.tsx` |
| Marketing palette | Deep navy background `#0f1d32` ("DataCamp-navy family" per CSS comment), mint/forest accent tokens (`text-mint-soft`, `forest-accent`), white typography. App theme uses OKLCH tokens; light theme primary is purple-violet, dark theme flips to navy. | `frontend/src/app/globals.css` L114–128, L316–318 |
| Logo assets | `frontend/public/logo-light.png`, `logo-dark.png`, `favicon.svg`, `apple-touch-icon.png`; also `backend/branding/logo.png`, `logo-dark.png`, `logo-transparent.png` | repo inspection |

⚠️ **Brand-consistency note for the video:** the brief asks for "emerald and teal accents
on charcoal." The live marketing pages already use a **deep-navy + mint/forest-green**
system — close enough to the brief to be authentic. The video should match the *actual
site* (navy-charcoal + mint/emerald), not an invented palette.

## 2. Route map (screen-recording shot list)

Public (no login needed):

| Route | Page |
|---|---|
| `/` | Marketing landing page (hero, tracks, loop, leaderboard preview, certificates) |
| `/tracks`, `/tracks/[slug]`, `/tracks/[slug]/[classSlug]` | Learning-tracks discovery |
| `/courses`, `/courses/[slug]` | Public course catalog + course detail |
| `/courses/[slug]/lesson/[lessonSlug]` | Public lesson preview |
| `/verify`, `/verify/certificate/[id]`, `/verify/badge/[id]`, `/verify/[publicId]` | Public credential registry |
| `/about`, `/updates` | About page, platform changelog |
| `/leaderboard` | Leaderboard (discovery group) |
| `/challenges`, `/challenges/[slug]` | Coding challenges arena |
| `/profile/[username]` (+ `/portfolio`, `/projects/[slug]`) | Public learner profiles |

Authenticated app:

| Route | Page |
|---|---|
| `/dashboard` | Student dashboard |
| `/learn`, `/learn/[slug]` | Course workspace: lessons, code runner, exercises |
| `/learn/[slug]/dashboard` | Per-course progress dashboard |
| `/learn/practicals/…` | Board practicals browser (class → subject → practical) |
| `/progress` | Progress page |
| `/projects`, `/projects/[slug]` | Student project showcase |
| `/achievements` | Badges/achievements |
| `/certificates`, `/certificates/[id]` | Certificate list + preview with PDF/PNG download and LinkedIn share |
| `/profile`, `/profile/portfolio` | Own profile + portfolio editor |
| `/sign-in`, `/sign-up`, `/verify-email`, `/forgot-password`, `/reset-password` | Auth flows |

Demo content: `seed_academy.py` provisions a demo learner **demo@codeyaar.dev** (password in the same file) — use this account for all screen recordings.

## 3. Feature verification table

| # | Feature | Status | Evidence | Video-worthy? |
|---|---|---|---|---|
| 1 | Landing page / brand | ✅ FULLY WORKING | `(public)/page.tsx` → `LearningEntry` component, full marketing copy live | Yes — opening shot |
| 2 | Learning tracks & discovery | ✅ FULLY WORKING | `/tracks` pages (221 + 463 lines), `CareerTrack` model, Sindh Board track hierarchy | Yes |
| 3 | Course catalog & detail | ✅ FULLY WORKING | `/courses`, `/courses/[slug]`, `Course` model | Yes |
| 4 | Lesson learning interface | ✅ FULLY WORKING | `/learn/[slug]` workspace; `lesson-content.tsx` renders markdown with syntax-highlighted, runnable code fences | Yes — core shot |
| 5 | In-browser code execution | ✅ WORKING (Python & C++) | `components/learning/workspace/runnable-code-block.tsx` ("languages … actually executes (Python and C++)"); backend `SubprocessSandbox` (`services/sandbox.py` L197) with timeout/memory limits; API `/execute/` (`lib/api.ts` L818) | Yes — hero product moment |
| 6 | Exercises & auto-grading | ✅ FULLY WORKING | `Exercise` model: 6 types (code, MCQ, multi-select, debugging, output-prediction, fill-blank), `test_cases` + `hidden_tests`, hints, post-submit explanation; `/exercises/{id}/run/` endpoint | Yes |
| 7 | Quizzes / assessments | ⚠️ PARTIAL | **No standalone quiz/question-bank system** — stated explicitly in `analytics_views.py` L9–10 ("the quiz / question-bank system is not built yet"). Quizzes exist as *assessment-type exercises* and a graded **Final Assessment** per course (`is_final_assessment`, feeds certificate grading) | Show as "checks your understanding" via exercise UI. **Do NOT advertise a quiz engine** |
| 8 | Student dashboard | ✅ FULLY WORKING | `/dashboard` (399 lines), per-course dashboard `/learn/[slug]/dashboard`, `Enrollment`/`LessonProgress` models | Yes |
| 9 | XP, levels, streaks | ✅ FULLY WORKING | `XPTransaction` model (incl. `streak_bonus`), `streak_days`/`longest_streak` on `UserProfile`, XP events recorded server-side (`services/progress.py`) | Yes |
| 10 | Leaderboard | ✅ FULLY WORKING | `/leaderboard` page, `LeaderboardEntrySerializer`, landing-page `LeaderboardPreview` | Yes |
| 11 | Learner profiles | ✅ FULLY WORKING | `/profile`, public `/profile/[username]` with level/badges stats, privacy-honouring metadata | Yes (brief) |
| 12 | Certificates | ✅ FULLY WORKING | Dedicated `certificates` app: real PDF + PNG renderers (`pdf.py`, `png.py`), QR verification (`qrutil.py`), eligibility service with passing score + final-assessment grading, revoke/re-issue states, public registry `/verify/*`, LinkedIn share flow | Yes — strong differentiator |
| 13 | Achievements / badges | ✅ FULLY WORKING | `Achievement` model, badge registry + seed tests (`tests_badges.py`), `/achievements` page, badge verify URLs | Yes |
| 14 | Auth + email verification | ✅ FULLY WORKING | Sign-up/sign-in pages, JWT with refresh cookies (`services/auth.py`), enforced email verification workflow | Not needed on screen |
| 15 | Projects / portfolio | ✅ FULLY WORKING | `Project`, `ProjectMilestone`, `ProjectImage` models; `/projects` showcase; portfolio editor + public pages | Yes |
| 16 | Coding challenges | ✅ FULLY WORKING | `/challenges` pages, `ChallengeSubmission`, `/challenges/{slug}/run/` API, challenge workspace tokens in `globals.css` | Yes (optional) |
| 17 | Practicals (board) | ✅ WORKING | `/learn/practicals/…` route family | Optional |
| 18 | Announcements / updates | ✅ WORKING | `(discovery)/announcements`, `/updates` changelog | No |
| 19 | Competitions / hackathons | ⚠️ PARTIAL (feature-complete UI, thin live content) | Pages + registration flow exist (`hackathons/[slug]/register`, admin competition form-builder) — but real events depend on admin-created content | **Skip in video** unless a live competition exists at record time |
| 20 | **AI features (tutor/feedback)** | ❌ DOES NOT EXIST | The site copy says "AI-native", but **no LLM/AI integration exists anywhere in the backend** (searched: openai/gemini/llm/AI-feedback — zero hits in product code). Homepage metadata repeats the claim | **ABSOLUTELY DO NOT show or imply an AI tutor/chatbot in the video.** This is unverified marketing copy on the site itself — flagged to owner separately |
| 21 | Admin / course studio | ✅ EXISTS | 40+ admin pages, `studio_views.py` | Out of scope for a learner-facing film |
| 22 | Class XII course | ❌ STUB (intentional) | `curriculum/class_xii.py`: `is_published: False`, "no lessons… nothing invented" | Never show |

## 4. Real content scale (what can be recorded)

Verified seeded content — all genuine, textbook-verified or hand-authored:

- **5 Academy courses** via `seed_academy.py` (Python, C++, Web, Git, DSA), materialised
  as Track → Course → Chapter → Lesson → Exercise with final assessments:
  - DSA: 37 lessons · Git: 35 · Python Foundations: 14 · Web: 8 · C++: 6 → **~100 lessons** each carrying graded exercises (code + MCQ).
- **Board curriculum (Sindh Board, English medium)** in `learning/curriculum/`:
  - Class X units 2–5: 26 lessons · Class XI (Intro, Control Structures, I/O & Operators, Libraries & Debugging): 28 lessons → **54 board lessons**, source-verified against the board PDFs in `textbooks/` (see `CLASS-X-SOURCE-VERIFICATION.md`, `CLASS-XI-SOURCE-VERIFICATION.md`).
- Certificate pipeline is live for courses with `certification_enabled`.

**Verdict:** there is enough real, dense content to record an authentic product demo. No mockups or fake UI needed.

## 5. Honest constraints to design around

1. **No quiz engine** → frame assessments as "checks and a final assessment", which is true.
2. **No AI assistant** → the film must not show chat UI. "AI-native" stays out of the narration.
3. **Code runner supports Python & C++ today** → record Python (most reliable on the dev sandbox).
4. **Competitions/hackathons are infrastructure** → skip unless live content exists.
5. **Light theme primary is purple**, marketing is navy+mint → record the **dark theme and the landing page**, which match the intended brand look.
