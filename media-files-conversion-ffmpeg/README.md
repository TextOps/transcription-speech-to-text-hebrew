# Media Files Conversion — FFmpeg Skill

Natural language FFmpeg operations with opinionated best practices built-in.

## Features

- 🚀 **Smart defaults**: Stream copy when possible, efficient presets, CPU-only encoding
- 💬 **Context-aware**: Asks about transcription before audio conversion (Whisper-optimized)
- 🛠️ **Helper script**: `ffmpeg_helper.py` for common operations
- 📚 **Built-in reference**: Detailed presets guide in `references/presets.md`

## Usage

The skill provides natural language FFmpeg operations:

- "Extract audio from this video for transcription"
- "Convert this MKV to MP4"
- "Trim this video from 1:30 to 2:45"
- "Resize this video to 720p"
- "Compress this for WhatsApp"

## Helper Script

```bash
# Extract audio (auto-detects purpose)
python3 scripts/ffmpeg_helper.py extract-audio input.mp4 --ask-purpose

# Convert video (smart defaults)
python3 scripts/ffmpeg_helper.py convert input.mkv output.mp4

# Trim video (fast mode by default)
python3 scripts/ffmpeg_helper.py trim input.mp4 output.mp4 --start 00:01:30 --end 00:02:45

# Resize video
python3 scripts/ffmpeg_helper.py resize input.mp4 output.mp4 --height 720

# Compress for messaging
python3 scripts/ffmpeg_helper.py compress input.mp4 output.mp4 --target whatsapp
```

## Best Practices

1. **Stream copy by default** - Avoid re-encoding when possible (10x faster, no quality loss)
2. **CPU-only encoding** - More reliable and hardware-agnostic than GPU encoders
3. **Fast presets** - Good balance of speed/quality (default: `fast`)
4. **Context-aware audio** - Whisper-optimized (16kHz mono) for transcription

## Requirements

- FFmpeg installed (`brew install ffmpeg` or system package manager)
- Python 3.7+ (for helper script)

## License

MIT
