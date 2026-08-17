"""
Command Module — Comprehensive command routing for JARVIS.
Integrates macOS control, file operations, shell execution, system monitoring,
network tools, window management, Git tools, and advanced utilities.

Each command is matched by keyword triggers and routed to the appropriate handler.
"""

import os
import sys
import webbrowser
import platform
from datetime import datetime
from functools import partial

# Import all modules
import macos_control as mac
import file_ops
import shell_executor
import system_monitor
import network_tools
import git_tools
import window_manager
import advanced_tools

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# Helper: wrap a no-argument handler so it accepts (and ignores) text
def _no_arg(func):
    """Wrap a function that takes no args so it can be called with text."""
    return lambda text: func()


# ---------------------------------------------------------------------------
# Basic Commands
# ---------------------------------------------------------------------------

def cmd_time(text: str) -> str:
    now = datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."


def cmd_date(text: str) -> str:
    now = datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')}."


def cmd_open_website(text: str) -> str:
    sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://github.com",
        "gmail": "https://mail.google.com",
        "stackoverflow": "https://stackoverflow.com",
        "reddit": "https://www.reddit.com",
        "twitter": "https://twitter.com",
        "x.com": "https://x.com",
        "spotify": "https://open.spotify.com",
        "linkedin": "https://www.linkedin.com",
        "amazon": "https://www.amazon.com",
        "netflix": "https://www.netflix.com",
        "chatgpt": "https://chat.openai.com",
        "perplexity": "https://www.perplexity.ai",
        "maps": "https://maps.apple.com",
        "apple music": "https://music.apple.com",
        "icloud": "https://www.icloud.com",
        "notion": "https://www.notion.so",
        "figma": "https://www.figma.com",
        "vscode": "https://code.visualstudio.com",
    }

    for name, url in sites.items():
        if name in text:
            webbrowser.open(url)
            return f"Opening {name.capitalize()}, sir."

    words = text.split()
    for word in words:
        if word.startswith("http"):
            webbrowser.open(word)
            return f"Opening {word}, sir."
    return "Which website would you like me to open?"


def cmd_search_web(text: str) -> str:
    query = text
    for prefix in ["search the web for", "search for", "search", "google"]:
        if prefix in query:
            query = query.split(prefix, 1)[-1].strip()
            break
    if not query:
        return "What would you like me to search for?"
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching the web for '{query}', sir."


def cmd_weather(text: str) -> str:
    if not HAS_REQUESTS:
        return "I need the 'requests' library for weather. Install it with: pip install requests"
    location = ""
    for prefix in ["weather in", "weather for", "weather", "temperature in", "temperature"]:
        if prefix in text:
            location = text.split(prefix, 1)[-1].strip()
            break
    if not location:
        location = "Stockholm"
    try:
        response = requests.get(
            f"https://wttr.in/{location}?format=%C+%t+%h+%w",
            timeout=5, headers={"User-Agent": "curl/7.0"},
        )
        if response.status_code == 200:
            return f"Weather in {location.capitalize()}: {response.text.strip()}."
        return f"I couldn't retrieve weather data for {location}."
    except Exception as e:
        return f"Weather service unavailable: {e}"


def cmd_joke(text: str) -> str:
    import random
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs.",
        "There are 10 types of people in the world: those who understand binary and those who don't.",
        "Why did the developer go broke? Because he used up all his cache.",
        "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
        "How many programmers does it take to change a light bulb? None -- that's a hardware problem.",
        "Debugging: being the detective in a crime movie where you are also the murderer.",
        "Why do Java developers wear glasses? Because they don't C#.",
        "What's a programmer's favorite hangout place? The Foo Bar.",
        "I would tell you a UDP joke, but you might not get it.",
        "There's no place like 127.0.0.1.",
    ]
    return random.choice(jokes)


def cmd_help(text: str) -> str:
    return (
        "Here's what I can do, sir:\n"
        "\n== SYSTEM CONTROL ==\n"
        "  Open/close apps — 'open Safari', 'close Chrome', 'quit Spotify'\n"
        "  List running apps — 'list apps', 'running apps'\n"
        "  Volume — 'set volume to 50', 'mute', 'unmute', 'what's the volume'\n"
        "  Brightness — 'set brightness to 80'\n"
        "  Dark mode — 'toggle dark mode', 'dark mode status'\n"
        "  Sleep/lock — 'sleep', 'lock screen', 'restart'\n"
        "  Screenshot — 'take a screenshot'\n"
        "  Empty trash — 'empty trash'\n"
        "  Battery — 'battery status'\n"
        "  Wi-Fi info — 'wi-fi info', 'network info'\n"
        "\n== FILE OPERATIONS ==\n"
        "  Create file — 'create file notes.txt'\n"
        "  Create folder — 'create folder Projects'\n"
        "  Read file — 'read file notes.txt'\n"
        "  List files — 'list files' or 'list files Downloads'\n"
        "  Search files — 'find files *.py'\n"
        "  Delete file — 'delete file old_notes.txt'\n"
        "  File info — 'file info notes.txt'\n"
        "  Reveal in Finder — 'reveal file Downloads'\n"
        "\n== TERMINAL & SHELL ==\n"
        "  Run commands — 'run command ls -la' or just 'ls -la'\n"
        "  Run Python — 'run python print(\"hello\")'\n"
        "  Run script — 'run script my_script.py'\n"
        "\n== SYSTEM MONITORING ==\n"
        "  Full report — 'system report', 'full system status'\n"
        "  Top processes — 'top processes' or 'top processes by memory'\n"
        "  Kill process — 'kill process Safari'\n"
        "  Network connections — 'network connections'\n"
        "\n== NETWORK TOOLS ==\n"
        "  IP address — 'my IP address'\n"
        "  Ping — 'ping google.com'\n"
        "  Speed test — 'speed test'\n"
        "  Port scan — 'scan ports localhost'\n"
        "  DNS lookup — 'dns lookup google.com'\n"
        "\n== WINDOW MANAGEMENT ==\n"
        "  Minimize — 'minimize Safari', 'minimize all'\n"
        "  Fullscreen — 'fullscreen Safari'\n"
        "  Bring to front — 'focus Safari'\n"
        "  Close windows — 'close all windows Safari'\n"
        "  List windows — 'list windows'\n"
        "  Hide app — 'hide Safari', 'hide all others'\n"
        "\n== GIT ==\n"
        "  Git status — 'git status'\n"
        "  Git log — 'git log'\n"
        "  Git branches — 'git branches'\n"
        "  Git info — 'git info'\n"
        "  Git pull — 'git pull'\n"
        "  Git push — 'git push'\n"
        "\n== MUSIC ==\n"
        "  Play/pause — 'play music', 'pause music'\n"
        "  Skip — 'next track', 'previous track'\n"
        "\n== ADVANCED ==\n"
        "  Password gen — 'generate password 20'\n"
        "  Word count — 'count words in hello world'\n"
        "  Base64 — 'base64 encode hello', 'base64 decode aGVsbG8='\n"
        "  Timer — 'set timer for 5 minutes'\n"
        "  Clipboard — 'clipboard history', 'clipboard'\n"
        "  Clear cache — 'clear cache'\n"
        "  Clear screen — 'clear screen'\n"
        "  Mac say — 'say hello world'\n"
        "  Quote — 'inspire me', 'give me a quote'\n"
        "  Dice — 'roll dice' or 'roll 2d20'\n"
        "  Time/date — 'what time is it', 'what's the date'\n"
        "  Weather — 'weather in Stockholm'\n"
        "  Open websites — 'open YouTube', 'open Google'\n"
        "  Web search — 'search for Python tutorials'\n"
        "  Joke — 'tell me a joke'\n"
        "  Exit — 'exit', 'quit', 'goodbye'\n"
        "\n== AI ==\n"
        "  Ask anything — I'll use AI to answer (if API key is set)\n"
        "  Clear AI memory — 'clear conversation'\n"
    )


def cmd_greeting(text: str) -> str:
    import random
    responses = [
        "Hello, sir. How can I assist you?",
        "At your service, sir. What can I do for you?",
        "Good to hear from you, sir. What's on your mind?",
        "Always a pleasure, sir. How may I help?",
        "Yes, sir? I'm listening.",
        "Ready when you are, sir.",
    ]
    return random.choice(responses)


# ---------------------------------------------------------------------------
# Command Registry: (triggers, handler, priority)
# Lower priority number = checked first
# ---------------------------------------------------------------------------

COMMANDS = [
    # Exit
    (["exit", "quit", "goodbye", "shut down", "bye", "see you"], None, 0),

    # Basic
    (["what time", "current time", "time is it", "tell me the time"], cmd_time, 1),
    (["what date", "what day", "what's the date", "today's date", "what is today"], cmd_date, 1),
    (["hello", "hi jarvis", "hey jarvis", "good morning", "good afternoon",
      "good evening", "jarvis you there", "you there jarvis"], cmd_greeting, 1),
    (["joke", "make me laugh", "something funny"], cmd_joke, 1),
    (["help", "what can you do", "commands list", "what do you do", "show commands"], cmd_help, 1),

    # Websites
    (["open youtube", "open google", "open github", "open gmail", "open reddit",
      "open stackoverflow", "open twitter", "open x.com", "open spotify",
      "open linkedin", "open amazon", "open netflix", "open chatgpt",
      "open perplexity", "open maps", "open apple music", "open icloud",
      "open notion", "open figma", "open vscode", "open http"], cmd_open_website, 2),
    (["search for", "search the web", "search ", "google "], cmd_search_web, 2),
    (["weather", "temperature"], cmd_weather, 2),

    # macOS App Control
    (["close app", "quit app", "close safari", "close chrome", "close spotify",
      "close slack", "close vscode", "close code", "close mail",
      "quit safari", "quit chrome", "quit spotify", "quit slack",
      "quit vscode", "quit code", "quit mail", "close firefox",
      "quit firefox", "close terminal", "quit terminal"], mac.close_app_wrapper, 3),
    (["list apps", "running apps", "what apps are running", "running applications"], mac.list_running_apps_wrapper, 3),

    # Volume
    (["set volume", "volume to", "change volume", "volume "], mac.set_volume_wrapper, 3),
    (["unmute"], _no_arg(mac.unmute), 3),
    (["mute"], _no_arg(mac.mute), 3),
    (["what's the volume", "current volume", "get volume"], _no_arg(mac.get_volume), 3),

    # Brightness
    (["set brightness", "brightness to", "change brightness"], mac.set_brightness_wrapper, 3),

    # Dark Mode
    (["toggle dark mode", "switch dark mode", "dark mode toggle"], _no_arg(mac.toggle_dark_mode), 3),
    (["dark mode status", "is dark mode on", "dark mode on"], _no_arg(mac.get_dark_mode), 3),

    # System Power
    (["sleep system", "go to sleep", "sleep now", "put mac to sleep", "sleep"], _no_arg(mac.sleep_system), 3),
    (["lock screen", "lock my mac", "lock the screen", "lock computer"], _no_arg(mac.lock_screen), 3),
    (["restart system", "restart mac", "restart computer", "reboot"], _no_arg(mac.restart_system), 3),

    # Screenshot
    (["take a screenshot", "screenshot", "capture screen", "grab screen"], _no_arg(mac.take_screenshot), 3),

    # Trash
    (["empty trash", "clear trash"], _no_arg(mac.empty_trash), 3),

    # Clipboard
    (["clipboard content", "what's in my clipboard", "show clipboard", "read clipboard"],
     _no_arg(mac.get_clipboard), 3),

    # Battery & Wi-Fi (specific before generic)
    (["battery detail", "detailed battery"], _no_arg(system_monitor.get_battery_detail), 2),
    (["battery status", "battery level", "how much battery", "battery"], _no_arg(mac.get_battery_status), 3),
    (["wi-fi info", "wifi info", "network info", "wi-fi status", "wifi status"],
     _no_arg(mac.get_wifi_info), 3),

    # File Operations
    (["create file", "make file", "new file"], file_ops.create_file, 4),
    (["create folder", "make folder", "new folder", "create directory", "make directory"],
     file_ops.create_folder, 4),
    (["read file", "show file", "cat file", "display file"], file_ops.read_file, 4),
    (["list files", "show files", "list directory", "list folder", "show folder",
      "what's in"], file_ops.list_files, 4),
    (["search for files", "find files", "search files", "find file"], file_ops.search_files, 4),
    (["delete file", "remove file"], file_ops.delete_file, 4),
    (["file info", "info about file", "file details"], file_ops.file_info, 4),
    (["reveal file", "show in finder", "reveal in finder"], mac.reveal_in_finder_wrapper, 4),
    (["open folder", "open directory"], mac.open_folder_wrapper, 4),

    # Generic app opening (after website/folder handlers to not steal them)
    (["open safari", "open chrome", "open firefox", "open terminal", "open mail",
      "open calculator", "open notes", "open calendar", "open messages",
      "open slack", "open discord", "open vscode", "open code", "open xcode",
      "open pages", "open numbers", "open keynote", "open preview",
      "open finder", "open settings", "open system settings",
      "open app ", "launch app ", "open ", "launch "], mac.open_app_wrapper, 4),

    # Shell / Terminal
    (["run command", "run terminal command", "execute command", "terminal command",
      "shell command"], shell_executor.run_command_wrapper, 5),

    # System Monitoring
    (["system report", "full system status", "system status report", "full report"],
     _no_arg(system_monitor.get_full_system_report), 6),
    (["top processes", "process list", "what's using cpu", "what's using memory"],
     system_monitor.get_top_processes_wrapper, 6),
    (["kill process", "kill safari", "kill chrome", "terminate process", "stop process"],
     system_monitor.kill_process, 6),
    (["network connections", "active connections", "show connections"],
     _no_arg(system_monitor.get_network_connections), 6),
    (["battery detail", "detailed battery"], _no_arg(system_monitor.get_battery_detail), 6),

    # Network Tools
    (["my ip", "ip address", "what's my ip", "show ip"], _no_arg(network_tools.get_ip_address), 7),
    (["ping "], network_tools.ping_host_wrapper, 7),
    (["speed test", "internet speed", "connection speed"], _no_arg(network_tools.speed_test), 7),
    (["scan ports", "port scan", "scan "], network_tools.port_scan_wrapper, 7),
    (["dns lookup", "lookup ", "resolve "], network_tools.dns_lookup_wrapper, 7),

    # Window Management
    (["minimize all", "minimize everything"], _no_arg(window_manager.minimize_all), 8),
    (["minimize safari", "minimize chrome", "minimize spotify", "minimize vscode",
      "minimize code", "minimize slack", "minimize "], window_manager.minimize_app_wrapper, 8),
    (["fullscreen safari", "fullscreen chrome", "fullscreen "], window_manager.fullscreen_app_wrapper, 8),
    (["focus safari", "focus chrome", "bring to front", "focus "], window_manager.bring_to_front_wrapper, 8),
    (["close all windows", "close windows"], window_manager.close_all_windows_wrapper, 8),
    (["list windows", "show windows", "visible windows"], _no_arg(window_manager.get_window_list), 8),
    (["hide safari", "hide chrome", "hide spotify", "hide "], window_manager.hide_app_wrapper, 8),
    (["hide all others", "hide other apps"], _no_arg(window_manager.hide_all_others), 8),

    # Git
    (["git status", "repository status", "repo status"], git_tools.git_status, 9),
    (["git log", "recent commits", "commit history"], git_tools.git_log_wrapper, 9),
    (["git branches", "list branches", "show branches"], git_tools.git_branches_wrapper, 9),
    (["git info", "repo info", "repository info"], git_tools.git_info_wrapper, 9),
    (["git pull", "pull latest"], git_tools.git_pull_wrapper, 9),
    (["git push", "push changes"], git_tools.git_push_wrapper, 9),

    # Music
    (["play music", "play spotify", "resume music"], _no_arg(mac.play_music), 10),
    (["pause music", "pause spotify", "stop music"], _no_arg(mac.pause_music), 10),
    (["next track", "skip song", "next song"], _no_arg(mac.next_track), 10),
    (["previous track", "previous song", "go back"], _no_arg(mac.previous_track), 10),

    # Advanced Tools
    (["generate password", "create password", "new password", "password generator"],
     advanced_tools.generate_password, 11),
    (["count words in", "word count", "count characters"], advanced_tools.count_words, 11),
    (["base64 encode", "encode base64"], advanced_tools.base64_encode, 11),
    (["base64 decode", "decode base64"], advanced_tools.base64_decode, 11),
    (["set timer", "timer for", "set a timer"], advanced_tools.set_timer, 11),
    (["clear clipboard history"], _no_arg(advanced_tools.clear_clipboard_history), 11),
    (["clipboard history", "clipboard log"], _no_arg(advanced_tools.get_clipboard_history), 11),
    (["clear cache", "flush cache", "clear system cache"], _no_arg(advanced_tools.clear_cache), 11),
    (["clear screen", "clear terminal", "cls"], _no_arg(advanced_tools.clear_terminal), 11),
    (["say "], advanced_tools.say_text, 11),
    (["inspire me", "give me a quote", "random quote", "quote"], _no_arg(advanced_tools.get_quote), 11),
    (["roll dice", "roll a die", "dice roll", "roll "], advanced_tools.roll_dice_wrapper, 11),

    # Python execution
    (["run python", "execute python", "python code", "python:"], advanced_tools.execute_python, 12),
    (["run script", "run python file", "execute script"], advanced_tools.execute_python_file, 12),
]


def match_command(text: str):
    """
    Try to match user input to a command.
    Returns (handler, is_exit) tuple.
    handler is None if no match found.
    is_exit is True if the user wants to quit.
    """
    text_clean = text.strip()
    text_lower = text_clean.lower()

    # Match registered commands FIRST (before shell detection)
    for triggers, handler, priority in COMMANDS:
        for trigger in triggers:
            if trigger in text_lower:
                if handler is None:
                    return (None, True)  # Exit command
                # Pass original text (preserve case) to handler
                return (partial(handler, text_clean), False)

    # If no registered command matched, try shell command detection
    shell_cmd = shell_executor.extract_command(text_clean)
    if shell_cmd:
        return (partial(shell_executor.run_command_wrapper, shell_cmd), False)

    return (None, False)  # No match
