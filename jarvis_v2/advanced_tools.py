"""
Advanced Tools Module — Clipboard history, code execution, password generation,
text utilities, reminders, and system cleanup.
"""

import os
import subprocess
import platform
import random
import string
import time
import json
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ---------------------------------------------------------------------------
# Clipboard History (in-memory)
# ---------------------------------------------------------------------------

_clipboard_history: list[str] = []
MAX_CLIPBOARD_HISTORY = 50


def track_clipboard() -> str | None:
    """Check clipboard for new content and add to history. Returns new content or None."""
    if platform.system() != "Darwin":
        return None
    try:
        result = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=2)
        content = result.stdout.strip()
        if content and (not _clipboard_history or _clipboard_history[-1] != content):
            _clipboard_history.append(content)
            if len(_clipboard_history) > MAX_CLIPBOARD_HISTORY:
                _clipboard_history.pop(0)
            return content
    except Exception:
        pass
    return None


def get_clipboard_history() -> str:
    """Show clipboard history."""
    if not _clipboard_history:
        return "Clipboard history is empty, sir."
    result = "Clipboard History:\n"
    for i, item in enumerate(reversed(_clipboard_history[-10:]), 1):
        preview = item[:100].replace("\n", " ")
        result += f"  {i}. {preview}\n"
    return result.strip()


def clear_clipboard_history() -> str:
    """Clear clipboard history."""
    _clipboard_history.clear()
    return "Clipboard history cleared, sir."


# ---------------------------------------------------------------------------
# Code Execution
# ---------------------------------------------------------------------------

def execute_python(text: str) -> str:
    """Execute Python code from user input."""
    # Extract code
    code = ""
    for prefix in ["run python", "execute python", "python code", "python:",
                   "run python code", "execute code"]:
        if prefix in text.lower():
            idx = text.lower().index(prefix) + len(prefix)
            code = text[idx:].strip()
            break

    if not code:
        return "What Python code would you like me to run? Example: run python print('hello')"

    # Remove quotes if wrapped
    if (code.startswith("'") and code.endswith("'")) or (code.startswith('"') and code.endswith('"')):
        code = code[1:-1]

    try:
        # Capture stdout
        import io
        import contextlib
        import traceback

        old_stdout = io.StringIO()
        with contextlib.redirect_stdout(old_stdout):
            try:
                exec(code, {"__name__": "__main__", "print": print})
            except Exception:
                traceback.print_exc(file=old_stdout)

        output = old_stdout.getvalue().strip()
        if output:
            if len(output) > 2000:
                output = output[:2000] + "\n... (truncated)"
            return f"Python output:\n{output}"
        return "Code executed successfully (no output), sir."
    except Exception as e:
        return f"Error executing code: {e}"


def execute_python_file(text: str) -> str:
    """Run a Python script file."""
    # Extract filename
    path = ""
    for prefix in ["run python file", "run script", "execute script", "run file"]:
        if prefix in text.lower():
            path = text.lower().split(prefix, 1)[-1].strip()
            break

    if not path:
        return "Which Python file would you like me to run? Example: run script my_script.py"

    filepath = os.path.expanduser(path)
    if not os.path.exists(filepath):
        return f"I couldn't find '{path}', sir."

    try:
        result = subprocess.run(
            ["python3", filepath],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            if output:
                if len(output) > 2000:
                    output = output[:2000] + "\n... (truncated)"
                return f"Script output:\n{output}"
            return "Script executed successfully (no output), sir."
        return f"Script failed:\n{error}"
    except subprocess.TimeoutExpired:
        return "Script timed out after 30 seconds, sir."
    except Exception as e:
        return f"Error running script: {e}"


# ---------------------------------------------------------------------------
# Password Generator
# ---------------------------------------------------------------------------

def generate_password(text: str) -> str:
    """Generate a secure random password."""
    # Check for length
    length = 16  # default
    for word in text.split():
        if word.isdigit():
            n = int(word)
            if 4 <= n <= 128:
                length = n
                break

    # Check for character type preferences
    use_symbols = True
    use_numbers = True
    use_upper = True
    use_lower = True

    if "no symbols" in text.lower() or "no special" in text.lower():
        use_symbols = False
    if "no numbers" in text.lower() or "no digits" in text.lower():
        use_numbers = False
    if "no uppercase" in text.lower() or "lowercase only" in text.lower():
        use_upper = False

    charset = ""
    if use_lower:
        charset += string.ascii_lowercase
    if use_upper:
        charset += string.ascii_uppercase
    if use_numbers:
        charset += string.digits
    if use_symbols:
        charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if not charset:
        charset = string.ascii_lowercase + string.digits

    password = "".join(random.choice(charset) for _ in range(length))

    return f"Generated password ({length} chars):\n  {password}"


# ---------------------------------------------------------------------------
# Text Utilities
# ---------------------------------------------------------------------------

def count_words(text: str) -> str:
    """Count words, characters, and lines in text."""
    # Extract the text to count (everything after the command)
    target = ""
    for prefix in ["count words in", "word count", "count characters in", "count "]:
        if prefix in text.lower():
            target = text.split(prefix, 1)[-1].strip() if prefix in text.lower() else ""
            break

    if not target:
        return "What text would you like me to count? Example: count words in hello world this is a test"

    words = len(target.split())
    chars = len(target)
    chars_no_spaces = len(target.replace(" ", ""))
    lines = len(target.split("\n"))
    sentences = target.count(".") + target.count("!") + target.count("?")

    return (
        f"Text statistics:\n"
        f"  Words: {words}\n"
        f"  Characters: {chars}\n"
        f"  Characters (no spaces): {chars_no_spaces}\n"
        f"  Lines: {lines}\n"
        f"  Sentences: {sentences}"
    )


def base64_encode(text: str) -> str:
    """Base64 encode text."""
    import base64
    target = ""
    for prefix in ["base64 encode", "encode base64", "encode b64"]:
        if prefix in text.lower():
            target = text.lower().split(prefix, 1)[-1].strip()
            break

    if not target:
        return "What text would you like me to encode?"

    try:
        encoded = base64.b64encode(target.encode()).decode()
        return f"Base64 encoded:\n  {encoded}"
    except Exception as e:
        return f"Encoding error: {e}"


def base64_decode(text: str) -> str:
    """Base64 decode text."""
    import base64
    target = ""
    text_lower = text.lower()
    for prefix in ["base64 decode", "decode base64", "decode b64"]:
        if prefix in text_lower:
            idx = text_lower.index(prefix) + len(prefix)
            target = text[idx:].strip()  # Use original text to preserve case
            break

    if not target:
        return "What base64 would you like me to decode?"

    try:
        decoded = base64.b64decode(target).decode()
        return f"Decoded:\n  {decoded}"
    except Exception as e:
        return f"Decoding error: {e}"


# ---------------------------------------------------------------------------
# Reminder / Timer
# ---------------------------------------------------------------------------

_active_timers: list[dict] = []


def set_timer(text: str) -> str:
    """Set a countdown timer."""
    # Extract minutes
    minutes = 0
    seconds = 0
    for word in text.split():
        if word.isdigit():
            n = int(word)
            if n > 0 and n < 10000:
                if "minute" in text.lower() or "min" in text.lower():
                    minutes = n
                elif "second" in text.lower() or "sec" in text.lower():
                    seconds = n
                else:
                    minutes = n  # default to minutes
                break

    if "hour" in text.lower() or "hr" in text.lower():
        for word in text.split():
            if word.isdigit():
                minutes = int(word) * 60
                break

    if minutes == 0 and seconds == 0:
        return "How long? Example: set timer for 5 minutes"

    total_seconds = minutes * 60 + seconds
    end_time = datetime.now().timestamp() + total_seconds

    _active_timers.append({
        "end_time": end_time,
        "duration": total_seconds,
        "label": f"{minutes}m {seconds}s" if minutes and seconds else f"{minutes}m" if minutes else f"{seconds}s"
    })

    # Start timer in background
    def _timer_done():
        time.sleep(total_seconds)
        if platform.system() == "Darwin":
            subprocess.run([
                "osascript", "-e",
                f'display notification "Timer for {_active_timers[0]["label"]} is done!" with title "JARVIS Timer"'
            ])

    import threading
    t = threading.Thread(target=_timer_done, daemon=True)
    t.start()

    return f"Timer set for {_active_timers[-1]['label']}, sir. I'll notify you when it's done."


# ---------------------------------------------------------------------------
# System Cleanup
# ---------------------------------------------------------------------------

def clear_cache() -> str:
    """Clear common cache locations on macOS."""
    if platform.system() != "Darwin":
        return "Cache clearing is optimized for macOS, sir."

    cleared = []
    cache_dirs = [
        ("User cache", os.path.expanduser("~/Library/Caches")),
        ("System logs", os.path.expanduser("~/Library/Logs")),
        ("DNS cache", None),  # Special handling
    ]

    # Clear DNS cache
    try:
        subprocess.run(["sudo", "dscacheutil", "-flushcache"], capture_output=True, timeout=5)
        subprocess.run(["sudo", "killall", "-HUP", "mDNSResponder"], capture_output=True, timeout=5)
        cleared.append("DNS cache")
    except Exception:
        pass

    # Report sizes before clearing (don't actually delete to be safe)
    sizes = []
    for name, path in cache_dirs:
        if path and os.path.exists(path):
            try:
                result = subprocess.run(
                    ["du", "-sh", path], capture_output=True, text=True, timeout=10
                )
                size = result.stdout.strip().split("\t")[0] if result.stdout else "unknown"
                sizes.append(f"  {name}: {size}")
            except Exception:
                sizes.append(f"  {name}: unknown")

    return (
        f"Cache report:\n" + "\n".join(sizes) +
        f"\n  DNS cache: flushed\n\n"
        f"To manually clear caches, run:\n"
        f"  rm -rf ~/Library/Caches/*\n"
        f"  rm -rf ~/Library/Logs/*\n"
        f"Note: I won't delete files automatically for safety, sir."
    )


def clear_terminal() -> str:
    """Clear the terminal screen."""
    os.system("clear" if platform.system() != "Windows" else "cls")
    return ""  # No spoken response needed


# ---------------------------------------------------------------------------
# Fun Features
# ---------------------------------------------------------------------------

def say_text(text: str) -> str:
    """Make macOS say text aloud using the 'say' command."""
    if platform.system() != "Darwin":
        return "Text-to-speech via 'say' is macOS only, sir."

    # Extract text to say
    target = ""
    for prefix in ["say ", "speak ", "mac say "]:
        if prefix in text.lower():
            target = text[len(prefix):].strip() if text.lower().startswith(prefix) else ""
            if not target:
                idx = text.lower().index(prefix) + len(prefix)
                target = text[idx:].strip()
            break

    if not target:
        return "What would you like me to say?"

    try:
        subprocess.Popen(["say", target])
        return "Speaking, sir."
    except Exception as e:
        return f"Error: {e}"


def roll_dice_wrapper(text: str) -> str:
    return roll_dice(text)


def get_quote() -> str:
    """Get an inspirational quote from a public API."""
    if not HAS_REQUESTS:
        return "Install requests: pip install requests"

    try:
        response = requests.get("https://api.quotable.io/random", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"'{data['content']}'\n  - {data['author']}"
        return "I couldn't fetch a quote right now, sir."
    except Exception:
        # Fallback quotes
        quotes = [
            "The best way to predict the future is to invent it. - Alan Kay",
            "Code is like humor. When you have to explain it, it's bad. - Cory House",
            "Talk is cheap. Show me the code. - Linus Torvalds",
            "Programs must be written for people to read. - Harold Abelson",
            "The function of good software is to make the complex appear simple. - Grady Booch",
        ]
        import random
        return random.choice(quotes)


def roll_dice(text: str) -> str:
    """Roll dice (default: 1d6)."""
    num_dice = 1
    sides = 6

    for word in text.split():
        if "d" in word and word.replace("d", "").isdigit():
            parts = word.split("d")
            if len(parts) == 2:
                try:
                    num_dice = int(parts[0])
                    sides = int(parts[1])
                except ValueError:
                    pass

    rolls = [random.randint(1, sides) for _ in range(num_dice)]
    total = sum(rolls)

    if num_dice == 1:
        return f"Rolled a d{sides}: {rolls[0]}"

    return f"Rolled {num_dice}d{sides}: {rolls} = {total}"
