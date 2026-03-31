# Container Repair & Bitstream Fixes

Covers Category A (container/index corruption) and Category C (bitstream structural issues).
The golden rule: always try stream-copy (`-c copy`) first — it is lossless and runs in seconds.

---

## Category A — Container / Index Corruption

### A1 — Can't seek / moov atom at end of file

The file plays but seeking is broken, or web playback stalls waiting for metadata.
The `moov` atom (the file's "map") is at the end instead of the beginning.

```bash
ffmpeg -i "<input>" -c copy -movflags +faststart "<output_faststart.mp4>"
```

This is a common artifact of files recorded without streaming in mind. The fix is instant.

### A2 — Broken container — rebuild index

Wrong duration reported, or FFprobe says `nb_frames: N/A`:

```bash
ffmpeg -i "<input>" -c copy -map 0 "<output_reindexed.mp4>"
```

If FFmpeg fails to read the file at the default probe size:

```bash
ffmpeg -analyzeduration 200M -probesize 200M \
  -i "<input>" -c copy "<output.mp4>"
```

### A3 — Truncated file (recording interrupted mid-write)

The file was cut off. FFmpeg extracts whatever was successfully written before the interruption:

```bash
# Attempt 1: ignore errors and copy
ffmpeg -err_detect ignore_err -i "<input>" -c copy "<output_recovered.mp4>"
```

```bash
# Attempt 2: more aggressive — discard corrupt packets and ignore DTS
ffmpeg -fflags +discardcorrupt+igndts -i "<input>" -c copy "<output_recovered.mp4>"
```

> **Note:** If the `moov` atom was never written (recording crashed before finalization), neither of these will work. In that case, mention `untrunc` to the user — it requires a healthy reference file recorded on the same device with the same settings.

### A4 — AVI with broken index

```bash
ffmpeg -i "<input.avi>" -c copy "<output_fixed.avi>"
```

FFmpeg automatically rebuilds the AVI index during remux.

### A5 — MKV with broken or missing timestamps

```bash
ffmpeg -fflags +genpts -i "<input.mkv>" -c copy "<output_fixed.mkv>"
```

`+genpts` regenerates Presentation Timestamps from scratch when they are missing or broken.

---

## Category C — Bitstream / Structural Issues

Bitstream Filters (BSF) modify the compressed stream directly without decoding — they are fast, lossless, and fix codec-level structural problems that stream-copy alone cannot address.

### C1 — H.264: add Annex-B start codes (MP4 → TS/raw)

MP4 stores H.264 in AVCC format (length-prefixed). Transport Streams need Annex-B (start-code prefixed). This filter adds those codes:

```bash
ffmpeg -i "<input.mp4>" -c copy \
  -bsf:v h264_mp4toannexb \
  "<output.ts>"
```

### C2 — AAC: ADTS → ASC (for packaging into MP4)

AAC audio from raw streams uses ADTS headers. Putting it into an MP4 container requires ASC format. Without this fix, FFmpeg will error with "Could not write header":

```bash
ffmpeg -i "<input>" -c copy \
  -bsf:a aac_adtstoasc \
  "<output.mp4>"
```

### C3 — H.264: fix wrong aspect ratio or color flags (no re-encode)

Correct metadata embedded in the bitstream without touching the actual video data:

```bash
# Fix sample aspect ratio
ffmpeg -i "<input>" -c copy \
  -bsf:v "h264_metadata=sample_aspect_ratio=1/1" \
  "<output_sar_fixed.mp4>"
```

### C4 — HEVC/H.265: Annex-B conversion (MP4 → TS)

```bash
ffmpeg -i "<input.mp4>" -c copy \
  -bsf:v hevc_mp4toannexb \
  "<output.ts>"
```

### C5 — General corruption: full re-encode as last resort

When BSF fixes don't resolve decoding errors (visible artifacts, decoder crashes):

```bash
ffmpeg -err_detect ignore_err \
  -i "<input>" \
  -c:v libx264 -crf 20 -preset medium \
  -c:a aac -b:a 192k \
  "<output_reencoded.mp4>"
```

Use CRF 18–20 for near-lossless quality. See `encoding.md` for full CRF guidance.
