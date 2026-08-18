from __future__ import annotations
import os
try:
    from openwakeword.model import Model
except Exception:
    Model = None
import numpy as np

class JarvisWake:
    """Wake engine. Uses openWakeWord when available; otherwise speech-recognition fallback."""
    def __init__(self):
        self.model=None
        self.audio=None
        self.stream=None
        self.ready=False
        if Model is not None and os.getenv("JARVIS_WAKE_ENGINE","auto") != "speech":
            try:
                self.model=Model(wakeword_models=["hey_jarvis"], inference_framework="tflite")
                import pyaudio
                self.audio=pyaudio.PyAudio()
                self.stream=self.audio.open(format=pyaudio.paInt16,channels=1,rate=16000,input=True,frames_per_buffer=1280)
                self.ready=True
            except Exception as e:
                print("JARVIS: local wake engine unavailable; using speech fallback:", e)
                self.close()

    def wait_for_wake_word(self, voice=None):
        if self.ready:
            while True:
                data=self.stream.read(1280, exception_on_overflow=False)
                pred=self.model.predict(np.frombuffer(data,dtype=np.int16))
                if pred.get("hey_jarvis",0) >= float(os.getenv("JARVIS_WAKE_THRESHOLD","0.5")):
                    return True
        if voice:
            return voice.listen_for_wake()[0]
        return False

    def close(self):
        try:
            if self.stream: self.stream.stop_stream(); self.stream.close()
            if self.audio: self.audio.terminate()
        except Exception: pass
        self.stream=None; self.audio=None; self.ready=False
