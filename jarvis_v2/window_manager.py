"""
Window Manager Module — macOS window management via AppleScript.
Control window positions, minimize, fullscreen, and arrangement.
"""

import platform
import subprocess


def is_macos() -> bool:
    return platform.system() == "Darwin"


def _run_applescript(script: str) -> str:
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return result.stdout.strip()


def minimize_app(app_name: str) -> str:
    """Minimize all windows of an application."""
    if not is_macos():
        return "Window management is only available on macOS, sir."
    script = f'''
    tell application "System Events"
        tell process "{app_name}"
            set frontmost to true
            click (1st button whose description is "minimize button") of (1st window)
        end tell
    end tell
    '''
    result = _run_applescript(script)
    if "Error" in result:
        # Fallback: use cmd+M
        script2 = f'''
        tell application "{app_name}" to activate
        delay 0.3
        tell application "System Events" to keystroke "m" using command down
        '''
        _run_applescript(script2)
        return f"Minimized {app_name}, sir."
    return f"Minimized {app_name}, sir."


def minimize_all() -> str:
    """Minimize all windows (cmd+option+M)."""
    if not is_macos():
        return "Only available on macOS, sir."
    script = '''
    tell application "System Events"
        keystroke "m" using {command down, option down}
    end tell
    '''
    _run_applescript(script)
    return "Minimized all windows, sir."


def fullscreen_app(app_name: str) -> str:
    """Toggle fullscreen for an app."""
    if not is_macos():
        return "Only available on macOS, sir."
    script = f'''
    tell application "{app_name}" to activate
    delay 0.3
    tell application "System Events"
        keystroke "f" using {{command down, control down}}
    end tell
    '''
    _run_applescript(script)
    return f"Toggled fullscreen for {app_name}, sir."


def bring_to_front(app_name: str) -> str:
    """Bring an application to the front."""
    if not is_macos():
        return "Only available on macOS, sir."
    script = f'''
    tell application "{app_name}" to activate
    '''
    _run_applescript(script)
    return f"Brought {app_name} to front, sir."


def close_all_windows(app_name: str) -> str:
    """Close all windows of an application."""
    if not is_macos():
        return "Only available on macOS, sir."
    script = f'''
    tell application "{app_name}"
        close every window
    end tell
    '''
    result = _run_applescript(script)
    if "Error" in result:
        # Fallback: cmd+option+W
        script2 = f'''
        tell application "{app_name}" to activate
        delay 0.3
        tell application "System Events" to keystroke "w" using {{command down, option down}}
        '''
        _run_applescript(script2)
    return f"Closed all windows of {app_name}, sir."


def split_screen_left(app_name: str) -> str:
    """Tile window to left half of screen."""
    if not is_macos():
        return "Only available on macOS, sir."
    # macOS Sequoia+ has built-in tiling, but for older versions we use AppleScript
    script = f'''
    tell application "{app_name}" to activate
    delay 0.3
    tell application "System Events"
        tell process "{app_name}"
            set position of window 1 to {{0, 0}}
        end tell
    end tell
    '''
    _run_applescript(script)
    return f"Tiled {app_name} to left side, sir."


def split_screen_right(app_name: str) -> str:
    """Tile window to right half of screen."""
    if not is_macos():
        return "Only available on macOS, sir."
    script = f'''
    tell application "{app_name}" to activate
    delay 0.3
    tell application "System Events"
        tell process "{app_name}"
            set position of window 1 to {{960, 0}}
        end tell
    end tell
    '''
    _run_applescript(script)
    return f"Tiled {app_name} to right side, sir."


def get_window_list() -> str:
    """List all visible windows."""
    if not is_macos():
        return "Only available on macOS, sir."
    script = '''
    tell application "System Events"
        set windowList to ""
        repeat with proc in (every process whose visible is true)
            set procName to name of proc
            repeat with w in (every window of proc)
                set windowList to windowList & procName & " - " & (name of w) & "\\n"
            end repeat
        end repeat
    end tell
    '''
    result = _run_applescript(script)
    if result and not result.startswith("Error"):
        if result.strip():
            return f"Visible windows:\n{result.strip()}"
        return "No visible windows found, sir."
    return f"Error listing windows: {result}"


def hide_app(app_name: str) -> str:
    """Hide an application (cmd+H)."""
    if not is_macos():
        return "Only available on macOS, sir."
    script = f'''
    tell application "{app_name}" to activate
    delay 0.2
    tell application "System Events" to keystroke "h" using command down
    '''
    _run_applescript(script)
    return f"Hidden {app_name}, sir."


def minimize_app_wrapper(text: str) -> str:
    for prefix in ["minimize safari", "minimize chrome", "minimize spotify",
                   "minimize vscode", "minimize code", "minimize slack",
                   "minimize mail", "minimize firefox", "minimize terminal", "minimize "]:
        if prefix in text:
            name = text.split(prefix, 1)[-1].strip() if prefix == "minimize " else prefix.replace("minimize ", "")
            if prefix == "minimize ":
                name = text.split("minimize ", 1)[-1].strip()
            if name:
                return minimize_app(name)
            break
    return "Which app would you like me to minimize?"

def fullscreen_app_wrapper(text: str) -> str:
    for prefix in ["fullscreen "]:
        if prefix in text:
            name = text.split(prefix, 1)[-1].strip()
            if name:
                return fullscreen_app(name)
            break
    return "Which app would you like to fullscreen?"

def bring_to_front_wrapper(text: str) -> str:
    for prefix in ["focus "]:
        if prefix in text:
            name = text.split(prefix, 1)[-1].strip()
            if name:
                return bring_to_front(name)
            break
    return "Which app would you like me to bring to front?"

def close_all_windows_wrapper(text: str) -> str:
    for prefix in ["close all windows"]:
        if prefix in text:
            rest = text.split(prefix, 1)[-1].strip()
            # Remove common filler words
            for word in ["of ", "in ", "for "]:
                if rest.startswith(word):
                    rest = rest[len(word):]
            if rest:
                return close_all_windows(rest)
            break
    return "Which app's windows would you like me to close?"

def hide_app_wrapper(text: str) -> str:
    for prefix in ["hide "]:
        if prefix in text:
            name = text.split(prefix, 1)[-1].strip()
            if name:
                return hide_app(name)
            break
    return "Which app would you like me to hide?"


def hide_all_others() -> str:
    """Hide all applications except the frontmost one (cmd+option+H)."""
    if not is_macos():
        return "Only available on macOS, sir."
    script = '''
    tell application "System Events" to keystroke "h" using {command down, option down}
    '''
    _run_applescript(script)
    return "Hidden all other applications, sir."
