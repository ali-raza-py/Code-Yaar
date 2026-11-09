# AI VIDEO PROMPTS — Cinematic Support Footage (Optional Garnish)

**Policy from TOOL-COMPARISON.md:** AI-generated footage is capped at ~15% of runtime
(≤2 clips, ≤6s each). It may only ever show *atmosphere* — never a fabricated Code Yaar
interface. If the free-tier watermark (Kling) is unacceptable, each prompt has a
**Fusion fallback** that achieves the beat with zero AI clips — the recommended default.

Consistent visual identity for all prompts:
deep charcoal-navy palette, single cool mint/teal practical light source, white
minimal production design, shallow depth of field, film grain, no text/logos in frame,
no faces in close-up, 16:9.

---

## P1 — Scene 1 opener: "The Tutorial Trance" (5s, only if watermark acceptable)

> **Prompt:** Slow cinematic push-in on a dark dorm room at night, only light source is
> a out-of-focus laptop screen glowing cool bluish-white, reflecting faintly on a desk,
> empty coffee mug, camera drifts slowly forward with subtle handheld micro-shake,
> shallow depth of field, heavy negative space, deep charcoal and desaturated navy
> color palette, soft film grain, moody restrained atmosphere, 16:9, 5 seconds.
>
> **Negative:** text, logos, user interface details, faces, warm orange tones, neon,
> fast motion, clutter, cartoon style, lens flares.

**Fusion fallback (recommended):** blurred dark gradient plate + animated grain +
slow 5% push on an out-of-focus "screen glow" rectangle (Fusion Glow/Blur nodes). 20
minutes, no watermark, on-brand.

## P2 — Scene 6 texture: "Proof" abstract (4s, optional)

> **Prompt:** Extreme macro shot of thin sheets of dark paper sliding into perfect
> alignment on a matte charcoal surface, one edge lit by a soft mint-teal rim light,
> dust particles drifting in the light beam, slow precise motion, cinematic product-
> film lighting, shallow depth of field, deep navy shadows, minimal and clean,
> 16:9, 4 seconds.
>
> **Negative:** hands, people, text, logos, bright backgrounds, warm colors, glitch,
> fast cuts.

**Fusion fallback:** the real certificate PNG (`/certificates/[id]` preview render)
parallaxed at 3° over a matte-gradient backdrop with a drifting light sweep — this is
honest AND better, since it shows the real credential.

## P3 — Social cutdowns only: "Evolve" loop (3s, optional)

> **Prompt:** Abstract slow-moving dark liquid surface, charcoal black with faint
> teal-green bioluminescent veins emerging and spreading like circuit traces across
> the frame, top-down view, very slow elegant motion, cinematic lighting, minimal,
> no objects, 16:9, 3 second seamless loop.
>
> **Negative:** text, logos, bright flashes, cartoon, 3d render look, fast motion.

**Fusion fallback:** Noise → Blur → ColorCorrect (mint veins) as an end-card backdrop.

---

## Generation protocol (if using Kling free)

1. Account: free tier ≈ 66 credits/day; a 5s std clip ≈ 33 → generate at most 2/day,
   2–3 takes per prompt across 2 days if needed.
2. Settings: 16:9, standard mode, 5s. Do not use "high quality" mode (credit cost).
3. Pick the take with the least morphing artifacts; expect to discard ≥50%.
4. Watermark handling: the free-tier mark sits in a corner. **Do not crop to remove it
   (ToS violation risk).** Options: (a) accept it inside a blurred-edge vignette beat
   where it reads as noise, (b) upscale 720p→1080p with Resolve's scale (it softens —
   another reason these shots stay atmospheric), or (c) **use the Fusion fallbacks and
   skip AI clips entirely — the recommended decision.**
5. Grade every AI clip through the same LUT/contrast curve as screen recordings so the
   film reads as one photograph.

## Why so few prompts

The product footage IS the film (Concept A). Every second of AI atmosphere is a second
of credibility traded for vibes — and free-tier AI output visibly costs resolution.
Three optional prompts exist to service the *problem beat* and *social cutdowns only*.
