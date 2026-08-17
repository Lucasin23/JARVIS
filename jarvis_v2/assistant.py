"""
Assistant core - The main interaction loop for JARVIS.
Handles input (voice or text), routes to commands or LLM, and speaks responses.
Includes proactive system monitoring, AI-powered command interpretation,
and optional wake-word ("Hey JARVIS") hands-free activation.
"""

import time
import threading
from speech import (
    speak, listen,
    is_voice_input_available, is_voice_output_available,
)
from commands import match_command
from llm import ask_llm, is_llm_available, get_model_info, clear_history, interpret_command
from system_monitor import monitor_alerts
from advanced_tools import track_clipboard


# Commands that require typed confirmation in wake-word mode
# (voice-activated destructive actions are dangerous)
DESTRUCTIVE_TRIGGERS = [
    "rm ", "rmdir", "mv ", "chmod", "chown",
    "kill ", "killall", "pkill",
    "git push", "git reset", "git clean",
    "defaults write", "defaults delete",
    "delete file", "empty trash", "restart",
]


def _is_destructive_command(text: str) -> bool:
    """Check if a command is destructive and should require confirmation."""
    text_lower = text.lower().strip()
    for trigger in DESTRUCTIVE_TRIGGERS:
        if trigger in text_lower:
            return True
    return False


class JarvisAssistant:
    """The core JARVIS assistant that ties everything together."""

    def __init__(self, voice_input: bool = False, voice_output: bool = True,
                 proactive: bool = True, wake_word: bool = False):
        """
        Initialize JARVIS.

        Args:
            voice_input: If True, listen for voice commands. Falls back to text if unavailable.
            voice_output: If True, speak responses aloud. Falls back to text if unavailable.
            proactive: If True, monitor system health and clipboard in the background.
            wake_word: If True, activate wake-word mode ("Hey JARVIS" hands-free).
        """
        self.voice_input = voice_input and is_voice_input_available()
        self.voice_output = voice_output and is_voice_output_available()
        self.wake_word = wake_word
        self.running = False
        self.proactive = proactive
        self._last_alert_time = 0
        self._wake_detector = None

        # Wake-word mode requires voice input capability
        if self.wake_word and not self.voice_input:
            print("\n  [!] Wake-word mode requires voice input capability.")
            print("      Install: pip install -r requirements-voice.txt")
            print("      Disabling wake-word mode.\n")
            self.wake_word = False

    def _print_banner(self):
        """Print the startup banner."""
        mode_parts = []
        if self.wake_word:
            mode_parts.append("WAKE WORD")
        mode_parts.append("VOICE IN" if self.voice_input else "TEXT IN")
        mode_parts.append("VOICE OUT" if self.voice_output else "TEXT OUT")

        banner = """
================================================================
     J  A  R  V  I  S   A  S  S  I  S  T  A  N  T
            Just A Rather Very Intelligent
                 System  v2.1.0
================================================================
        """
        print(banner)
        print(f"  Mode: {' + '.join(mode_parts)}")
        print(f"  AI: {get_model_info()}")

        if self.wake_word:
            from wake_word import get_wake_word_engine
            engine = get_wake_word_engine()
            print(f"  Wake-word engine: {engine}")
            if engine == "porcupine":
                print("  Say \"Hey JARVIS\" to activate.")
            elif engine == "speech_recognition":
                print("  Say \"JARVIS\" to activate (fallback STT mode).")
            else:
                print("  [!] No wake-word engine available. Install:")
                print("      pip install -r requirements-wake.txt")
                self.wake_word = False

        if not is_llm_available():
            print("  Note: AI responses disabled. Type 'help' for built-in commands.")
        if self.proactive:
            print("  Proactive monitoring: ON")
        print("  Type 'help' to see available commands.")
        print("  Type 'exit' or say 'goodbye' to quit.\n")

    def _get_input(self) -> str:
        """Get input from voice or text, depending on mode."""
        if self.voice_input:
            print("\n[Listening]...")
            text = listen(timeout=8, phrase_limit=15)
            if text:
                print(f"  You said: {text}")
                return text
            print("  (Voice input failed. Type your command instead.)")

        try:
            user_input = input("\nYou: ").strip()
            return user_input
        except (EOFError, KeyboardInterrupt):
            return "exit"

    def _process_command(self, user_input: str) -> bool:
        """
        Process user input and generate a response.
        Returns True if the assistant should continue, False if it should exit.
        """
        if not user_input:
            return True

        # Check for clear conversation command
        if "clear conversation" in user_input.lower() or "clear ai memory" in user_input.lower():
            clear_history()
            speak("Conversation history cleared, sir.", voice=self.voice_output)
            return True

        # In wake-word mode, require typed confirmation for destructive commands
        if self.wake_word and _is_destructive_command(user_input):
            speak(
                "That command could be destructive, sir. "
                "In wake-word mode, I require typed confirmation. "
                "Please type 'yes' to confirm, or anything else to cancel.",
                voice=self.voice_output
            )
            try:
                confirmation = input("\nConfirm [yes/no]: ").strip().lower()
                if confirmation not in ("yes", "y"):
                    speak("Cancelled, sir.", voice=self.voice_output)
                    return True
            except (EOFError, KeyboardInterrupt):
                speak("Cancelled, sir.", voice=self.voice_output)
                return True

        # Match to a built-in command
        handler, is_exit = match_command(user_input)

        if is_exit:
            speak("Goodbye, sir. I'll be here if you need me.", voice=self.voice_output)
            return False

        if handler is not None:
            try:
                response = handler()
                if response:
                    speak(response, voice=self.voice_output)
            except Exception as e:
                speak(f"Error executing command: {e}", voice=self.voice_output)
            return True

        # No built-in command matched — try AI command interpretation first
        if is_llm_available():
            interpreted = interpret_command(user_input)
            if interpreted and interpreted.get("action") and interpreted["action"] != "none":
                response = self._execute_interpreted(interpreted)
                if response:
                    speak(response, voice=self.voice_output)
                    return True

        # Fall back to conversational LLM response
        response = ask_llm(user_input)
        speak(response, voice=self.voice_output)
        return True

    def _execute_interpreted(self, interpretation: dict) -> str | None:
        """Execute a command interpreted by the LLM."""
        action = interpretation.get("action", "")
        args = interpretation.get("args", "")

        try:
            if action == "open_app":
                import macos_control as mac
                return mac.open_app(args)
            elif action == "close_app":
                import macos_control as mac
                return mac.close_app(args)
            elif action == "set_volume":
                import macos_control as mac
                return mac.set_volume(int(args))
            elif action == "set_brightness":
                import macos_control as mac
                return mac.set_brightness(int(args))
            elif action == "toggle_dark_mode":
                import macos_control as mac
                return mac.toggle_dark_mode()
            elif action == "sleep":
                import macos_control as mac
                return mac.sleep_system()
            elif action == "lock_screen":
                import macos_control as mac
                return mac.lock_screen()
            elif action == "screenshot":
                import macos_control as mac
                return mac.take_screenshot()
            elif action == "run_shell":
                import shell_executor
                result = shell_executor.run_command(args)
                return shell_executor.format_command_result(result, args)
            elif action == "search_web":
                import webbrowser
                webbrowser.open(f"https://www.google.com/search?q={args.replace(' ', '+')}")
                return f"Searching for '{args}', sir."
            elif action == "open_website":
                import webbrowser
                webbrowser.open(args if args.startswith("http") else f"https://{args}")
                return f"Opening {args}, sir."
            elif action == "weather":
                import requests
                r = requests.get(f"https://wttr.in/{args}?format=%C+%t+%h+%w",
                                 timeout=5, headers={"User-Agent": "curl/7.0"})
                if r.status_code == 200:
                    return f"Weather in {args}: {r.text.strip()}."
                return f"Couldn't get weather for {args}."
            elif action == "play_music":
                import macos_control as mac
                return mac.play_music()
            elif action == "pause_music":
                import macos_control as mac
                return mac.pause_music()
        except Exception as e:
            return f"I tried to {action} but encountered an error: {e}"

        return None

    def _proactive_monitor(self):
        """Background thread for proactive system monitoring."""
        while self.running:
            try:
                time.sleep(60)
                alert = monitor_alerts()
                if alert and time.time() - self._last_alert_time > 300:
                    speak(alert, voice=self.voice_output)
                    self._last_alert_time = time.time()
                track_clipboard()
            except Exception:
                pass

    def _run_wake_word_mode(self):
        """Run in wake-word mode: wait for wake word, then listen for a command."""
        from wake_word import WakeWordDetector

        self._wake_detector = WakeWordDetector(engine="auto")

        if not self._wake_detector.start():
            print("\n  [!] Failed to start wake-word detection.")
            print("      Falling back to normal voice mode.\n")
            self.wake_word = False
            self.run()
            return

        self.running = True

        # Start proactive monitoring
        if self.proactive:
            monitor_thread = threading.Thread(target=self._proactive_monitor, daemon=True)
            monitor_thread.start()

        speak("Wake-word mode active. Say \"Hey JARVIS\" when you need me, sir.",
              voice=self.voice_output)

        last_print = 0

        while self.running:
            # Periodic "listening" indicator
            def on_listening():
                nonlocal last_print
                now = time.time()
                if now - last_print > 10:
                    print(f"\n  [Wake] Listening for \"Hey JARVIS\"... (engine: {self._wake_detector.engine_name})")
                    last_print = now

            print(f"\n  [Wake] Listening for \"Hey JARVIS\"... (engine: {self._wake_detector.engine_name})")
            last_print = time.time()

            # Block until wake word detected
            detected = self._wake_detector.wait_for_wake_word(on_listening=on_listening)

            if not detected:
                if not self.running:
                    break
                continue

            # Wake word detected!
            print("\n  [Wake] Wake word detected!")
            speak("Yes, sir?", voice=self.voice_output)

            # Listen for the actual command
            print("  [Wake] Listening for command...")
            command_text = listen(timeout=10, phrase_limit=15)

            if command_text:
                print(f"  You said: {command_text}")
                should_continue = self._process_command(command_text)
                if not should_continue:
                    self.running = False
                    break
            else:
                speak("I didn't catch that, sir. Say \"Hey JARVIS\" again when you're ready.",
                      voice=self.voice_output)

        # Cleanup
        if self._wake_detector:
            self._wake_detector.cleanup()
            self._wake_detector = None

    def run(self):
        """Main loop — start JARVIS and keep listening until exit."""
        self._print_banner()
        self.running = True

        # Wake-word mode has its own loop
        if self.wake_word:
            self._run_wake_word_mode()
            return

        # Start proactive monitoring thread
        if self.proactive:
            monitor_thread = threading.Thread(target=self._proactive_monitor, daemon=True)
            monitor_thread.start()

        # Greet the user
        hour = time.localtime().tm_hour
        if hour < 12:
            greeting = "Good morning, sir. JARVIS is online and at your service."
        elif hour < 18:
            greeting = "Good afternoon, sir. JARVIS is online and ready."
        else:
            greeting = "Good evening, sir. JARVIS is online and standing by."
        speak(greeting, voice=self.voice_output)

        # Main interaction loop
        while self.running:
            try:
                user_input = self._get_input()
                should_continue = self._process_command(user_input)
                if not should_continue:
                    self.running = False
            except KeyboardInterrupt:
                speak("\nShutting down. Goodbye, sir.", voice=self.voice_output)
                self.running = False
            except Exception as e:
                speak(f"An error occurred: {e}", voice=self.voice_output)

    def stop(self):
        """Stop the assistant."""
        self.running = False
        if self._wake_detector:
            self._wake_detector.cleanup()
