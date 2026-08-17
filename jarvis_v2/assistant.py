"""
Assistant core - The main interaction loop for JARVIS.
Handles input (voice or text), routes to commands or LLM, and speaks responses.
Includes proactive system monitoring and AI-powered command interpretation.
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


class JarvisAssistant:
    """The core JARVIS assistant that ties everything together."""

    def __init__(self, voice_input: bool = False, voice_output: bool = True,
                 proactive: bool = True):
        """
        Initialize JARVIS.

        Args:
            voice_input: If True, listen for voice commands. Falls back to text if unavailable.
            voice_output: If True, speak responses aloud. Falls back to text if unavailable.
            proactive: If True, monitor system health and clipboard in the background.
        """
        self.voice_input = voice_input and is_voice_input_available()
        self.voice_output = voice_output and is_voice_output_available()
        self.running = False
        self.proactive = proactive
        self._last_alert_time = 0

    def _print_banner(self):
        """Print the startup banner."""
        mode_parts = []
        mode_parts.append("VOICE IN" if self.voice_input else "TEXT IN")
        mode_parts.append("VOICE OUT" if self.voice_output else "TEXT OUT")

        banner = """
================================================================
     J  A  R  V  I  S   A  S  S  I  S  T  A  N  T
            Just A Rather Very Intelligent
                 System  v2.0.0
================================================================
        """
        print(banner)
        print(f"  Mode: {' + '.join(mode_parts)}")
        print(f"  AI: {get_model_info()}")
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
            text = listen(timeout=5, phrase_limit=10)
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
                # Try to execute the interpreted command
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
                time.sleep(60)  # Check every minute

                # Check system alerts
                alert = monitor_alerts()
                if alert and time.time() - self._last_alert_time > 300:  # Max once per 5 min
                    speak(alert, voice=self.voice_output)
                    self._last_alert_time = time.time()

                # Track clipboard
                track_clipboard()

            except Exception:
                pass

    def run(self):
        """Main loop — start JARVIS and keep listening until exit."""
        self._print_banner()
        self.running = True

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
