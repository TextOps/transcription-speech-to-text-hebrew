# Visual Quality & Color Reference

Covers Category E (visual fixes) and Category G (color space, metadata).
All fixes here require re-encoding the video — there is no lossless path for visual corrections.
Use CRF 17–18 for visually lossless output. See `encoding.md` for full CRF guidance.

---

## Category E — Visual Quality Fixes

### E1 — Deinterlace (interlaced → progressive)

Interlaced video shows "combing" artifacts on motion — horizontal lines where odd and even fields don't align. Common in broadcast footage (PAL 50i, NTSC 29.97i).

`yadif` (Yet Another Deinterlacing Filter) is the standard high-quality deinterlacer:

```bash
ffmpeg -i "<input>" \
  -vf "yadif=mode=1" \
  -c:v libx264 -crf 18 \
  -c:a copy \
  "<output_progressive.mp4>"
```

`mode=1` = output one frame per field (doubles frame count). Use `mode=0` to keep original frame rate (drops half the fields — faster but slightly lower quality).

For PAL 50i → 25p (keep frame count, best quality):
```bash
-vf "yadif=mode=0:parity=1"
```

### E2 — Denoise (reduce digital noise / grain)

**Light denoise** — good for webcam footage or slightly noisy video. Fast:
```bash
ffmpeg -i "<input>" \
  -vf "hqdn3d=4:3:6:4.5" \
  -c:v libx264 -crf 20 \
  -c:a copy \
  "<output_denoised.mp4>"
```

**Strong denoise** — for very noisy low-light footage. Much slower:
```bash
ffmpeg -i "<input>" \
  -vf "dctdnoiz=sigma=10" \
  -c:v libx264 -crf 18 \
  -c:a copy \
  "<output_denoised.mp4>"
```

Adjust `sigma` (1–20): higher values remove more noise but also soften detail.

### E3 — Stabilize shaky footage

Two-pass stabilization using `vidstab`. Requires the `vidstab` plugin (included in most ffmpeg builds):

```bash
# Pass 1: analyze motion and write transforms
ffmpeg -i "<input>" \
  -vf "vidstabdetect=shakiness=10:accuracy=15:result=transforms.trf" \
  -f null -

# Pass 2: apply stabilization
ffmpeg -i "<input>" \
  -vf "vidstabtransform=smoothing=30:input=transforms.trf" \
  -c:v libx264 -crf 18 \
  -c:a copy \
  "<output_stable.mp4>"
```

- `shakiness` (1–10): how unstable the input is expected to be
- `smoothing` (1–100): higher = smoother result, more crop
- The output will be slightly cropped to compensate for edge movement

### E4 — Remove compression artifacts (deblock)

For heavily compressed video where "blocky" square artifacts are visible:

```bash
ffmpeg -i "<input>" \
  -vf "deblock=filter=weak:block=4" \
  -c:v libx264 -crf 20 \
  -c:a copy \
  "<output_deblocked.mp4>"
```

`filter=weak` is gentler. Use `filter=strong` for severe blocking, but expect some softness.

### E5 — Auto-detect visual anomalies

Run these before deciding on a fix — don't watch the full file manually:

```bash
# Detect sustained black frames (signal loss, unintended gaps)
ffmpeg -i "<input>" -vf "blackdetect=d=0.1:pic_th=0.98" -an -f null - 2>&1 | grep blackdetect

# Detect frozen / stuck frames
ffmpeg -i "<input>" -vf "freezedetect=n=-60dB:d=2" -an -f null - 2>&1 | grep freeze

# Signal statistics — useful for diagnosing over/underexposure or color clipping
ffmpeg -i "<input>" -vf "signalstats" -an -f null - 2>&1 | head -60
```

---

## Category G — Metadata & Color Space

### G1 — Fix color range mismatch (the "washed out" problem)

The most common color complaint. Video encoded with PC/full range (0–255) but tagged as TV/limited range (16–235), or vice versa, will look washed out or crushed on one type of display.

```bash
# Tag the file as TV/broadcast range (does not change pixel values)
ffmpeg -i "<input>" -c copy -color_range tv "<output_tv_range.mp4>"

# Tag as PC/full range
ffmpeg -i "<input>" -c copy -color_range pc "<output_pc_range.mp4>"
```

> **Warning:** This only changes the metadata tag, not the actual pixel values. If the pixel values are also wrong (actual crushed blacks or clipped whites), re-encoding with a `scale` filter to remap the range is required.

### G2 — Set BT.709 color primaries (HD standard)

For HD video that looks correct on a calibrated monitor but "off" on TVs or other players — missing color profile:

```bash
ffmpeg -i "<input>" \
  -c:v libx264 -crf 18 \
  -color_primaries bt709 \
  -color_trc bt709 \
  -colorspace bt709 \
  -movflags +write_colr \
  -c:a copy \
  "<output_bt709.mp4>"
```

`-movflags +write_colr` embeds the color profile in the MP4/MOV container atom so players read it without guessing.

For 4K/HDR content use `bt2020` primaries and `smpte2084` (PQ) or `arib-std-b67` (HLG) transfer.

### G3 — Fix wrong aspect ratio

When the video displays at incorrect dimensions (squished or stretched):

```bash
# Override Display Aspect Ratio in metadata — lossless
ffmpeg -i "<input>" -c copy -aspect 16:9 "<output_ar_fixed.mp4>"
```

For anamorphic content where the pixel aspect ratio (SAR) is the issue:
```bash
ffmpeg -i "<input>" -c copy \
  -bsf:v "h264_metadata=sample_aspect_ratio=1/1" \
  "<output_sar_fixed.mp4>"
```

### G4 — Strip all metadata (privacy / clean export)

Removes GPS coordinates, device info, timestamps, encoder tags:

```bash
ffmpeg -i "<input>" -c copy \
  -map_metadata -1 \
  "<output_clean.mp4>"
```

To strip only video metadata but keep audio tags, add `-map_metadata:s:v -1`.

### G5 — Copy metadata from one file to another

Useful after re-encoding when you want to preserve original creation date, GPS, etc.:

```bash
ffmpeg -i "<re_encoded.mp4>" -i "<original.mp4>" \
  -map 0 -map_metadata 1 \
  -c copy \
  "<output_with_original_metadata.mp4>"
```
