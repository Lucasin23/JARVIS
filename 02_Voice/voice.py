import speech_recognition as sr
import subprocess
import time


class JarvisVoice:

    def __init__(self):
        self.recognizer = sr.Recognizer()

        # Voice detection settings
        self.recognizer.pause_threshold = 0.8
        self.recognizer.non_speaking_duration = 0.4

        # Don't wait forever for speech
        self.recognizer.phrase_threshold = 0.3

        self.microphone = sr.Microphone()

        # Calibrate microphone once when JARVIS starts
        with self.microphone as source:
            print("JARVIS: Calibrating microphone...")
            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

        print("JARVIS: Microphone ready.")


    # -----------------------------------------
    # WAKE WORD
    # -----------------------------------------

    def wait_for_wake_word(self):

        with self.microphone as source:

            print("JARVIS is waiting...")

            try:

                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=3
                )

                text = self.recognizer.recognize_google(
                    audio,
                    language="en-US"
                )

                print("Heard:", text)

                if "jarvis" in text.lower():
                    return True

            except sr.WaitTimeoutError:
                pass

            except sr.UnknownValueError:
                pass

            except sr.RequestError as error:

                print(
                    "JARVIS: Speech recognition unavailable."
                )

                print(
                    "JARVIS: Check your internet connection."
                )

                time.sleep(1)

        return False


    # -----------------------------------------
    # COMMAND LISTENING
    # -----------------------------------------

    def listen(self):

        with self.microphone as source:

            print("JARVIS is listening...")

            try:

                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=8
                )

            except sr.WaitTimeoutError:

                print("JARVIS: No speech detected.")
                return ""

        try:

            text = self.recognizer.recognize_google(
                audio,
                language="en-US"
            )

            print("You:", text)

            return text

        except sr.UnknownValueError:

            print("JARVIS: I didn't catch that.")
            return ""

        except sr.RequestError:

            print(
                "JARVIS: Speech recognition unavailable."
            )

            print(
                "JARVIS: Please check your internet connection."
            )

            return ""


    # -----------------------------------------
    # SPEAK
    # -----------------------------------------

    def speak(self, text):

        subprocess.run([
            "say",
            text
        ])