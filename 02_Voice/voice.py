import speech_recognition as sr
import subprocess 


class JarvisVoice:

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.0
        self.recognizer.non_speaking_duration = 0.5
        self.microphone = sr.Microphone()

    def wait_for_wake_word(self):
        with self.microphone as source:
            print("JARVIS is waiting...")

            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=0.3
            )

            try:
                audio = self.recognizer.listen(
                    source,
                    phrase_time_limit=3
                )

                text = self.recognizer.recognize_google(audio)

                print("Heard:", text)

                if "jarvis" in text.lower():
                    return True

            except sr.UnknownValueError:
                pass

            except sr.RequestError as error:
                print("JARVIS: Speech recognition error:", error)

        return False

    def listen(self):
        with self.microphone as source:
            print("JARVIS is listening...")

            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=0.3
            )

            audio = self.recognizer.listen(
                source,
                phrase_time_limit=8
            )

        try:
            text = self.recognizer.recognize_google(audio)

            print("You:", text)

            return text

        except sr.UnknownValueError:
            print("JARVIS: I didn't catch that.")
            return ""

        except sr.RequestError as error:
            print("JARVIS: Speech recognition error:", error)
            return ""

    def speak(self, text):
        subprocess.run(["say", text])