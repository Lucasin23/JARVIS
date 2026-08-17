"""
Wake-Word Module — "Hey JARVIS" hands-free activation.

Two engines:
  1. Porcupine (primary) — offline, lightweight, always-on. Requires pvporcupine + access key.
  2. SpeechRecognition fallback — loops Google STT, checks for "jarvis" keyword. Requires internet.

Usage:
    detector = WakeWordDetector(engine="porcupine")
    detector.wait_for_wake_word()  # Blocks until wake word detected
    detector.cleanup()

If Porcupine isn't installed or no access key, automatically falls back to STT loop.
"""

import os
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Engine availability checks
# ---------------------------------------------------------------------------

_porcupine_available = False
_pvrecorder_available = False

try:
    import pvporcupine
    _porcupine_available = True
except ImportError:
    pass

try:
    import pvrecorder
    _pvrecorder_available = True
except ImportError:
    pass

_sr_available = False
try:
    import speech_recognition as sr
    _sr_available = True
except ImportError:
    pass


def is_wake_word_available() -> bool:
    """Check if any wake-word engine is available."""
    return _porcupine_available or _sr_available


def get_wake_word_engine() -> str:
    """Return the best available engine name."""
    if _porcupine_available and os.getenv("PICOVOICE_ACCESS_KEY", "").strip():
        return "porcupine"
    if _sr_available:
        return "speech_recognition"
    return "none"


# ---------------------------------------------------------------------------
# Porcupine-based wake-word detector
# ---------------------------------------------------------------------------

class PorcupineDetector:
    """Offline wake-word detection using Picovoice Porcupine."""

    def __init__(self):
        self._porcupine = None
        self._recorder = None
        self._running = False

    def start(self) -> bool:
        """Initialize Porcupine and recorder. Returns True if successful."""
        access_key = os.getenv("PICOVOICE_ACCESS_KEY", "").strip()
        if not access_key:
            return False

        if not _porcupine_available or not _pvrecorder_available:
            return False

        try:
            # Check for custom keyword model
            keyword_path = os.getenv("PORCUPINE_KEYWORD_PATH", "").strip()

            if keyword_path and os.path.exists(keyword_path):
                # Use custom "Hey JARVIS" model
                self._porcupine = pvporcupine.create(
                    access_key=access_key,
                    keyword_paths=[keyword_path],
                )
            else:
                # Use built-in "jarvis" keyword if available
                # Porcupine includes several built-in keywords
                available_keywords = pvporcupine.KEYWORDS

                if "jarvis" in available_keywords:
                    self._porcupine = pvporcupine.create(
                        access_key=access_key,
                        keywords=["jarvis"],
                    )
                else:
                    # Fall back to "picovoice" as the wake word
                    self._porcupine = pvporcupine.create(
                        access_key=access_key,
                        keywords=["picovoice"],
                    )

            # Start the recorder
            self._recorder = pvrecorder.PvRecorder(
                device_index=-1,
                frame_length=self._porcupine.frame_length,
            )
            self._recorder.start()
            self._running = True
            return True

        except Exception as e:
            print(f"  [Wake Word] Porcupine init error: {e}")
            self.cleanup()
            return False

    def wait_for_wake_word(self, on_listening=None) -> bool:
        """
        Block until wake word is detected.
        Returns True if detected, False if interrupted/error.

        Args:
            on_listening: Optional callback called each loop iteration
                          (e.g., to print a "listening..." message periodically).
        """
        if not self._porcupine or not self._recorder:
            return False

        keyword_label = "Hey JARVIS" if "jarvis" in str(self._porcupine.keyword_paths) + str(getattr(self._porcupine, '_keywords', [])) else "Picovoice"

        try:
            while self._running:
                audio_frame = self._recorder.read()
                keyword_index = self._porcupine.process(audio_frame)

                if keyword_index >= 0:
                    return True

                if on_listening:
                    on_listening()

        except KeyboardInterrupt:
            return False
        except Exception as e:
            print(f"  [Wake Word] Detection error: {e}")
            return False

        return False

    def cleanup(self):
        """Release resources."""
        self._running = False
        if self._recorder:
            try:
                self._recorder.stop()
            except Exception:
                pass
            self._recorder = None
        if self._porcupine:
            try:
                self._porcupine.delete()
            except Exception:
                pass
            self._porcupine = None


# ---------------------------------------------------------------------------
# SpeechRecognition-based fallback detector
# ---------------------------------------------------------------------------

class SpeechRecognitionDetector:
    """Fallback wake-word detection using SpeechRecognition + Google STT."""

    WAKE_WORDS = ["jarvis", "hey jarvis", "jarvis you there", "jarvis are you there"]

    def __init__(self):
        self._running = False

    def start(self) -> bool:
        """Initialize. Returns True if STT is available."""
        if not _sr_available:
            return False
        self._running = True
        return True

    def wait_for_wake_word(self, on_listening=None) -> bool:
        """
        Continuously listen and check for the wake word.
        Returns True if detected, False if interrupted/error.
        """
        if not _sr_available:
            return False

        recognizer = sr.Recognizer()

        try:
            while self._running:
                try:
                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        if on_listening:
                            on_listening()

                        # Short listening window (2 seconds) to save resources
                        audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)

                    try:
                        text = recognizer.recognize_google(audio).lower().strip()
                        # Check if any wake word variant is in the text
                        for wake_word in self.WAKE_WORDS:
                            if wake_word in text:
                                return True
                    except sr.UnknownValueError:
                        pass  # Didn't catch anything, keep listening
                    except sr.RequestError:
                        time.sleep(1)  # Network issue, wait and retry

                except sr.WaitTimeoutError:
                    continue  # No speech detected in window, keep listening
                except Exception as e:
                    if "stream" in str(e).lower() or "device" in str(e).lower():
                        print(f"  [Wake Word] Microphone error: {e}")
                        return False
                    time.sleep(0.5)

        except KeyboardInterrupt:
            return False

        return False

    def cleanup(self):
        self._running = False


# ---------------------------------------------------------------------------
# Unified detector interface
# ---------------------------------------------------------------------------

class WakeWordDetector:
    """
    Unified wake-word detector. Automatically picks the best available engine.

    Priority:
      1. Porcupine (offline, if access key + library installed)
      2. SpeechRecognition fallback (requires internet)
    """

    def __init__(self, engine: str = "auto"):
        """
        Args:
            engine: "auto" (default), "porcupine", or "sr" (SpeechRecognition fallback)
        """
        self._engine_name = engine
        self._detector = None
        self._running = False

        if engine == "auto":
            self._engine_name = get_wake_word_engine()
        elif engine == "porcupine":
            self._engine_name = "porcupine" if _porcupine_available else "none"
        elif engine in ("sr", "speech_recognition"):
            self._engine_name = "speech_recognition" if _sr_available else "none"

    def start(self) -> bool:
        """Initialize the detector. Returns True if an engine is available."""
        if self._engine_name == "porcupine":
            self._detector = PorcupineDetector()
            if self._detector.start():
                self._running = True
                return True
            # Fall back to SR
            print("  [Wake Word] Porcupine unavailable, falling back to SpeechRecognition.")
            self._engine_name = "speech_recognition" if _sr_available else "none"

        if self._engine_name == "speech_recognition":
            self._detector = SpeechRecognitionDetector()
            if self._detector.start():
                self._running = True
                return True

        print("  [Wake Word] No wake-word engine available.")
        print("    Install: pip install -r requirements-wake.txt")
        print("    Or install voice deps: pip install -r requirements-voice.txt")
        return False

    def wait_for_wake_word(self, on_listening=None) -> bool:
        """Block until wake word detected."""
        if not self._detector:
            return False
        return self._detector.wait_for_wake_word(on_listening=on_listening)

    def cleanup(self):
        """Release resources."""
        self._running = False
        if self._detector:
            self._detector.cleanup()
            self._detector = None

    @property
    def engine_name(self) -> str:
        return self._engine_name

    @property
    def is_running(self) -> bool:
        return self._running
