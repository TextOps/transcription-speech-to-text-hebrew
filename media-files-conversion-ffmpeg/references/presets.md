# FFmpeg Presets Reference

## Encoding Speed Presets (x264/x265)

Presets control the speed/quality trade-off during encoding. **This skill defaults to `fast` for good balance.**

| Preset | Speed | File Size | Use Case |
|--------|-------|-----------|----------|
| `ultrafast` | Fastest | Largest | Real-time encoding, live streaming |
| `superfast` | Very fast | Larger | Quick previews, testing |
| `veryfast` | Fast | Large | Time-critical tasks |
| **`fast`** | **Balanced** | **Moderate** | **DEFAULT - General use** |
| `medium` | Moderate | Smaller | High-quality archival |
| `slow` | Slow | Smaller | Professional archival |
| `slower` | Very slow | Smallest | Maximum quality archival |
| `veryslow` | Slowest | Smallest | Extreme quality (rarely needed) |

**Recommendation:**
- Use `fast` by default (2-3x realtime)
- Use `veryfast` when speed is critical (4-5x realtime)
- Use `medium` or `slow` only for final archival (not for prototyping)

## CRF (Constant Rate Factor) Values

CRF controls quality (lower = better quality, larger file).

| CRF | Quality | Use Case |
|-----|---------|----------|
| 18-20 | Very high | Visually lossless, archival |
| 21-23 | High | General preservation (DEFAULT) |
| 24-26 | Good | Casual viewing |
| 27-29 | Moderate | Compression, web distribution |
| 30+ | Lower | Aggressive compression |

**Recommendation:**
- Use CRF 23 by default (good quality, reasonable size)
- Use CRF 18 for archival or preservation
- Use CRF 28 for messaging apps or web distribution

## Audio Presets

### For Transcription (Whisper)

```bash
-ar 16000 -ac 1 -c:a libmp3lame -b:a 64k
```

- 16kHz sample rate (Whisper's native rate)
- Mono (1 channel)
- MP3 codec at 64kbps (sufficient for speech)

### For Listening (Music/Podcast)

```bash
-c:a aac -b:a 128k
```

- AAC codec (better quality than MP3 at same bitrate)
- 128kbps (good balance)

**Or for higher quality:**

```bash
-c:a aac -b:a 192k
```

### For Stream Copy (No Re-encoding)

```bash
-c:a copy
```

- Preserves original audio codec
- No quality loss
- Fast

## Container Formats

| Format | Best For | Notes |
|--------|----------|-------|
| `.mp4` | Universal compatibility | H.264 video + AAC audio |
| `.mkv` | Feature-rich | Supports multiple audio/subtitle tracks |
| `.webm` | Web distribution | VP9 or AV1 video + Opus audio |
| `.mov` | Apple ecosystem | Similar to MP4 but Apple-centric |
| `.avi` | Legacy | Avoid for new projects |

**Recommendation:** Use `.mp4` for maximum compatibility.

## Common Codec Combinations

### Video

| Codec | Use Case | Command |
|-------|----------|---------|
| `libx264` (H.264) | Universal compatibility | `-c:v libx264` |
| `libx265` (H.265/HEVC) | Better compression (slower) | `-c:v libx265` |
| `copy` | No re-encoding | `-c:v copy` |

### Audio

| Codec | Use Case | Command |
|-------|----------|---------|
| `aac` | Universal compatibility | `-c:a aac -b:a 128k` |
| `libmp3lame` (MP3) | Compatibility, speech | `-c:a libmp3lame -b:a 128k` |
| `libopus` (Opus) | High-quality web audio | `-c:a libopus -b:a 128k` |
| `copy` | No re-encoding | `-c:a copy` |

## Resolution Scaling

### Common Resolutions

| Name | Resolution | Use Case |
|------|------------|----------|
| 4K | 3840×2160 | High-end displays |
| 1080p (Full HD) | 1920×1080 | Standard quality |
| 720p (HD) | 1280×720 | Moderate quality |
| 480p (SD) | 854×480 | Low bandwidth |
| 360p | 640×360 | Very low bandwidth |

### Scaling Commands

```bash
# Scale to specific height (maintains aspect ratio)
-vf scale=-2:720

# Scale to specific width (maintains aspect ratio)
-vf scale=1280:-2

# Scale to exact size (may distort)
-vf scale=1280:720

# Scale with aspect ratio preservation
-vf scale=1280:720:force_original_aspect_ratio=decrease
```

**Note:** `-2` tells FFmpeg to automatically calculate the dimension to maintain aspect ratio.

## Bitrate Guidelines

### Video Bitrate

| Resolution | Target Bitrate (H.264) |
|------------|------------------------|
| 4K | 20-30 Mbps |
| 1080p | 5-10 Mbps |
| 720p | 2.5-5 Mbps |
| 480p | 1-2.5 Mbps |

### Audio Bitrate

| Quality | Bitrate |
|---------|---------|
| High (music) | 192-320 kbps |
| Standard | 128 kbps |
| Speech | 64-96 kbps |
| Low (transcription) | 32-64 kbps |

## Messaging App Targets

### WhatsApp

- Max file size: 16MB (unofficial limit, varies)
- Recommended: 480p, CRF 28, 64kbps mono audio
- Command: See `compress --target whatsapp`

### Telegram

- Max file size: 2GB (official limit)
- Recommended: 720p, CRF 26, 96kbps stereo audio
- Command: See `compress --target telegram`

### Discord

- Max file size: 25MB (Nitro: 500MB)
- Recommended: 720p, CRF 27, 96kbps audio

## Hardware Acceleration (NOT USED)

This skill **deliberately avoids GPU encoders** for reliability and portability:

- ❌ `-c:v h264_nvenc` (NVIDIA)
- ❌ `-c:v h264_qsv` (Intel Quick Sync)
- ❌ `-c:v h264_videotoolbox` (macOS)

**Why CPU-only?**
- Works on any machine (VPS, Docker, local)
- Consistent quality across environments
- More reliable error handling
- GPU encoders often have quality/compatibility issues

If speed is critical, use faster presets (`veryfast`) instead of GPU acceleration.
