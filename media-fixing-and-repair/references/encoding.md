# Encoding, Re-packaging & Format Conversion

Covers Category F: CRF encoding strategy, container remux, audio extraction, and format conversions.

---

## The CRF Quality Model

CRF (Constant Rate Factor) is the right encoding mode for quality-driven work. Unlike fixed bitrate (CBR/VBR), CRF allocates more bits to complex scenes and fewer to simple ones — resulting in consistent visual quality throughout the file.

| CRF value | Quality level | Use case |
|---|---|---|
| 0 | Lossless | Archival only — huge files, no practical use unless mathematically lossless is required |
| 17–18 | Visually lossless | High-quality masters, no perceptible quality loss on any screen |
| 20–22 | High quality | Excellent for most distribution and editing use |
| 23 | FFmpeg default | Good all-purpose balance of quality and size |
| 26–28 | Acceptable | Review copies, fast transfers, preview renders |
| 30+ | Low quality | Thumbnails, proofs, very bandwidth-limited delivery |

Lower CRF = better quality = larger file. There is no universally "correct" value — it depends on the content and the use case. Ask the user if unsure.

---

## F1 — Standard H.264 re-encode

```bash
ffmpeg -i "<input>" \
  -c:v libx264 -crf 23 -preset slow \
  -c:a aac -b:a 192k \
  "<output.mp4>"
```

**preset** controls the tradeoff between encoding speed and compression efficiency:
- `ultrafast` / `superfast` — real-time streaming, very large files
- `medium` — default, good balance
- `slow` / `slower` — better compression, same quality at smaller file size
- `veryslow` — maximum compression, practically diminishing returns beyond `slow`

For archival or delivery masters, use `crf 18 -preset slow`.

### F2 — H.265 (HEVC) re-encode

~30% smaller file than H.264 at equivalent visual quality. Slower to encode; older devices may not support hardware decode.

```bash
ffmpeg -i "<input>" \
  -c:v libx265 -crf 28 -preset slow \
  -c:a aac -b:a 192k \
  "<output_hevc.mp4>"
```

Note: H.265 CRF scale is shifted — CRF 28 in HEVC is roughly equivalent to CRF 23 in H.264.

---

## F3 — Lossless container remux (change format, no re-encode)

When only the container needs to change and the codec is compatible:

```bash
# MP4 → MKV
ffmpeg -i "<input.mp4>" -c copy "<output.mkv>"

# MKV → MP4
ffmpeg -i "<input.mkv>" -c copy "<output.mp4>"

# MOV → MP4
ffmpeg -i "<input.mov>" -c copy "<output.mp4>"

# TS → MP4
ffmpeg -i "<input.ts>" -c copy "<output.mp4>"
```

> **Gotcha for MKV → MP4:** If the H.264 stream uses Annex-B format (common in MKV), MP4 needs the BSF fix: add `-bsf:v h264_mp4toannexb`. See `container-repair.md`.

---

## F4 — Extract audio only

```bash
# Fast copy — lossless, keeps original codec (works when source is MP4/AAC)
ffmpeg -i "<input.mp4>" -vn -c:a copy "<output.aac>"

# Re-encode to MP3
ffmpeg -i "<input>" -vn -c:a libmp3lame -q:a 2 "<output.mp3>"
# -q:a 2 ≈ 190 kbps VBR, excellent quality

# Lossless FLAC
ffmpeg -i "<input>" -vn -c:a flac "<output.flac>"

# WAV (uncompressed)
ffmpeg -i "<input>" -vn -c:a pcm_s16le "<output.wav>"
```

---

## F5 — Prepare audio for ASR / Whisper

For the full explanation, see `audio-engineering.md` (D7).

Quick recipe:
```bash
ffmpeg -i "<input>" -ar 16000 -ac 1 -c:a pcm_s16le "<output_for_asr.wav>"
```

---

## F6 — Trim / cut a segment without re-encoding

```bash
# Cut from 00:01:30 to 00:05:00 — stream copy (fast, no quality loss)
ffmpeg -ss 00:01:30 -to 00:05:00 -i "<input>" -c copy "<output_trimmed.mp4>"
```

> **Note:** Stream copy seeks to the nearest keyframe, so the actual start may be a few frames off. If frame-accurate trimming is needed, move `-ss` to after `-i` and add `-c:v libx264 -crf 18` to re-encode.

---

## F7 — Hardware-accelerated encoding (when available)

For faster encoding on supported systems. Quality is slightly lower than software encoding at the same settings.

**NVIDIA (NVENC):**
```bash
ffmpeg -i "<input>" -c:v h264_nvenc -rc:v vbr -cq:v 23 -preset p4 -c:a copy "<output.mp4>"
```

**Intel QuickSync:**
```bash
ffmpeg -i "<input>" -c:v h264_qsv -global_quality 23 -c:a copy "<output.mp4>"
```

**Apple VideoToolbox (macOS):**
```bash
ffmpeg -i "<input>" -c:v h264_videotoolbox -q:v 65 -c:a copy "<output.mp4>"
```

Check available hardware encoders on the current system:
```bash
ffmpeg -encoders 2>/dev/null | grep -E "nvenc|qsv|videotoolbox|vaapi|amf"
```
