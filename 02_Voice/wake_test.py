import pyaudio
import numpy as np
from openwakeword.model import Model

model = Model(
wakeword_models=["hey_jarvis"],
inference_framework="tflite"
)

audio = pyaudio.PyAudio()

stream = audio.open(
format=pyaudio.paInt16,
channels=1,
rate=16000,
input=True,
frames_per_buffer=1280
)

print("Wake-word detector is ready.")
print('Say "Hey JARVIS"...')

try:
    while True:
        data = stream.read(1280, exception_on_overflow=False)

        audio_data = np.frombuffer(
        data,
        dtype=np.int16
        )

        prediction = model.predict(audio_data)

        score = prediction.get("hey_jarvis", 0)

        if score > 0.5:
            print("JARVIS ACTIVATED!")
            break

finally:
    stream.stop_stream()    
    stream.close()
    audio.terminate()