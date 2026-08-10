import pyaudio
import numpy as np
from openwakeword.model import Model


class JarvisWake:
    def __init__(self):
        self.model = Model(
        wakeword_models=["hey_jarvis"],
        inference_framework="tflite"
        )

        self.audio = pyaudio.PyAudio()

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1280
        )

    def wait_for_wake_word(self):
        print("JARVIS is listening for wake word...")

        while True:
            data = self.stream.read(
                1280,
                exception_on_overflow=False
            )

            audio_data = np.frombuffer(
                data,
                dtype=np.int16
            )

            prediction = self.model.predict(audio_data)

            score = prediction.get("hey_jarvis", 0)

            if score > 0.5:
                print("JARVIS ACTIVATED!")
                return True

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()