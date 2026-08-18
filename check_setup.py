import platform, shutil, sys
print("JARVIS setup check")
print("Python:",sys.version.split()[0])
print("Machine:",platform.machine())
print("macOS:",platform.system(),platform.release())
for x in ("open","osascript","say","afplay"):
    print(x, "OK" if shutil.which(x) else "MISSING")
try:
    import speech_recognition; print("SpeechRecognition OK")
except Exception as e: print("SpeechRecognition:",e)
try:
    import pyaudio; print("PyAudio OK")
except Exception as e: print("PyAudio:",e)
try:
    import openwakeword; print("openWakeWord OK")
except Exception as e: print("openWakeWord:",e)
