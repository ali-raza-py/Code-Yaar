# VOICEOVER — Narration Plan (Free-Tier, Commercial-Safe)

## 1. Options compared

| Option | Quality | Cost | Commercial use | Verdict |
|---|---|---|---|---|
| **TTSMaker** (ttsmaker.com) | Very good on its best modern voices; occasional flat prosody on long sentences | $0 | ✅ Site terms: synthesized audio free for commercial use, no fees. ⚠️ One aggregator claims *certain voices* need attribution — read the license note on the chosen voice page and screenshot it | **Recommended AI pick** |
| **Clipchamp / Microsoft Edge "Read Aloud" voices** | Good neural voices | $0 (app) | ⚠️ Microsoft's consumer ToS around extracted audio is gray; not clearly licensed for ad use | Runner-up, license-risky |
| **ElevenLabs free** | Best-in-class | $0 tier | ❌ Official docs: free plan has **no commercial license** | Unusable for a promo film at $0 |
| **Google AI Studio (Gemini TTS) free** | Very good, controllable | Free tier | ⚠️ Quotas reduced in 2026; check current speech-generation quota + terms before relying | Backup |
| **Human narration (team member)** | Highest trust; a real founder voice is a startup signal | $0 | ✅ | **Best quality-per-rupee if any team member has a calm, clear English read.** Record: phone/USB mic, closet-of-clothes treatment, 48 kHz WAV |

**Recommendation:** produce the film with TTSMaker first; if a team member volunteers,
a human re-record drops straight into the same timeline (same script, same gaps).

## 2. Voice spec (applies to both)

- **Character:** late-20s/early-30s, neutral international English, calm peer — a
  smart friend showing you something, not an ad announcer. Low energy, high certainty.
- **Speed:** ~150–160 wpm. The script is ~100 words in 58s *by design* — leave the
  gaps; silence is confidence.
- **Emphasis map:** stress on "feels", hard stop after "build something.", slow down on
  "actually explains it", "actually verify" — the two "actually"s are the thesis.
  Final four beats ("Think. Build. Evolve.") ≈ 0.8s apart, matching on-screen words.
- **Pronunciation:** "Code Yaar" = "kohd yahr" (rhymes with "car"). "XP" = letter names.
- **TTSMaker setup:** 48 kHz, highest bitrate; split generation per scene block so
  takes can be swapped without regenerating everything; pick a voice tagged US/UK
  "narration/news" style, moderate pace (−1 or −2 steps if it rushes).

## 3. Music & sound design (all Pixabay Content License — commercial, no attribution)

| Layer | Spec | Search terms used |
|---|---|---|
| Music bed | Minimal ambient-electronic, steady soft pulse, ~90–100 BPM, no vocals, no big drop, plenty of quiet versions to strip back at Scene 6 | "ambient corporate minimal", "deep focus minimal" |
| SFX palette | 1 sub-boom (logo), 2 soft whooshes (panel slides), keyboard taps (≤5 taps, not a storm), mouse click, UI "result tick", one restrained confirm chime, one terminal "solved" blip | "cinematic sub boom", "whoosh soft", "ui click", "chime subtle success" |
| Rule | Every SFX must sync to a real frame in the recording. If an effect draws attention to itself, delete it. | — |

## 4. Mix targets (Deliver page in Resolve)

- Voice: normalize peaks ≈ −6 dBFS; de-esser/low-shelf cut if TTS adds sibilance/bass bloom; 150 ms reverb send at −30 dB only on the final tagline words (the one cinematic courtesy).
- Music: −22 to −26 dB under voice; duck −4 dB automatically under VO via compressor sidechain if needed.
- SFX: −16 to −20 dB — felt, not heard-as-events.
- Master: **−14 LUFS integrated** (YouTube/social norm), true peak ≤ −1 dBTP.
- Export mix: 48 kHz stereo WAV + the video's AAC track.

## 5. Legal hygiene

Screenshot and archive: TTSMaker license page for the chosen voice, Pixabay download
pages (license certificate links) for every track/SFX used. Keeps the "free but
commercial" claim provable if the video is ever disputed.
