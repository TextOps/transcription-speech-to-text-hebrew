#!/usr/bin/env python3
"""
FFmpeg Helper - Natural language FFmpeg operations with best practices
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_ffmpeg(cmd, verbose=True):
    """Run ffmpeg command and handle errors."""
    if verbose:
        print(f"Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if verbose:
            print("✓ Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e.stderr}", file=sys.stderr)
        return False


def extract_audio(input_file, output_file=None, for_transcription=False, ask_purpose=False):
    """Extract audio from video file."""
    
    if ask_purpose:
        print("Is this audio extraction for transcription? (y/n): ", end='')
        response = input().strip().lower()
        for_transcription = response in ['y', 'yes']
    
    if output_file is None:
        ext = 'mp3' if for_transcription else 'aac'
        output_file = Path(input_file).with_suffix(f'.{ext}')
    
    if for_transcription:
        # Whisper-optimized: 16kHz mono MP3
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vn', '-ar', '16000', '-ac', '1',
            '-c:a', 'libmp3lame', '-b:a', '64k',
            str(output_file)
        ]
    else:
        # High-quality extraction with stream copy
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vn', '-acodec', 'copy',
            str(output_file)
        ]
    
    return run_ffmpeg(cmd)


def convert_video(input_file, output_file, stream_copy=True, preset='fast', crf=23):
    """Convert video with smart defaults."""
    
    if stream_copy:
        # Try stream copy first (fast, no quality loss)
        cmd = ['ffmpeg', '-i', input_file, '-c', 'copy', output_file]
        
        if run_ffmpeg(cmd, verbose=False):
            print("✓ Converted with stream copy (fast, no quality loss)")
            return True
        else:
            print("⚠ Stream copy failed (incompatible codecs). Re-encoding...")
    
    # Fallback: re-encode
    cmd = [
        'ffmpeg', '-i', input_file,
        '-c:v', 'libx264', '-preset', preset, '-crf', str(crf),
        '-c:a', 'aac', '-b:a', '128k',
        output_file
    ]
    
    return run_ffmpeg(cmd)


def trim_video(input_file, output_file, start, end, fast=True):
    """Trim video to specified time range."""
    
    if fast:
        # Fast trim with stream copy
        cmd = [
            'ffmpeg',
            '-ss', start, '-to', end,
            '-i', input_file,
            '-c', 'copy',
            output_file
        ]
    else:
        # Accurate trim with re-encoding
        cmd = [
            'ffmpeg', '-i', input_file,
            '-ss', start, '-to', end,
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-c:a', 'copy',
            output_file
        ]
    
    return run_ffmpeg(cmd)


def resize_video(input_file, output_file, width=None, height=None, preset='fast', crf=23):
    """Resize video maintaining aspect ratio."""
    
    if width is None and height is None:
        print("Error: Must specify either width or height", file=sys.stderr)
        return False
    
    if width:
        scale = f"{width}:-2"
    else:
        scale = f"-2:{height}"
    
    cmd = [
        'ffmpeg', '-i', input_file,
        '-vf', f'scale={scale}',
        '-c:v', 'libx264', '-preset', preset, '-crf', str(crf),
        '-c:a', 'copy',
        output_file
    ]
    
    return run_ffmpeg(cmd)


def compress_video(input_file, output_file, target='general', crf=None):
    """Compress video for different targets."""
    
    targets = {
        'whatsapp': {
            'scale': 'scale=-2:480',
            'crf': 28,
            'audio_bitrate': '64k',
            'audio_channels': 1
        },
        'telegram': {
            'scale': 'scale=-2:720',
            'crf': 26,
            'audio_bitrate': '96k',
            'audio_channels': 2
        },
        'general': {
            'crf': 28,
            'audio_bitrate': '96k',
            'audio_channels': 2
        }
    }
    
    if target not in targets:
        print(f"Error: Unknown target '{target}'. Use: {', '.join(targets.keys())}", file=sys.stderr)
        return False
    
    params = targets[target]
    
    cmd = ['ffmpeg', '-i', input_file]
    
    if 'scale' in params:
        cmd.extend(['-vf', params['scale']])
    
    cmd.extend([
        '-c:v', 'libx264', '-preset', 'fast',
        '-crf', str(crf or params['crf']),
        '-b:a', params['audio_bitrate'],
        '-ac', str(params['audio_channels']),
        output_file
    ])
    
    return run_ffmpeg(cmd)


def main():
    parser = argparse.ArgumentParser(description='FFmpeg Helper - Natural language operations')
    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')
    
    # Extract audio
    extract_parser = subparsers.add_parser('extract-audio', help='Extract audio from video')
    extract_parser.add_argument('input', help='Input video file')
    extract_parser.add_argument('output', nargs='?', help='Output audio file')
    extract_parser.add_argument('--for-transcription', action='store_true', help='Optimize for transcription (16kHz mono)')
    extract_parser.add_argument('--ask-purpose', action='store_true', help='Ask if audio is for transcription')
    
    # Convert video
    convert_parser = subparsers.add_parser('convert', help='Convert video format')
    convert_parser.add_argument('input', help='Input video file')
    convert_parser.add_argument('output', help='Output video file')
    convert_parser.add_argument('--no-stream-copy', action='store_true', help='Force re-encoding (skip stream copy)')
    convert_parser.add_argument('--preset', default='fast', help='Encoding preset (default: fast)')
    convert_parser.add_argument('--crf', type=int, default=23, help='CRF value (default: 23)')
    
    # Trim video
    trim_parser = subparsers.add_parser('trim', help='Trim video')
    trim_parser.add_argument('input', help='Input video file')
    trim_parser.add_argument('output', help='Output video file')
    trim_parser.add_argument('--start', required=True, help='Start time (HH:MM:SS)')
    trim_parser.add_argument('--end', required=True, help='End time (HH:MM:SS)')
    trim_parser.add_argument('--accurate', action='store_true', help='Use accurate mode (re-encode)')
    
    # Resize video
    resize_parser = subparsers.add_parser('resize', help='Resize video')
    resize_parser.add_argument('input', help='Input video file')
    resize_parser.add_argument('output', help='Output video file')
    resize_parser.add_argument('--width', type=int, help='Target width')
    resize_parser.add_argument('--height', type=int, help='Target height')
    resize_parser.add_argument('--preset', default='fast', help='Encoding preset (default: fast)')
    resize_parser.add_argument('--crf', type=int, default=23, help='CRF value (default: 23)')
    
    # Compress video
    compress_parser = subparsers.add_parser('compress', help='Compress video')
    compress_parser.add_argument('input', help='Input video file')
    compress_parser.add_argument('output', help='Output video file')
    compress_parser.add_argument('--target', default='general', choices=['whatsapp', 'telegram', 'general'],
                                  help='Compression target (default: general)')
    compress_parser.add_argument('--crf', type=int, help='Override CRF value')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'extract-audio':
        success = extract_audio(
            args.input,
            args.output,
            for_transcription=args.for_transcription,
            ask_purpose=args.ask_purpose
        )
    elif args.command == 'convert':
        success = convert_video(
            args.input,
            args.output,
            stream_copy=not args.no_stream_copy,
            preset=args.preset,
            crf=args.crf
        )
    elif args.command == 'trim':
        success = trim_video(
            args.input,
            args.output,
            args.start,
            args.end,
            fast=not args.accurate
        )
    elif args.command == 'resize':
        success = resize_video(
            args.input,
            args.output,
            width=args.width,
            height=args.height,
            preset=args.preset,
            crf=args.crf
        )
    elif args.command == 'compress':
        success = compress_video(
            args.input,
            args.output,
            target=args.target,
            crf=args.crf
        )
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
