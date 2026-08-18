from __future__ import annotations
import os, subprocess, time
try:
    import speech_recognition as sr
except Exception:
    sr = None

class JarvisVoice:
    def __init__(self):
        self.enabled = sr is not None
        self.recognizer = sr.Recognizer() if self.enabled else None
        self.microphone = sr.Microphone() if self.enabled else None
        if self.enabled:
            self.recognizer.pause_threshold = 0.7
            self.recognizer.phrase_threshold = 0.25
            try:
                with self.microphone as source:
                    print("JARVIS: calibrating microphone...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            except Exception as e:
                print("JARVIS microphone:", e)

    def listen(self, timeout=6, phrase_time_limit=10):
        if not self.enabled:
            return input("YOU > ").strip()
        try:
            with self.microphone as source:
                audio=self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text=self.recognizer.recognize_google(audio, language=os.getenv("JARVIS_LANGUAGE","en-US"))
            print("YOU >", text)
            return text
        except Exception:
            return ""

    def listen_for_wake(self):
        text=self.listen(timeout=5, phrase_time_limit=4)
        return "jarvis" in text.lower(), text
