import importlib
import subprocess
import time

from importlib import import_module


# ============================================================
# SKILLS
# ============================================================

skills_module = import_module("09_Skills.router")
JarvisSkills = skills_module.JarvisSkills

apps = import_module("09_Skills.apps")
browser = import_module("09_Skills.browser")


# ============================================================
# WAKE WORD
# ============================================================

wake_module = importlib.import_module("02_Voice.wake")
JarvisWake = wake_module.JarvisWake


# ============================================================
# BRAIN
# ============================================================

brain_module = importlib.import_module("01_Brain.brain")
JarvisBrain = brain_module.JarvisBrain


# ============================================================
# VOICE
# ============================================================

voice_module = importlib.import_module("02_Voice.voice")
JarvisVoice = voice_module.JarvisVoice


# ------------------------------------------------------------
# VOICE OUTPUT (TTS)
# ------------------------------------------------------------
# JARVIS supports two voice backends (see 08_Configuration/voices.json):
#   - kokoro     : the original local JARVIS voice ("bm_george")
#   - elevenlabs : the winning Jarvis voice (Paul-Bettany-like,
#                  voice_id xbpwjFFJpcRThvL5EyVi)
# The ElevenLabs voice is used when ELEVENLABS_API_KEY is set; otherwise
# JARVIS falls back to the local Kokoro voice automatically. The old voice
# is always kept as a fallback.
# ------------------------------------------------------------

_tts_module = importlib.import_module("02_Voice.tts")
_tts_speak = _tts_module.speak


# ============================================================
# MEMORY
# ============================================================

memory_module = importlib.import_module("03_Memory.memory")
Memory = memory_module.Memory


# ============================================================
# CREATE JARVIS COMPONENTS
# ============================================================

brain = JarvisBrain()
voice = JarvisVoice()
skills = JarvisSkills()
memory = Memory()


print("JARVIS is ready.")


# ============================================================
# HELPER: JARVIS SPEAK
# ============================================================

def speak(response, speed="1.0"):

    print("JARVIS:", response)

    _tts_speak(response, speed)


# ============================================================
# MAIN JARVIS LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # WAIT FOR WAKE WORD
    # --------------------------------------------------------

    wake = JarvisWake()

    activated = wake.wait_for_wake_word()

    wake.close()

    if not activated:
        continue


    # --------------------------------------------------------
    # JARVIS ACTIVATED
    # --------------------------------------------------------

    speak("Yes, sir?", speed="0.90")


    # --------------------------------------------------------
    # COMMAND LOOP
    # --------------------------------------------------------

    while True:

        time.sleep(1.5)

        message = voice.listen()

        if not message:
            continue


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if message.lower() in ["exit", "quit", "shutdown"]:

            speak("Shutting down.")

            break


        print("COMMAND:", message)


        # ----------------------------------------------------
        # MEMORY: REMEMBER
        # ----------------------------------------------------

        if message.lower().startswith("remember that "):

            memory_text = message[14:].strip()

            if " is " in memory_text:

                key, value = memory_text.split(" is ", 1)

                key = key.strip()
                value = value.strip()

                memory.remember(key, value)

                speak(
                    f"I'll remember that {key} is {value}."
                )

                continue


        # ----------------------------------------------------
        # MEMORY: RECALL
        # ----------------------------------------------------

        recall_phrases = [
            "what is my ",
            "what's my ",
            "do you remember my ",
            "tell me my ",
            "what do you remember about my "
        ]

        memory_handled = False


        for phrase in recall_phrases:

            if message.lower().strip().startswith(
                phrase.strip()
            ):

                key = message[len(phrase):].strip().rstrip("?")

                key = "my " + key

                value = memory.recall(key)


                if value:

                    response = (
                        f"Your {key[3:]} is {value}."
                    )

                else:

                    response = (
                        f"I don't remember your {key[3:]}."
                    )


                speak(response)

                memory_handled = True

                break


        if memory_handled:
            continue


        # ----------------------------------------------------
        # OLD SKILLS ROUTER
        #
        # We keep this as a fallback.
        # ----------------------------------------------------

        skill, data = skills.handle(message)


        # ----------------------------------------------------
        # AI COMMAND UNDERSTANDING
        # ----------------------------------------------------

        try:

            command = brain.understand_command(message)

            intent = command.get("intent")
            target = command.get("target")

            print(
                "COMMAND INTENT:",
                intent,
                "TARGET:",
                target
            )

        except Exception as error:

            print(
                "COMMAND PARSER ERROR:",
                error
            )

            intent = None
            target = None


        # ----------------------------------------------------
        # FALLBACK TO OLD ROUTER
        # ----------------------------------------------------

        if intent == "question" and skill is not None:

            intent = None
            target = None


        # ====================================================
        # OPEN WEBSITE
        # ====================================================

        if intent == "open_website":

            if target:

                if browser.open_browser(target):

                    speak(f"Opening {target}.")

                else:

                    speak(
                        f"I couldn't open {target}."
                    )

            else:

                speak("Which website would you like me to open?")

            continue


        # ====================================================
        # OPEN APP
        # ====================================================

        if intent == "open_app":

            if target:

                if apps.open_app(target):

                    speak(f"Opening {target}.")

                else:

                    speak(
                        f"I couldn't open {target}."
                    )

            else:

                speak(
                    "Which application would you like me to open?"
                )

            continue


        # ====================================================
        # SEARCH WEB
        # ====================================================

        if intent == "search_web":

            if target:

                if browser.search_web(target):

                    speak(
                        f"Searching Google for {target}."
                    )

                else:

                    speak(
                        "I couldn't search the web."
                    )

            else:

                speak(
                    "What would you like me to search for?"
                )

            continue


        # ====================================================
        # CLOSE APP
        # ====================================================

        if intent == "close_app":

            if target:

                if apps.close_app(target):

                    speak("Okay.")

                else:

                    speak(
                        f"I couldn't close {target}."
                    )

            else:

                speak(
                    "Which application would you like me to close?"
                )

            continue


        # ====================================================
        # OLD ROUTER FALLBACK
        # ====================================================

        if skill == "browser_open":

            if browser.open_browser(data):

                speak(f"Opening {data}.")

            else:

                speak(
                    f"I couldn't open {data}."
                )

            continue


        if skill == "app":

            if apps.open_app(data):

                speak(f"Opening {data}.")

            else:

                speak(
                    f"I couldn't open {data}."
                )

            continue


        if skill == "browser_search":

            if browser.search_web(data):

                speak(
                    f"Searching Google for {data}."
                )

            else:

                speak(
                    "I couldn't search the web."
                )

            continue


        if skill == "close_app":

            if apps.close_app(data):

                speak("Okay.")

            else:

                speak(
                    f"I couldn't close {data}."
                )

            continue


        if skill == "app_help":

            speak(
                "Which application would you like me to open?"
            )

            continue


        # ====================================================
        # NORMAL QUESTION → OLLAMA
        # ====================================================

        if intent == "question" and target:

            response = brain.think(target)

            speak(response)

            continue


        # ====================================================
        # FINAL FALLBACK → OLLAMA
        # ====================================================

        response = brain.think(message)

        speak(response)