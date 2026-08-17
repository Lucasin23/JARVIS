"""
Speech module - Text-to-Speech and Speech-to-Text with graceful fallbacks.
If voice libraries aren't available, everything degrades to text mode silently.
"""

import os
import sys

# ---------------------------------------------------------------------------
# Text-to-Speech
# ---------------------------------------------------------------------------

_tts_engine = None
_tts_available = False

try:
    import pyttsx3
    _tts_available = True
except ImportError:
    pass


def _get_tts_engine():
    """Lazily initialize the TTS engine."""
    global _tts_engine
    if _tts_engine is None and _tts_available:
        try:
            _tts_engine = pyttsx3.init()
            _tts_engine.setProperty("rate", 175)
        except Exception:
            return None
    return _tts_engine


def speak(text: str, voice: bool = True) -> None:
    """
    Speak text aloud if voice is enabled and TTS is available.
    Always prints to console as well.
    """
    if text:
        print(f"\n[JARVIS]: {text}")

    if not voice or not _tts_available or not text:
        return

    engine = _get_tts_engine()
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass  # Silently fall back to text-only


# ---------------------------------------------------------------------------
# Speech-to-Text
# ---------------------------------------------------------------------------

_stt_available = False

try:
    import speech_recognition as sr
    _stt_available = True
except ImportError:
    pass


def listen(timeout: int = 5, phrase_limit: int = 10) -> str | None:
    """
    Listen for a voice command via microphone.
    Returns recognized text, or None if listening fails.
    """
    if not _stt_available:
        return None

    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)

        text = recognizer.recognize_google(audio)
        return text.lower().strip()
    except Exception:
        return None


def is_voice_input_available() -> bool:
    return _stt_available


def is_voice_output_available() -> bool:
    return _tts_available
