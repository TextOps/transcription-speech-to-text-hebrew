# Audio Engineering Reference

Covers Category D: channel mapping, downmixing, mixing multiple sources, and preparing audio for ASR/transcription.

---

## D1 — Extract a single channel as mono

```bash
# Extract left channel (index 0)
ffmpeg -i "<input>" -map_channel 0.0.0 "<output_left.wav>"

# Extract right channel (index 1)
ffmpeg -i "<input>" -map_channel 0.0.1 "<output_right.wav>"
```

Use when one channel contains only noise or a different source (common in interview recordings where each side of the stereo field is a different mic).

---

## D2 — Merge separate mono tracks into stereo

```bash
ffmpeg -i "<left.wav>" -i "<right.wav>" \
  -filter_complex "[0:a][1:a]amerge=inputs=2[aout]" \
  -map "[aout]" \
  "<output_stereo.wav>"
```

For more than 2 inputs, increase `inputs=N` to match. The `amerge` filter creates a single multi-channel stream from separate mono inputs — it does not mix them together (use `amix` for mixing).

---

## D3 — Downmix multi-channel to stereo

### Simple downmix (quick, adequate for most use cases)

```bash
ffmpeg -i "<input>" -ac 2 -c:v copy "<output_stereo.mp4>"
```

FFmpeg applies its default downmix matrix. Good for casual use.

### Custom pan downmix (preserves loudness, broadcast-quality)

The simple `-ac 2` approach can lose surround energy. This pan filter implements a standard film downmix matrix:

```bash
ffmpeg -i "<input>" \
  -filter_complex "[0:a]pan=stereo|c0=0.5*c0+0.707*c2+0.5*c4|c1=0.5*c1+0.707*c2+0.5*c5[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k \
  "<output_downmixed.mp4>"
```

Channel mapping for standard 5.1:
- `c0` = Front Left, `c1` = Front Right, `c2` = Center (LFE omitted), `c4` = Back Left, `c5` = Back Right
- Center channel mixed at -3dB (0.707) into both sides — this is ITU-R BS.775 standard

---

## D4 — Pan Law: fix volume drop after mono→stereo conversion

When a mono source is placed identically in both stereo channels, the perceived volume increases by ~3dB. FFmpeg compensates by attenuating by 3dB. If the result sounds too quiet, add this back:

```bash
ffmpeg -i "<input_mono>" \
  -filter_complex "[0:a]pan=stereo|c0=c0|c1=c0,volume=3dB[aout]" \
  -map "[aout]" \
  "<output_stereo_normalized.wav>"
```

The `volume=3dB` filter applies a 3 dB gain after the pan to restore the original perceived loudness.

---

## D5 — Split a multi-channel file into separate mono files

Useful for multi-mic production recordings where each channel is a separate microphone:

```bash
ffmpeg -i "<input_8ch.wav>" \
  -filter_complex "[0:a]channelsplit=channel_layout=7.1[FL][FR][FC][LFE][BL][BR][SL][SR]" \
  -map "[FL]"  ch1_FL.wav \
  -map "[FR]"  ch2_FR.wav \
  -map "[FC]"  ch3_Center.wav \
  -map "[LFE]" ch4_LFE.wav \
  -map "[BL]"  ch5_BL.wav \
  -map "[BR]"  ch6_BR.wav \
  -map "[SL]"  ch7_SL.wav \
  -map "[SR]"  ch8_SR.wav
```

For stereo source: `channel_layout=stereo`, outputs `[FL]` and `[FR]`.

---

## D6 — Mix multiple audio streams together (amix)

Different from `amerge` — `amix` actually blends signals together into fewer channels:

```bash
# Mix dialog + music + SFX into a single stereo output
ffmpeg -i "<dialog.wav>" -i "<music.wav>" -i "<sfx.wav>" \
  -filter_complex "[0:a][1:a][2:a]amix=inputs=3:duration=first:dropout_transition=2[aout]" \
  -map "[aout]" \
  "<output_mixed.wav>"
```

- `duration=first` — output ends when the first input ends
- `duration=longest` — output ends when the longest input ends
- `dropout_transition=2` — fade out any input that ends early over 2 seconds

---

## D7 — Prepare audio for ASR / Whisper transcription

This is the most important audio recipe for transcription pipelines. These settings are optimal for Whisper and most cloud STT engines (Google, AWS, Azure):

```bash
ffmpeg -i "<input>" \
  -ar 16000 \
  -ac 1 \
  -c:a pcm_s16le \
  "<output_for_asr.wav>"
```

| Parameter | Value | Why |
|---|---|---|
| `-ar 16000` | 16 kHz sample rate | Whisper's native processing rate — avoids internal resampling and latency |
| `-ac 1` | Mono | All STT engines downmix to mono internally; sending mono saves 50% file size with zero quality loss for transcription |
| `-c:a pcm_s16le` | 16-bit PCM (uncompressed) | Standard for speech processing; 24-bit or 32-bit gives no accuracy improvement for voice |

### Extract only a specific time segment for ASR

```bash
ffmpeg -ss 00:10:00 -to 00:20:00 -i "<input>" \
  -ar 16000 -ac 1 -c:a pcm_s16le \
  "<output_segment_asr.wav>"
```

Use `-ss` before `-i` for fast seeking (keyframe-accurate), or after `-i` for frame-accurate (slower).

### Target a specific file size for upload limits

```bash
# Encode as FLAC (lossless, ~40% smaller than WAV, excellent for STT)
ffmpeg -i "<input>" \
  -ar 16000 -ac 1 \
  -c:a flac \
  "<output_asr.flac>"

# Encode as Opus (lossy but excellent quality at 32kbps for voice)
ffmpeg -i "<input>" \
  -ar 16000 -ac 1 \
  -c:a libopus -b:a 32k \
  "<output_asr.opus>"
```
