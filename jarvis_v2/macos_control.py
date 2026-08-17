"""
macOS Control Module — System automation via AppleScript and shell commands.
Gives JARVIS the ability to control your Mac: apps, volume, brightness,
dark mode, screenshots, sleep, clipboard, and more.

Requires macOS. All functions check platform and return helpful messages on non-Mac systems.
"""

import os
import platform
import subprocess
import shutil


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == "Darwin"


def _run_applescript(script: str) -> str:
    """Run an AppleScript and return its output."""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return result.stdout.strip()


def _not_macos_msg() -> str:
    return "This command only works on macOS, sir."


# ---------------------------------------------------------------------------
# Application Control
# ---------------------------------------------------------------------------

def open_app(app_name: str) -> str:
    """Open an application by name."""
    if not is_macos():
        return _not_macos_msg()
    try:
        subprocess.Popen(["open", "-a", app_name])
        return f"Opening {app_name}, sir."
    except Exception as e:
        return f"I couldn't open {app_name}: {e}"


def close_app(app_name: str) -> str:
    """Quit an application by name."""
    if not is_macos():
        return _not_macos_msg()
    script = f'tell application "{app_name}" to quit'
    result = _run_applescript(script)
    if "Error" in result:
        # Try via killall as fallback
        try:
            subprocess.run(["killall", app_name], capture_output=True, timeout=5)
            return f"Closed {app_name}, sir."
        except Exception:
            return f"I couldn't close {app_name}: {result}"
    return f"Closed {app_name}, sir."


def list_running_apps() -> str:
    """List all currently running applications."""
    if not is_macos():
        return _not_macos_msg()
    try:
        result = subprocess.run(
            ["ps", "-A"], capture_output=True, text=True, timeout=5
        )
        # Extract app names from /Applications
        apps_dir = "/Applications"
        installed_apps = []
        if os.path.exists(apps_dir):
            for item in os.listdir(apps_dir):
                if item.endswith(".app"):
                    installed_apps.append(item.replace(".app", ""))

        # Check which are running
        running = []
        for app in sorted(installed_apps):
            if app.lower() in result.stdout.lower():
                running.append(app)

        if running:
            return "Currently running applications:\n  " + "\n  ".join(running)
        return "I couldn't detect any running applications, sir."
    except Exception as e:
        return f"Error listing applications: {e}"


# ---------------------------------------------------------------------------
# Volume Control
# ---------------------------------------------------------------------------

def set_volume(level: int) -> str:
    """Set system volume (0-100)."""
    if not is_macos():
        return _not_macos_msg()
    level = max(0, min(100, level))
    script = f'set volume output volume {level}'
    _run_applescript(script)
    return f"Volume set to {level}%, sir."


def get_volume() -> str:
    """Get current system volume."""
    if not is_macos():
        return _not_macos_msg()
    script = 'output volume of (get volume settings)'
    result = _run_applescript(script)
    if result and not result.startswith("Error"):
        return f"Current volume is {result}%, sir."
    return f"Unable to read volume: {result}"


def mute() -> str:
    """Mute the system."""
    if not is_macos():
        return _not_macos_msg()
    _run_applescript('set volume output muted true')
    return "Muted, sir."


def unmute() -> str:
    """Unmute the system."""
    if not is_macos():
        return _not_macos_msg()
    _run_applescript('set volume output muted false')
    return "Unmuted, sir."


# ---------------------------------------------------------------------------
# Brightness Control
# ---------------------------------------------------------------------------

def set_brightness(level: int) -> str:
    """Set screen brightness (0-100). Uses brightness CLI if available, otherwise AppleScript."""
    if not is_macos():
        return _not_macos_msg()
    level = max(0, min(100, level))

    # Try the 'brightness' CLI tool first (if installed via brew)
    if shutil.which("brightness"):
        try:
            brightness_val = level / 100.0
            subprocess.run(["brightness", str(brightness_val)], capture_output=True, timeout=5)
            return f"Brightness set to {level}%, sir."
        except Exception:
            pass

    # Fallback: try via AppleScript (works on some macOS versions)
    return f"Brightness control requires the 'brightness' CLI tool. Install it with: brew install brightness. Then I can set it to {level}%."


# ---------------------------------------------------------------------------
# Appearance / Dark Mode
# ---------------------------------------------------------------------------

def toggle_dark_mode() -> str:
    """Toggle between dark and light mode."""
    if not is_macos():
        return _not_macos_msg()
    script = '''
    tell application "System Events"
        set darkMode to dark mode of appearance preferences
        set dark mode of appearance preferences to not darkMode
    end tell
    '''
    result = _run_applescript(script)
    if "Error" in result:
        return f"I couldn't toggle dark mode: {result}"

    # Check new state
    check = _run_applescript('tell application "System Events" to get dark mode of appearance preferences')
    if check == "true":
        return "Dark mode is now on, sir."
    return "Light mode is now on, sir."


def get_dark_mode() -> str:
    """Check if dark mode is currently enabled."""
    if not is_macos():
        return _not_macos_msg()
    result = _run_applescript('tell application "System Events" to get dark mode of appearance preferences')
    if result == "true":
        return "Dark mode is currently on, sir."
    elif result == "false":
        return "Light mode is currently on, sir."
    return f"Unable to determine dark mode status: {result}"


# ---------------------------------------------------------------------------
# System Power
# ---------------------------------------------------------------------------

def sleep_system() -> str:
    """Put the Mac to sleep."""
    if not is_macos():
        return _not_macos_msg()
    subprocess.Popen(["pmset", "sleepnow"])
    return "Going to sleep, sir. I'll be here when you wake."


def restart_system() -> str:
    """Restart the Mac (requires confirmation)."""
    if not is_macos():
        return _not_macos_msg()
    # This shows a confirmation dialog from macOS
    subprocess.Popen(["osascript", "-e", 'tell application "System Events" to restart'])
    return "Restarting the system, sir."


def lock_screen() -> str:
    """Lock the screen."""
    if not is_macos():
        return _not_macos_msg()
    subprocess.Popen(
        ["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"],
        stderr=subprocess.DEVNULL
    )
    # Fallback method
    subprocess.Popen(["pmset", "displaysleepnow"])
    return "Screen locked, sir."


# ---------------------------------------------------------------------------
# Screenshot
# ---------------------------------------------------------------------------

def take_screenshot() -> str:
    """Take a screenshot and save to Desktop."""
    if not is_macos():
        return _not_macos_msg()
    timestamp = subprocess.run(
        ["date", "+%Y%m%d_%H%M%S"], capture_output=True, text=True
    ).stdout.strip()
    filepath = os.path.expanduser(f"~/Desktop/screenshot_{timestamp}.png")
    subprocess.Popen(["screencapture", filepath])
    return f"Screenshot saved to {filepath}, sir."


# ---------------------------------------------------------------------------
# Clipboard
# ---------------------------------------------------------------------------

def get_clipboard() -> str:
    """Read the current clipboard content."""
    if not is_macos():
        return _not_macos_msg()
    try:
        result = subprocess.run(
            ["pbpaste"], capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            preview = result.stdout.strip()[:200]
            return f"Clipboard content: {preview}"
        return "Clipboard is empty, sir."
    except Exception as e:
        return f"Error reading clipboard: {e}"


def set_clipboard(text: str) -> str:
    """Set the clipboard to the given text."""
    if not is_macos():
        return _not_macos_msg()
    try:
        subprocess.run(["pbcopy"], input=text, text=True, timeout=5)
        return "Text copied to clipboard, sir."
    except Exception as e:
        return f"Error setting clipboard: {e}"


# ---------------------------------------------------------------------------
# Display Info
# ---------------------------------------------------------------------------

def get_battery_status() -> str:
    """Get battery percentage and charging status."""
    if not is_macos():
        return _not_macos_msg()
    try:
        result = subprocess.run(
            ["pmset", "-g", "batt"], capture_output=True, text=True, timeout=5
        )
        output = result.stdout.strip()
        # Parse battery percentage
        for line in output.split("\n"):
            if "Battery" in line or "%" in line:
                if "AC" in line or "charged" in line.lower():
                    return f"Battery: {line.strip()} (plugged in), sir."
                return f"Battery: {line.strip()}, sir."
        return output
    except Exception as e:
        return f"Error reading battery: {e}"


def get_wifi_info() -> str:
    """Get current Wi-Fi network name."""
    if not is_macos():
        return _not_macos_msg()
    try:
        result = subprocess.run(
            ["networksetup", "-getairportnetwork", "en0"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return f"Wi-Fi: {result.stdout.strip()}, sir."
        # Try en1 for some Macs
        result = subprocess.run(
            ["networksetup", "-getairportnetwork", "en1"],
            capture_output=True, text=True, timeout=5
        )
        return f"Wi-Fi: {result.stdout.strip()}, sir."
    except Exception as e:
        return f"Error reading Wi-Fi info: {e}"


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------

def send_notification(title: str, message: str) -> str:
    """Send a macOS notification."""
    if not is_macos():
        return _not_macos_msg()
    script = f'display notification "{message}" with title "{title}"'
    _run_applescript(script)
    return f"Notification sent, sir."


# ---------------------------------------------------------------------------
# Play media (Spotify / Music)
# ---------------------------------------------------------------------------

def play_music() -> str:
    """Play/pause music in the default music app."""
    if not is_macos():
        return _not_macos_msg()
    # Try Spotify first, then Music
    result = _run_applescript('tell application "Spotify" to play')
    if "Error" in result:
        result = _run_applescript('tell application "Music" to play')
        if "Error" in result:
            return "I couldn't find Spotify or Music running, sir."
        return "Playing music, sir."
    return "Playing Spotify, sir."


def pause_music() -> str:
    """Pause music."""
    if not is_macos():
        return _not_macos_msg()
    result = _run_applescript('tell application "Spotify" to pause')
    if "Error" in result:
        result = _run_applescript('tell application "Music" to pause')
        if "Error" in result:
            return "I couldn't find Spotify or Music running, sir."
    return "Music paused, sir."


def next_track() -> str:
    """Skip to next track."""
    if not is_macos():
        return _not_macos_msg()
    result = _run_applescript('tell application "Spotify" to next track')
    if "Error" in result:
        result = _run_applescript('tell application "Music" to next track')
        if "Error" in result:
            return "I couldn't find Spotify or Music running, sir."
    return "Next track, sir."


def previous_track() -> str:
    """Go to previous track."""
    if not is_macos():
        return _not_macos_msg()
    result = _run_applescript('tell application "Spotify" to previous track')
    if "Error" in result:
        result = _run_applescript('tell application "Music" to previous track')
        if "Error" in result:
            return "I couldn't find Spotify or Music running, sir."
    return "Previous track, sir."


# ---------------------------------------------------------------------------
# Empty Trash
# ---------------------------------------------------------------------------

def empty_trash() -> str:
    """Empty the trash."""
    if not is_macos():
        return _not_macos_msg()
    script = '''
    tell application "Finder"
        empty trash
    end tell
    '''
    result = _run_applescript(script)
    if "Error" in result:
        return f"I couldn't empty the trash: {result}"
    return "Trash emptied, sir."


# ---------------------------------------------------------------------------
# Finder / File Reveal
# ---------------------------------------------------------------------------

def reveal_in_finder(path: str) -> str:
    """Reveal a file or folder in Finder."""
    if not is_macos():
        return _not_macos_msg()
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return f"I couldn't find '{path}', sir."
    subprocess.Popen(["open", "-R", expanded])
    return f"Revealing '{path}' in Finder, sir."


def open_folder(path: str) -> str:
    """Open a folder in Finder."""
    if not is_macos():
        return _not_macos_msg()
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return f"I couldn't find '{path}', sir."
    subprocess.Popen(["open", expanded])
    return f"Opening '{path}', sir."


# ---------------------------------------------------------------------------
# Wrapper functions for command routing (extract args from natural language)
# ---------------------------------------------------------------------------

def _extract_app_name(text: str, prefixes: list[str]) -> str:
    """Extract app name from text after one of the prefixes."""
    for prefix in prefixes:
        if prefix in text:
            idx = text.index(prefix) + len(prefix)
            name = text[idx:].strip()
            for word in [" please", " for me", " now"]:
                if name.lower().endswith(word):
                    name = name[:-len(word)].strip()
            return name
    return ""

def close_app_wrapper(text: str) -> str:
    name = _extract_app_name(text, ["close app", "quit app", "close ", "quit "])
    if not name:
        return "Which app would you like me to close?"
    return close_app(name)

def list_running_apps_wrapper(text: str) -> str:
    return list_running_apps()

def set_volume_wrapper(text: str) -> str:
    import re
    match = re.search(r'\d+', text)
    if match:
        return set_volume(int(match.group()))
    return "What volume level? Example: set volume to 50"

def set_brightness_wrapper(text: str) -> str:
    import re
    match = re.search(r'\d+', text)
    if match:
        return set_brightness(int(match.group()))
    return "What brightness level? Example: set brightness to 80"

def reveal_in_finder_wrapper(text: str) -> str:
    for prefix in ["reveal file", "show in finder", "reveal in finder"]:
        if prefix in text:
            path = text.split(prefix, 1)[-1].strip()
            return reveal_in_finder(path)
    return "Which file would you like me to reveal?"

def open_folder_wrapper(text: str) -> str:
    for prefix in ["open folder", "open directory"]:
        if prefix in text:
            path = text.split(prefix, 1)[-1].strip()
            return open_folder(path)
    return "Which folder would you like me to open?"


def open_app_wrapper(text: str) -> str:
    """Wrapper for command routing: open an arbitrary Mac app."""
    # Extract app name after "open " or "launch "
    for prefix in ["open app", "launch app", "open application", "launch application",
                   "open ", "launch "]:
        if prefix in text.lower():
            idx = text.lower().index(prefix) + len(prefix)
            name = text[idx:].strip()
            # Remove common filler words
            for word in [" please", " for me", " now", " app"]:
                if name.lower().endswith(word):
                    name = name[:-len(word)].strip()
            if name and name not in ["youtube", "google", "github", "gmail", "reddit",
                                      "stackoverflow", "twitter", "spotify", "linkedin",
                                      "amazon", "netflix", "chatgpt", "perplexity", "maps",
                                      "apple music", "icloud", "notion", "figma", "vscode",
                                      "http"]:
                return open_app(name)
            break
    return "Which app would you like me to open? Example: open Safari"
