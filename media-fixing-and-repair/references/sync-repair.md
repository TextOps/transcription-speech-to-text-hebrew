# Audio/Video Sync Repair

Covers Category B. Always diagnose the sync type before applying a fix — the two sub-types have completely different causes and solutions.

---

## Identify the sync type first

Run FFprobe and compare `start_time` between streams:

```bash
ffprobe -v quiet -show_streams -print_format json "<file>" | grep start_time
```

Then compare frame rates:

```bash
ffprobe -v quiet -show_streams -print_format json "<file>" | grep -E "r_frame_rate|avg_frame_rate"
```

| Symptom | Likely type | Fix |
|---|---|---|
| Audio shifted by fixed amount from start | B1 — Constant offset | `itsoffset` |
| In sync at start, drifts over time | B2 — VFR drift | Convert to CFR |
| Both of the above | Both | CFR conversion first, then itsoffset if residual |

---

## B1 — Constant Offset (fixed desync throughout)

**Cause:** The audio and video streams have different `start_time` values inside the container. Common in files from capture cards, screen recorders, or phone recordings with delayed audio init.

**Find the offset:**

```bash
# The offset to apply = video_start_time - audio_start_time
ffprobe -v quiet -show_streams -print_format json "<input>" | grep start_time
```

Example: video `start_time = 0.000000`, audio `start_time = 1.500000` → audio starts 1.5s late → use `itsoffset 1.5` to delay video by the same amount (or advance audio).

### Simple offset fix (lossless, stream-copy)

```bash
# Delay video by N seconds to match late audio
# (Or equivalently: advance audio by declaring video input first with no offset)
ffmpeg -itsoffset 1.5 -i "<input>" -i "<input>" \
  -map 0:v -map 1:a \
  -c copy \
  "<output_synced.mp4>"
```

> The file is opened twice. The first input (with `itsoffset`) provides the delayed video. The second provides the audio unchanged. This is the correct pattern for applying itsoffset to a single file.

### Fine-tuning offset sign

- Audio arrives **too late** (lip flap before sound): delay the video → positive `itsoffset` before video input
- Audio arrives **too early** (sound before lips move): delay the audio → positive `itsoffset` before audio input

```bash
# Delay audio by 0.8 seconds
ffmpeg -i "<input>" -itsoffset 0.8 -i "<input>" \
  -map 0:v -map 1:a \
  -c copy \
  "<output_synced.mp4>"
```

---

## B2 — Progressive Drift (Variable Frame Rate)

**Cause:** The file has Variable Frame Rate (VFR) — the time between frames is not constant. `r_frame_rate` and `avg_frame_rate` will differ in FFprobe output.

VFR is common in:
- Smartphone recordings (adaptive frame rate for battery saving)
- OBS screen captures
- Game recordings
- Webcam footage with dropped frames under load

NLEs (Premiere, DaVinci, Final Cut) assume CFR internally. As the video progresses, the accumulated error between VFR timestamps and the NLE's fixed frame grid grows — causing drift that worsens toward the end.

### Convert VFR → CFR

This requires re-encoding the video (lossless conversion is not possible for VFR→CFR):

```bash
ffmpeg -i "<input>" \
  -vf "fps=30" \
  -fps_mode cfr \
  -c:v libx264 -crf 18 -preset slow \
  -c:a copy \
  "<output_cfr.mp4>"
```

**Choose the target fps:** use the `r_frame_rate` value from FFprobe (e.g., 30, 60, 25, 24). Don't guess — matching the declared rate avoids unnecessary interpolation.

### If audio still drifts after CFR conversion

The `-async 1` flag stretches or compresses the audio minimally to stay aligned with the new fixed video timeline:

```bash
ffmpeg -i "<input>" \
  -vf "fps=30" \
  -fps_mode cfr \
  -c:v libx264 -crf 18 \
  -c:a aac -async 1 \
  "<output_cfr_synced.mp4>"
```

`-async 1` makes very small timing adjustments — it's not perceptible to the ear on normal footage.

---

## Verifying sync is fixed

After applying any sync fix, check that `start_time` values are now aligned:

```bash
ffprobe -v quiet -show_streams -print_format json "<output>" | grep start_time
```

Both streams should report `0.000000` (or identical non-zero values). Also verify:

```bash
ffprobe -v quiet -show_streams -print_format json "<output>" \
  | grep -E "r_frame_rate|avg_frame_rate"
```

After CFR conversion, both values should be identical (e.g., `"30/1"` and `"30/1"`).
