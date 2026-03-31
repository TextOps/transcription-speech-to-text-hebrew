# Diagnostics Reference — FFprobe Deep Analysis

## Standard full diagnosis (always run first)

```bash
ffprobe -v quiet -print_format json \
  -show_format -show_streams -show_chapters \
  "<file_path>"
```

## Packet-level scan (timestamps, sequence integrity)

```bash
ffprobe -v quiet -print_format json \
  -show_packets -read_intervals "%+#200" \
  "<file_path>"
```

The `-read_intervals "%+#200"` flag reads only the first 200 packets — enough to catch timestamp issues without scanning the whole file.

## Frame-level scan (codec structure, interlacing)

```bash
ffprobe -v quiet -print_format json \
  -show_frames -read_intervals "%+#100" \
  "<file_path>"
```

## What to read from the output

| Field | Location | What it tells you |
|---|---|---|
| `codec_type` | `streams[]` | Is this stream video, audio, or subtitle? |
| `codec_name` | `streams[]` | h264, hevc, aac, mp3, opus… |
| `r_frame_rate` vs `avg_frame_rate` | `streams[]` | If they differ → VFR file (sync drift risk) |
| `start_time` | `streams[]` | Compare between video and audio — a difference means constant sync offset |
| `bit_rate` | `streams[]` or `format` | Suspiciously low → possible corruption |
| `nb_frames` | `streams[]` | "N/A" means the index is broken or the container doesn't store frame count |
| `duration` | `format` vs `streams[]` | Mismatch between format duration and stream duration → broken container or Edit List |
| `pts` / `dts` | `packets[]` | Non-monotonic values → broken timestamps, needs `-fflags +genpts` or remux |
| `pict_type` | `frames[]` | Absence of "I" frames → keyframe index problem |
| `tags.encoder` | `format` | Reveals the capture device or software (useful context for known quirks) |

## Detecting VFR

```bash
ffprobe -v quiet -show_streams -print_format json "<file>" \
  | grep -E "r_frame_rate|avg_frame_rate"
```

If `r_frame_rate` (declared) ≠ `avg_frame_rate` (measured) → VFR. Example:
```
"r_frame_rate": "60/1",
"avg_frame_rate": "29311/1000"   ← actual average is ~29.3 fps, not 60
```

## Detecting sync offset

```bash
ffprobe -v quiet -show_streams -print_format json "<file>" \
  | grep start_time
```

Offset = `video_start_time - audio_start_time`. If non-zero → use `itsoffset` fix.

## Detecting Edit Lists (MP4/MOV edts atom)

Edit Lists cause the container's "timeline duration" to differ from the underlying stream duration. They're used for non-destructive editing in MP4/MOV.

```bash
ffprobe -v trace "<file_path>" 2>&1 | grep -iE "edts|elst|media_time"
```

Key values in the output:
- `media_time` — where in the stream the edit begins
- `duration` — how long this edit segment runs
- Formula for actual start time: `media_time / (90000 for video)` seconds

Edit Lists are usually harmless — just note their presence when explaining duration discrepancies. Only flatten them (via re-encode) if they cause active compatibility problems in an NLE.

## Auto-detecting visual problems

Run these before deciding on a visual fix — they save time vs. watching the whole file.

```bash
# Black frame detection (signal loss, fade-to-black gaps)
ffmpeg -i "<input>" -vf "blackdetect=d=0.1:pic_th=0.98" -an -f null - 2>&1 | grep blackdetect

# Frozen frame detection
ffmpeg -i "<input>" -vf "freezedetect=n=-60dB:d=2" -an -f null - 2>&1 | grep freeze

# Signal statistics (brightness levels, clipping)
ffmpeg -i "<input>" -vf "signalstats" -an -f null - 2>&1 | head -60
```

## Post-fix verification (always run after any repair)

```bash
ffprobe -v quiet -print_format json \
  -show_format -show_streams \
  "<output_file>"
```

Check:
- Both video and audio streams present
- `duration` is correct
- `start_time` values are aligned (ideally both 0.000000)
- No FFprobe error messages
- `r_frame_rate` == `avg_frame_rate` (after CFR conversion)
