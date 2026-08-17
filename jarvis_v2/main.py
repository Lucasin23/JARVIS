#!/usr/bin/env python3
"""
JARVIS AI Assistant - Entry Point
A voice/text-controlled AI assistant inspired by Iron Man's JARVIS.
Designed for macOS with full system control capabilities.

Usage:
    python main.py                       # Text in, voice out (default)
    python main.py --voice               # Full voice mode (voice in + voice out)
    python main.py --text                # Text-only mode (no voice output)
    python main.py --voice-in            # Voice input, text output
    python main.py --wake-word           # Wake-word mode ("Hey JARVIS" hands-free)
    python main.py --no-proactive         # Disable proactive monitoring

For setup instructions, see README.md

Requirements: Python 3.10+
Platform: macOS (optimized for Apple Silicon M1+)
"""

import argparse
import sys

from assistant import JarvisAssistant
from speech import is_voice_input_available, is_voice_output_available


def parse_args():
    parser = argparse.ArgumentParser(
        description="JARVIS AI Assistant - Your personal AI butler for macOS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              Text input + voice output (default)
  python main.py --voice      Full voice mode
  python main.py --text       Silent text-only mode
  python main.py --voice-in   Voice input, text output (for quiet environments)
  python main.py --wake-word  Hands-free: say "Hey JARVIS" to activate
  python main.py --no-proactive  Disable background system monitoring
        """,
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Enable full voice mode (voice input + voice output)",
    )
    parser.add_argument(
        "--voice-in",
        action="store_true",
        help="Enable voice input only (responses are text)",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Text-only mode (no voice input or output)",
    )
    parser.add_argument(
        "--wake-word",
        action="store_true",
        help="Enable wake-word mode: say \"Hey JARVIS\" to activate hands-free",
    )
    parser.add_argument(
        "--no-proactive",
        action="store_true",
        help="Disable proactive system monitoring (battery alerts, CPU warnings, etc.)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Determine input/output modes
    if args.wake_word:
        # Wake-word mode requires voice input
        voice_in = True
        voice_out = True
        wake_word = True
    elif args.voice:
        voice_in = True
        voice_out = True
        wake_word = False
    elif args.voice_in:
        voice_in = True
        voice_out = False
        wake_word = False
    elif args.text:
        voice_in = False
        voice_out = False
        wake_word = False
    else:
        voice_in = False
        voice_out = True
        wake_word = False

    proactive = not args.no_proactive

    # Check capabilities and warn if voice was requested but unavailable
    if (voice_in or wake_word) and not is_voice_input_available():
        print("\n[!] Voice input is not available.")
        if wake_word:
            print("    Wake-word mode requires microphone input.")
            print("    Install: pip install -r requirements-voice.txt")
            print("    For better wake-word: pip install -r requirements-wake.txt")
        else:
            print("    Install dependencies: pip install -r requirements-voice.txt")
            print("    See README.md for platform-specific PyAudio installation.")
        print("    Switching to text input mode.\n")
        voice_in = False
        wake_word = False

    if voice_out and not is_voice_output_available():
        print("\n[!] Voice output is not available.")
        print("    Install dependency: pip install pyttsx3")
        print("    Switching to text output mode.\n")
        voice_out = False

    if wake_word:
        from wake_word import is_wake_word_available, get_wake_word_engine
        if not is_wake_word_available():
            print("\n[!] No wake-word engine available.")
            print("    Install Porcupine for offline wake-word detection:")
            print("      pip install -r requirements-wake.txt")
            print("    Or install SpeechRecognition for fallback mode:")
            print("      pip install -r requirements-voice.txt")
            print("    Switching to normal voice mode.\n")
            wake_word = False

    # Create and start the assistant
    jarvis = JarvisAssistant(
        voice_input=voice_in,
        voice_output=voice_out,
        proactive=proactive,
        wake_word=wake_word,
    )

    try:
        jarvis.run()
    except KeyboardInterrupt:
        print("\n\nJARVIS is shutting down. Goodbye, sir.")
        sys.exit(0)


if __name__ == "__main__":
    main()
