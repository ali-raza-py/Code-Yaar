# PRODUCTION GUIDE — Step by Step, Zero Budget

Time estimates assume one operator learning as they go. Order matters — later steps
depend on earlier ones. All software: OBS Studio, Canva (free), DaVinci Resolve (free),
TTSMaker, Pixabay. (Optional: Kling — see AI-VIDEO-PROMPTS.md; the guide works without it.)

---

## STEP 0 — Environment prep (½ h)

1. Start the app (`dev.cmd` from repo root starts backend + frontend) or point the
   browser at the deployed site. Decide: **all footage from this one environment**.
2. Log in as `demo@codeyaar.dev`. Warm it up: finish a few lessons, run snippets,
   pass one assessment, enroll in 2 courses — screens must look lived-in, not empty.
3. Windows settings: hide taskbar (auto-hide), turn off notifications, power plan
   "no sleep", close everything except the browser + OBS.
4. Browser: 1920×1080 window, 100% zoom, dark theme, no bookmarks bar
   (`Ctrl+Shift+B` to toggle), press `F11` for kiosk-style capture (a clean browser
   frame gets re-added in the edit as a design element).

## STEP 1 — Capture product footage (2–3 h; ASSET-CHECKLIST §1 is the shot list)

OBS setup (once):
- Settings → Video: Base 1920×1080, Output 1920×1080, FPS 60 (editorial flexibility
  for smooth slowdowns; export timeline is 30).
- Settings → Output → Recording: format **MKV** (crash-safe), encoder x264,
  CRF 18, preset veryfast; Audio 48 kHz.
- Source: **Window Capture** → the browser (more stable than Display Capture; no
  desktop edges in frame).
- Cursor: Windows Settings → Accessibility → Mouse → size up; add a highlight circle
  (off unless your Windows build lacks it — the halo is added in post otherwise).

Per shot: rehearse → record 2–3 takes → mark keepers in a text file
(`A5-take2.txt`). Keep each take's first/last second idle for clean trims.
Convert MKV→MP4 later with Remux (File → Remux Recordings) if Resolve is fussy.

## STEP 2 — Brand plates & graphics in Canva (1 h)

1. Create a 1920×1080 design; background = the exact navy sampled from the site.
2. Build: (a) logo lockup page (use `logo-light.png`), (b) mono mint eyebrow style,
   (c) white headline style (tight letter-spacing ≈ −2%), (d) browser-chrome bar
   strip (dark rounded bar, 3 grey dots, empty address pill), (e) end card.
   **Use only free elements** (filter "Free") — otherwise export demands payment.
3. Share → Download → **PNG, transparent** for overlays; JPG for plates.
   No video export from Canva — Canva is the *graphics* shop; Resolve animates.

## STEP 3 — (Optional) AI B-roll (1 h + generation waits)

Only after approving AI-VIDEO-PROMPTS.md direction. Kling free: generate P1, pick the
least-artifact take. If the watermark bothers you at 100% zoom — it will — switch to
the Fusion fallback (Step 5b). Skipping Step 3 entirely is a legitimate, recommended
choice.

## STEP 4 — Voiceover (45 m)

1. ttsmaker.com → paste VIDEO-SCRIPT.md's clean read **per scene** (7 files) →
   test 2–3 voices → render chosen takes at max quality → download WAV/MP3.
2. In Resolve Fairlight: place VO_01…07 at their scene start points (table in
   STORYBOARD.md). Nudge scene handles ±0.3s to fit the *voice*, not vice versa —
   the picture was budgeted with slack on purpose.
3. Strip silences > 0.6s inside lines with Razor; keep the scripted gaps *between*
   lines (those are musical).

## STEP 5 — Assembly & motion in DaVinci Resolve (main work; 1–2 days first cut)

**5a. Timeline bones.**
New project "codeyaar-launch" → timeline 1920×1080@30. Tracks:
V1 backgrounds · V2 UI panels · V3 overlays/text · V4 global grade · A1 VO · A2 SFX · A3 music.
Drop the navy plate full length; cut it at scene boundaries with 4–6 frame overlaps.

**5b. Panel choreography (the signature move, learned once, reused 6×).**
1. Drag a screen recording onto V2. Right-click → Composite in 'Fusion' for the
   fancy ones, or stay on the Edit page for simple crops:
   - Crop browser edges to the interesting region (Crop settings on the Inspector).
   - Add rounded corners + shadow without Fusion: Effects Library → "Soft Round"
     (or the free "Corner Rounder"): radius ≈12 px at full-frame, Drop Shadow
   - opacity 30%, size 12, angle −60°) via the OpenFX "Window" node equivalent —
     or in Fusion: Rectangle(mask, rounded) → Merge over background + DropShadowTool.
2. Keyframe Entrance: Start transform X +40px, opacity 0 → frame 15: X 0, opacity
   100, Ease Out (spline: bezier fast-in). Same numbers every scene = "one easing
   signature."
3. Drift: scale 100→104% over the clip (Transform node / Ken-Burns) — imperceptible
   motion kills the slideshow feel.
4. Zoom pushes (Scene 4 typing beat): duplicate clip segment, crop tighter on the
   editor region, crossfade the crop 0.6s (or keyframe Zoom-blur-free scaling).
5. Cursor halo: Fusion Ellipse (soft-edged, 20% white) tracked to the recorded cursor
   with a Tracker node — or simply a static glow PNG parented via keyframes; 8
   minutes per shot max, don't gold-plate.

**5c. Type on screen.** Text+ titles on V3 using the Canva-exported styles:
eyebrow (mono mint) top-left of panel, headline in the navy margin. Animate:
opacity + Y 12px, ease-out 0.5s, per-beat timings from STORYBOARD.md. End card:
three tagline words on 0.8s centers, static hold 2s.

**5d. Logo reveal (Scene 2).** Import logo PNG to Fusion; merge through a
Rectangle mask, animate mask width 0→100 over 0.6s (Linear → Ease), underline =
another Rectangle scaled X with 0.2s delay. One boom SFX on the first visible frame.

**5e. Transitions.** Only two kinds: hard cut, and panel-slide (outgoing +40px/
opacity-0 over 8 frames while incoming does the entrance). The single 16-frame
dissolve before the end card: Edit page → Dissolve, or keyframe opacity.

## STEP 6 — Music, SFX, mix (2–3 h)

1. Pixabay: download bed + SFX per VOICEOVER.md §3 into A3/A2.
2. Music: trim to scenes 2–7; fade in 6 frames under the boom, volume envelope:
   full in product scenes, −6 dB during certificate beat, strip percussion entirely
   from 0:50. Fade out with picture.
3. SFX: snap each to its action frame (zoom timeline to 5×, nudge with Alt+←/→).
4. Fairlight mix: VO ≈ −6 dBFS peaks, music −22…−26 under voice, SFX −16…−20;
   sidechain-duck music off VO if it fights (simple compressor, sidechain = VO bus).
5. Master meter: **−14 LUFS integrated** (Resolve's loudness meter: target ITU-R
   BS.1770-4), TP ≤ −1 dBTP. Adjust with a Limiter on master, not by boosting music.

## STEP 7 — Color & consistency pass (1 h)

On V4 node tree (Color page): one shared node — slight lift blacks to navy-black
(match plate), desaturate reds, +5 tint toward teal on highlights. This makes any
AI clip, screenshots, and recordings read as one film. Check every frame-to-frame
cut for brightness jumps; screen recordings often differ 2–3% — normalize with
Gain on the problem clip.

## STEP 8 — Deliver (30 m)

Deliver page → custom export:
- Master: MP4 · H.264 · 1920×1080 · 30 fps · restrictions off · quality 80000 kbps
  · Audio AAC 320 kbps 48 kHz. ✔ "Export video"
  (Stick to H.264 8-bit — HEVC export can be gated in the free build on Windows.)
- Check file < 200 MB for easy upload; if larger, 50 Mbps two-pass.
- Also export: 1080×1920 vertical cutdown *after* the master is approved
  (see DISTRIBUTION-STRATEGY.md).

## STEP 9 — Review loop

1. Watch on: monitor → phone (that's where most viewers will see it) → TV-size if possible.
2. Fix list, re-render only changed sections (Resolve renders in place).
3. One "fresh eyes" pass by a non-team member: where did attention drift? Cut 2 seconds there.

---

## What NOT to do (guardrails that keep it premium)

- No template intros/outros from any tool. Ever.
- No auto-caption styles, emoji, stickers, "glitch" transitions, or speed-ramped cursors.
- No zooming into UI regions the recording can't resolve — re-capture closer instead.
- Don't regenerate VO for 0.2s timing issues — move the picture.
- If a scene feels weak, it lacks either motion or a better take — never add more effects.
