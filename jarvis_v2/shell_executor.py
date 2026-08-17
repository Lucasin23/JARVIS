"""
Shell Executor Module — Run terminal commands with safety checks.
Lets JARVIS execute shell commands when you ask it to.
Includes a blocklist of dangerous commands and a confirmation system.
"""

import subprocess
import platform
from datetime import datetime


# Commands that are blocked outright (too dangerous for an assistant)
BLOCKED_COMMANDS = [
    "rm -rf /", "rm -rf ~", "rm -rf /*", "rm -rf *",
    "mkfs", "dd if=/dev/zero", "dd if=/dev/random",
    ":(){ :|:& };:",  # fork bomb
    "chmod -R 777 /",
    "shutdown -h now", "halt", "init 0",
]

# Commands that require explicit confirmation (destructive but useful)
DESTRUCTIVE_PATTERNS = [
    "rm ", "rmdir", "mv ", "chmod", "chown",
    "kill ", "killall", "pkill",
    ">", ">>",  # file overwriting
    "pip uninstall", "brew uninstall", "npm uninstall",
    "git push", "git reset --hard", "git clean",
    "defaults write",  # system settings change
    "defaults delete",
]


def _is_blocked(command: str) -> bool:
    """Check if a command is in the blocklist."""
    cmd_lower = command.lower().strip()
    for blocked in BLOCKED_COMMANDS:
        if blocked in cmd_lower:
            return True
    return False


def _is_destructive(command: str) -> bool:
    """Check if a command is potentially destructive (needs confirmation)."""
    cmd_lower = command.lower().strip()
    for pattern in DESTRUCTIVE_PATTERNS:
        if pattern in cmd_lower:
            return True
    return False


def extract_command(text: str) -> str | None:
    """Extract a shell command from natural language input."""
    text_lower = text.lower()

    # Common patterns for shell commands
    # NOTE: Do NOT include generic "run " or "execute " here -- those are handled
    # by registered commands (run python, run script, run command) in commands.py
    prefixes = [
        "run command", "run terminal command", "execute command",
        "terminal command", "shell command",
        "terminal: ", "cmd: ", "shell: ",
    ]

    for prefix in prefixes:
        if text_lower.startswith(prefix):
            cmd = text[len(prefix):].strip()
            if cmd:
                return cmd

    # If the input looks like a raw command (starts with common CLI tools)
    cli_tools = [
        "ls", "cd", "pwd", "echo", "cat", "grep", "find", "wc",
        "head", "tail", "sort", "uniq", "cut", "tr", "sed", "awk",
        "git ", "pip ", "npm ", "brew ", "python ", "python3 ",
        "node ", "java ", "gcc ", "make ", "docker ", "curl ", "wget ",
        "ssh ", "scp ", "rsync ", "tar ", "zip ", "unzip ",
        "mkdir", "touch", "cp ", "mv ", "ln ", "chmod", "chown",
        "ps ", "top ", "df ", "du ", "free", "whoami", "hostname",
        "ifconfig", "ping ", "traceroute", "dig ", "nslookup",
        "defaults ", "open ", "pbcopy", "pbpaste", "say ",
        "screencapture", "pmset ", "networksetup",
        "launchctl ", "defaults", "diskutil ",
        "caffeinate", "pbpaste", "open",
    ]

    for tool in cli_tools:
        if text_lower.startswith(tool):
            return text.strip()

    return None


def run_command(command: str, timeout: int = 30) -> dict:
    """
    Execute a shell command safely.
    Returns a dict with: success, output, error, is_destructive, is_blocked.
    """
    if _is_blocked(command):
        return {
            "success": False,
            "output": "",
            "error": "Command blocked for safety reasons, sir.",
            "is_destructive": False,
            "is_blocked": True,
        }

    is_destr = _is_destructive(command)

    try:
        # Use bash for consistent behavior
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            executable="/bin/bash" if platform.system() != "Windows" else None,
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        # Truncate very long output
        if len(output) > 3000:
            output = output[:3000] + "\n... (output truncated)"

        return {
            "success": result.returncode == 0,
            "output": output,
            "error": error,
            "is_destructive": is_destr,
            "is_blocked": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Command timed out after {timeout} seconds, sir.",
            "is_destructive": is_destr,
            "is_blocked": False,
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Error executing command: {e}",
            "is_destructive": is_destr,
            "is_blocked": False,
        }


def format_command_result(result: dict, command: str) -> str:
    """Format a command execution result for JARVIS to speak."""
    if result["is_blocked"]:
        return result["error"]

    if result["success"]:
        if result["output"]:
            return f"Command executed successfully:\n\n{result['output']}"
        return "Command executed successfully, sir. No output."
    else:
        msg = f"Command failed"
        if result["error"]:
            msg += f": {result['error']}"
        if result["output"]:
            msg += f"\nOutput: {result['output']}"
        return msg + "."


def run_command_wrapper(command: str) -> str:
    """Wrapper for command routing: runs a shell command and returns formatted result."""
    # If the input starts with 'run command' etc, extract the actual command
    for prefix in ["run command", "run terminal command", "execute command",
                   "terminal command", "shell command"]:
        if command.lower().startswith(prefix):
            actual_cmd = command[len(prefix):].strip()
            break
    else:
        actual_cmd = command

    if not actual_cmd:
        return "What command would you like me to run?"

    # Check for destructive commands and add a warning
    if _is_destructive(actual_cmd):
        result = run_command(actual_cmd)
        if result["success"]:
            return f"[CAUTION: destructive command] Command executed:\n{result.get('output', '')}"
        return f"[CAUTION: destructive command] {format_command_result(result, actual_cmd)}"

    result = run_command(actual_cmd)
    return format_command_result(result, actual_cmd)
