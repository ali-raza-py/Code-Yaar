# TOOL COMPARISON — Free AI Video Production Stack (researched November 2026)

> All limits below were cross-checked against official pricing/help pages or multiple
> recent secondary sources (links at the end). **Nothing here claims unlimited free
> generation.** Where sources conflict, the conflict is stated. Free tiers change
> often — re-verify the flagged items the day of production.

## 1. Master comparison

| Tool | Role | Free tier (verified) | Watermark | Export res | Commercial use | Verdict |
|---|---|---|---|---|---|---|
| **DaVinci Resolve (free)** | Final editor, color, audio, Fusion motion graphics | Full free app, no time cap; up to UHD 3840×2160 8-bit/60fps; AI features (magic mask etc.) and >4K are Studio-only | ❌ None | 4K | ✅ Yes | **Backbone of the whole pipeline. Keep.** |
| **OBS Studio** | Screen recording of the real product | Completely free, open source | ❌ None | Any | ✅ Yes | **Keep — only sane way to capture the product.** |
| **Canva (free)** | Title cards, lower-thirds, social crops, device frames, simple animated text | Free video editor exports **1080p without watermark** *as long as only free assets are used*; premium elements force paid export; limited monthly AI uses | ❌ (if careful) | 1080p | ✅ With free assets | **Keep for design support.** |
| **Kling AI** | Cinematic AI B-roll (2–3 shots max) | ~**66 credits/day** (reduced from 166 historically); a 5s standard clip ≈ 33 credits → ~2 clips/day; free output watermarked | ✅ Yes (free) | 720p | ⚠️ Check ToS | **Best *recurring* free AI video credits. Use sparingly or skip.** |
| **Runway** | High-end AI video | **125 credits ONE-TIME** (never refresh), 720p, watermarked | ✅ Yes | 720p | Paid plans only for robust terms | Skip — one-time credits, watermarked. |
| **Pika** | Stylized AI video | ~**80 credits/month**, 480p on free; third-party sources disagree on watermark/commercial rights for free tier | ⚠️ Unverified | 480p | ⚠️ Verify at pika.art/pricing | Skip — 480p too soft next to 1080p screen capture. |
| **Luma Dream Machine** | Cinematic AI video | Small daily/monthly free allowance, watermarked; credits metered per second per resolution | ✅ Yes | ≤720p free | ⚠️ | Skip — no advantage over Kling's daily refresh. |
| **InVideo AI** | Auto-generated "script→video" explainers | Free: watermark, capped monthly exports (~4–10/mo per current sources), ~3-min cap | ✅ Heavy | 720p | Paid to remove | **Skip — produces the generic template look the brief bans.** |
| **VEED.io** | Browser editor, captions | Free: watermark on every export, 720p cap, limited upload minutes | ✅ Yes | 720p | Paid | Skip. |
| **CapCut (desktop)** | Fast social-style editing | Free 1080p export without watermark **if no Pro features/templates used**; sources conflict on 4K in free (verify in-app before relying) | ⚠️ Only via Pro assets | 1080p+ | ⚠️ Check commercial terms | Optional alternate editor; Resolve is stronger and fully clean. |
| **Adobe Express** | Quick graphics | Free tier with limited exports/templates; premium assets locked | ⚠️ Mixed | 1080p | ✅ with free assets | Redundant — Canva covers this role. |
| **Jitter** | UI motion graphics (Figma-like for motion) | Free: **720p exports with watermark** | ✅ Yes | 720p | ⚠️ | **The brief asked us to evaluate it. Result: free tier is too crippled to be the motion tool. Replace with Resolve Fusion + Canva.** |
| **TTSMaker** | AI voiceover | Free, 100+ languages, 600+ voices; official terms state generated audio is **free for commercial use** (one aggregator claims attribution needed for *certain voices* — read the voice's license note before use) | — | MP3/WAV | ✅ (verify per voice) | **Best zero-budget commercial-safe VO.** |
| **ElevenLabs** | Premium AI voice | 10k credits/mo (~10 min) BUT **no commercial license on free plan** (official docs) | — | — | ❌ on free | Not legally usable for a promo video at $0. Skip. |
| **Pixabay Music / SFX** | Background music, whooshes, UI clicks | Free Content License: commercial use, no attribution | — | MP3/WAV | ✅ | **Keep.** |
| **Figma (free)** | Frame/retouch screenshots before animation | Full free personal tier | — | PNG/SVG | ✅ | Optional support. |

## 2. Key findings that shaped the recommendation

1. **Every "AI explainer in one click" tool (InVideo, VEED) watermarks and caps hard** —
   and their output is exactly the template-look the brief bans. They are out.
2. **Jitter's free tier (720p + watermark) disqualifies it** as a primary motion tool,
   despite being the "obvious" choice in the prompt. DaVinci Fusion is harder to learn
   but exports clean 4K and can animate real UI screenshots better than Jitter's free tier.
3. **AI video generators are all weak on free tiers**: Runway is one-time credits,
   Pika/Luma cap resolution at 480–720p, and every free output is watermarked except
   unverified claims about Pika. **Only Kling refreshes daily (66/day).**
   → Strategic conclusion: **AI footage must be a garnish (≤3 short atmospheric shots),
   not the meal.** The meal is real screen recordings — which is also the honest choice:
   the product footage *is* the hero.
4. **ElevenLabs free = non-commercial.** A startup launch video is commercial.
   TTSMaker's published terms grant commercial use, making it the correct zero-budget pick;
   human narration remains the quality ceiling at $0 (record on a phone under a blanket).
5. **DaVinci Resolve free is genuinely professional** (the same app used for Hollywood
   work), supports commercial use, has no watermark, and its Fusion tab replaces the
   entire motion-graphics spend.
6. Sources conflict on **CapCut free 4K** (2026 reports both ways) and on **Kling's
   exact daily figure** (66/day is the current consistent report, previously 166).
   Re-verify in-app on production day; the pipeline does not depend on either.

## 3. Recommended zero-budget stack

| Job | Tool | Cost |
|---|---|---|
| Capture real product | **OBS Studio** | $0 |
| Stills, cards, crops, device frames | **Canva Free** (free assets only) | $0 |
| UI motion (Ken Burns, panel reveals, cursor trails) | **DaVinci Resolve → Fusion** | $0 |
| Optional cinematic B-roll (2–3 shots) | **Kling AI free** (accept watermark → design shots where watermark is unobtrusive, or substitute Fusion-generated abstract backgrounds) | $0 |
| Voiceover | **TTSMaker** (commercial-safe voices) or a human take | $0 |
| Music + SFX | **Pixabay** | $0 |
| Assembly, color, mix, export 1080p/4K | **DaVinci Resolve** | $0 |

**Fully achievable at $0, including commercial use.** The only quality compromise is
AI-clip watermarks — which we design around by keeping AI footage under ~15% of runtime
or replacing it with Fusion-generated abstract shots (instructions in PRODUCTION-GUIDE.md).

## 4. Source links

- DaVinci Resolve free capabilities & 4K limits — https://www.blackmagicdesign.com/products/davinciresolve ; https://davinciresolveclub.com/davinci-resolve-free-version-features/
- Runway free plan (125 one-time credits) — https://help.runwayml.com/hc/en-us/articles/50404627334547-Free-plan-details ; https://help.runwayml.com/hc/en-us/articles/15124877443219-How-do-credits-work
- Kling free tier (66 credits/day, watermarked) — https://www.aitoolcurator.com/learn/kling-guide/free-plan-limits/ ; https://whichoneisreal.com/compare/best-free-ai-video/
- Luma pricing/credits — https://lumalabs.ai/pricing ; https://www.aitoolcurator.com/learn/luma-guide/free-tier/
- Pika pricing — https://pika.art/pricing ; https://lumalabs.ai/news/pika-pricing
- InVideo free plan caps — https://invideo.io/pricing/ ; https://resource.digen.ai/invideo-ai-free-plan-pricing-2026/
- VEED free plan — https://www.veed.io/pricing ; https://www.guidde.com/knowledge-hub/veed-io-pricing-plans-alternatives-2026
- CapCut free vs Pro (conflicting 4K reports) — https://www.miracamp.com/learn/capcut/price-free-vs-capcut-pro ; https://freealternatives.to/capcut/review
- Canva free video export (no watermark with free assets) — https://www.canva.com/video-editor/ ; https://www.canva.com/pricing/
- Jitter free tier (720p + watermark) — https://www.tiltit.video/blog/best-motion-graphics-tools-non-designers-2026 ; https://jitter.video/
- ElevenLabs free = no commercial license — https://elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform ; https://elevenlabs.io/pricing
- TTSMaker commercial terms — https://ttsmaker.com/copyright_and_commercial_license_terms
- Pixabay Content License — https://pixabay.com/service/license-summary/
