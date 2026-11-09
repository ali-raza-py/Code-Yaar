# CREATIVE DIRECTION — Three Concepts, One Selection

Objective: a film that could represent Code Yaar as an ambitious, credible ed-tech
startup — a genuine product launch, not a slideshow or generic AI ad.

---

## CONCEPT A — "The Launch Film" (Premium SaaS product launch)

**Story idea.** Pure product confidence. No skits, no characters. Opens on darkness,
one line of type, then the real interface arrives — choreographed like a Linear/Stripe
launch reel. The UI itself is the protagonist; motion graphics only frame it.

- **Visual identity:** near-black charcoal field, white Inter-class type, mint/emerald
  accent used only on interactive highlights. Real product footage in soft-shadowed
  floating browser panels, parallax layering, 5–8% scale drifts.
- **Scene structure:** Problem title card → logo reveal → UI panel sequence
  (learn → practice → build → track) → tagline close. 7 beats / 58s.
- **Typography:** one family. Huge, tight-tracked headlines (site H1 style:
  `tracking-[-0.04em]`), small mono eyebrows in uppercase (`THINK. BUILD. EVOLVE.`
  is literally the site's eyebrow style — reuse it).
- **Transitions:** cut + slide-over-panel only. One cross-dissolve into the end card.
- **Motion:** easing-forward entrances, 0.4–0.6s; nothing bounces.
- **Sound:** minimal electronic pulse bed, dry UI clicks synced to actions, one sub-boom
  at logo reveal.
- **Pros:** maximally credible; cheapest to produce (almost no AI footage needed);
  ages well; highlights the real, working product — matches the honesty rule perfectly.
- **Cons:** less "emotional"; needs genuinely smooth screen recordings to carry it.

## CONCEPT B — "Signal from the Dark" (Cinematic brand film)

**Story idea.** A student's desk at 2 a.m., laptop glow, endless tutorial autoplay —
tension built with cinematic AI-generated imagery. Code Yaar appears as a calm
turning point; the film then loosens into the product.

- **Visual identity:** teal-orange-night cinematic grade, anamorphic flares, shallow
  focus, slow dolly moves (Kling AI shots), intercut with UI.
- **Scene structure:** 3 atmospheric AI shots (problem) → logo → 3 product scenes →
  aspirational AI closing shot → tagline.
- **Typography:** wide-tracked caps over film grain; fewer words, longer holds.
- **Transitions:** dissolves, light-leak wipes.
- **Sound:** ambient swell, heartbeat design, reverb-heavy.
- **Pros:** emotional, "expensive-looking" when AI footage is good; strong on social.
- **Cons:** **depends on free-tier AI video = watermarked 720p clips** mixed into 1080p —
  visible quality cliff; generic "AI stock" vibe is exactly what the brief bans; every
  added cinematic second is a second not showing the product. Highest risk at $0.

## CONCEPT C — "Learn in Public" (Developer-native explainer)

**Story idea.** POV of one real learner session, screen-recorded end to end: enroll →
lesson → run code → pass assessment → dashboard XP tick → certificate. Narrated like a
calm dev-log, faster cuts, terminal-flavored type.

- **Visual identity:** 100% real UI, zoom-heavy editing, cursor choreography, mono type,
  green-on-black terminal accents.
- **Scene structure:** single continuous journey in 6 chapters with time-stamp lower-thirds.
- **Pros:** maximum authenticity; production is nearly free and fast.
- **Cons:** reads as a walkthrough/tutorial, not a launch film; low brand ambition;
  no "logo moment"; can feel like a school project if motion design is weak —
  the very failure mode the brief forbids.

---

## SELECTION: Concept A, with measured injections of B and C

**"The Launch Film" is the strongest base** because:

1. It makes the **verified-working product** the hero — the single biggest asset Code
   Yaar has (≈150 real lessons, live code runner, real certificates).
2. It survives the free-tier reality: it needs almost no AI footage, so watermarked
   720p clips never contaminate the frame.
3. It matches the actual brand language already live on the landing page
   (navy/charcoal, mint accents, mono eyebrows, tight white headlines) — the film
   becomes an extension of the site, not a parallel invention.

**Borrow from B:** one (optional) clean atmospheric beat for Scene 1 — and if the
watermark issue is unresolved, generate it in Fusion (grain + glow + drift over a
dark still) instead of AI video.
**Borrow from C:** all product footage must be *real interactions* recorded live
(a real run of real code, a real assessment pass), not static screenshots pretending.

### Final visual identity system

| Token | Spec |
|---|---|
| Background | `#0d1826`–`#0f1d32` (sampled from the live site's navy) with subtle vignette |
| Type | White `#f5f7fa` headlines, tight `-2%` tracking; mono uppercase eyebrows in mint |
| Accent | Mint/emerald `~#34d399` family (sample exact hex from site at record time — no raw hex invented in templates; pull from `globals.css` tokens) |
| Panels | Real UI screenshots/recordings in rounded-12px browser chrome, 30% soft drop shadow, 2–4° parallax |
| Motion | 24fps feel at 30fps export; entrances `ease-out 0.5s`; drift ≤5% over 6s |
| Transitions | Cuts; panel slide; one dissolve to end card. **No wipes, spins, or zooms-punch** |
| Audio | Ambient electronic bed −22 LUFS feel, synced UI foley, single sub-boom at reveal |

### Guardrails (from the brief, enforced)

No fake UI — every pixel of product shown comes from the verified route list in
RESEARCH.md. No AI claims, no quiz-engine claims, no cartoon assets, no neon,
no template stickers, no emoji, no stock-photo "happy students."
