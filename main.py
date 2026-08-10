import importlib
import subprocess
import time

from importlib import import_module

skills_module = import_module("09_Skills.router")
JarvisSkills = skills_module.JarvisSkills

apps = import_module("09_Skills.apps")

wake_module = importlib.import_module("02_Voice.wake")
JarvisWake = wake_module.JarvisWake

# Brain
brain_module = importlib.import_module("01_Brain.brain")
JarvisBrain = brain_module.JarvisBrain

# Voice
voice_module = importlib.import_module("02_Voice.voice")
JarvisVoice = voice_module.JarvisVoice


brain = JarvisBrain()
voice = JarvisVoice()
skills = JarvisSkills()



print("JARVIS is ready.")


while True:

    # Wait for wake word
    wake = JarvisWake()
    activated = wake.wait_for_wake_word()
    wake.close()

    if not activated:
        continue

    subprocess.run([
    "uv",
    "tool",
    "run",
    "kokoro-tts-tool",
    "synthesize",
    "-v",
    "bm_george",
    "--speed",
    "0.90",
    "Yes, sir?"
])

    while True:
        time.sleep(1.5)

        # Listen for command
        message = voice.listen()

        if not message:
            continue

        # Exit command
        if message.lower() in ["exit", "quit", "shutdown"]:
            print("JARVIS: Shutting down.")
            break

        # App commands
        skill, data = skills.handle(message)
        print("SKILLS:", skill, "DATA:", data)

        if skill == "app":
            if apps.open_app(data):
                subprocess.run([
                    "uv",
                    "tool",
                    "run",
                    "kokoro-tts-tool",
                    "synthesize",
                    "-v",
                    "bm_george",
                    "--speed",
                    "1.0",
                    f"Opening {data}."
                ])

            continue

        # Think
        response = brain.think(message)

        # Print response
        print("JARVIS:", response)

        # Speak response
        subprocess.run([
            "uv",
            "tool",
            "run",
            "kokoro-tts-tool",
            "synthesize",
            "-v",
            "bm_george",
            "--speed",
            "1.0",
            response
        ])