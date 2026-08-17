# JARVIS AI Assistant v2.0

A voice/text-controlled AI assistant inspired by Iron Man's JARVIS (Just A Rather Very Intelligent System).

Built in Python with full macOS system control — open/close apps, volume, brightness, dark mode, file operations, shell commands, system monitoring, network tools, window management, Git integration, and AI-powered natural language command interpretation.

**Requirements:** Python 3.10+ (uses `str | None` and `list[dict]` type hints)
**Platform:** macOS (optimized for Apple Silicon M1/M2/M3). Basic commands work on Linux/Windows too.

## Features

### System Control (macOS)
- Open/close/minimize/hide applications
- Volume control (set, mute, unmute)
- Brightness control (requires `brew install brightness`)
- Dark mode toggle
- Sleep, lock screen, restart
- Screenshots
- Empty trash
- Clipboard read/track
- Battery status
- Wi-Fi info
- macOS text-to-speech via `say` command

### File Operations
- Create files and folders
- Read file contents
- List directory contents
- Search for files by pattern
- Delete files (moves to trash if `send2trash` is installed)
- Get file information (size, modified date, type)
- Reveal files in Finder

### Terminal & Shell
- Run any shell command with safety checks (dangerous commands are blocked)
- Execute Python code inline
- Run Python script files

### System Monitoring
- Full system report (CPU, memory, disk, network, uptime)
- Top processes by CPU or memory
- Kill processes by name or PID
- Active network connections
- Battery details
- Proactive alerts (high CPU, low memory/disk/battery)

### Network Tools
- Local and public IP addresses
- Ping hosts
- Internet speed test
- Port scanning
- DNS lookup
- Wi-Fi details

### Window Management
- Minimize specific apps or all windows
- Toggle fullscreen
- Bring apps to front
- Close all windows of an app
- List visible windows
- Hide apps or hide all others

### Git Integration
- Repository status (staged, unstaged, untracked files)
- Recent commit log
- Branch listing
- Comprehensive repo info
- Pull and push

### Music Control
- Play/pause (Spotify or Apple Music)
- Next/previous track

### Advanced Utilities
- Password generator (configurable length and character types)
- Word/character counter
- Base64 encode/decode
- Countdown timer with notification
- Clipboard history tracking
- System cache report
- Terminal clearing
- Inspirational quotes
- Dice roller (supports NdM notation)

### AI Conversation (Optional)
- Falls back to LLM for anything not covered by built-in commands
- AI-powered command interpretation (translates natural language to system actions)
- Conversation history for context
- Supports any OpenAI-compatible API (OpenAI, Groq, Together AI, Ollama, etc.)

## Quick Start

### 1. Install Dependencies

```bash
# Core dependencies (required)
pip install -r requirements.txt

# Voice input dependencies (optional, for microphone mode)
pip install -r requirements-voice.txt
```

### 2. (Optional) Configure AI Responses

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

Without an API key, JARVIS works with all built-in commands. AI conversation and command interpretation require an OpenAI-compatible API key.

### 3. Run JARVIS

```bash
# Default: Text input + voice output
python main.py

# Full voice mode (speak + hear responses)
python main.py --voice

# Voice input, text output (quiet environments)
python main.py --voice-in

# Silent text-only mode
python main.py --text

# Disable proactive monitoring
python main.py --no-proactive
```

## Command Reference

### System Control
| Command | Example |
|---------|---------|
| Open app | "open Safari", "open Calculator" |
| Close app | "close Chrome", "quit Spotify" |
| List running apps | "list apps", "running apps" |
| Set volume | "set volume to 50" |
| Mute/unmute | "mute", "unmute" |
| Get volume | "what's the volume" |
| Set brightness | "set brightness to 80" |
| Dark mode | "toggle dark mode", "dark mode status" |
| Sleep | "sleep", "go to sleep" |
| Lock screen | "lock screen" |
| Restart | "restart" |
| Screenshot | "take a screenshot" |
| Empty trash | "empty trash" |
| Battery | "battery status" |
| Wi-Fi | "wi-fi info" |

### File Operations
| Command | Example |
|---------|---------|
| Create file | "create file notes.txt" |
| Create file with content | "create file notes.txt with content hello world" |
| Create folder | "create folder Projects" |
| Read file | "read file notes.txt" |
| List files | "list files" or "list files Downloads" |
| Search files | "find files *.py" |
| Delete file | "delete file old_notes.txt" |
| File info | "file info notes.txt" |
| Reveal in Finder | "reveal file Downloads" |
| Open folder | "open folder Documents" |

### Terminal & Shell
| Command | Example |
|---------|---------|
| Run command | "run command ls -la" or just "ls -la" |
| Run Python | "run python print('hello')" |
| Run script | "run script my_script.py" |

### System Monitoring
| Command | Example |
|---------|---------|
| Full report | "system report", "full system status" |
| Top processes | "top processes" or "top processes by memory" |
| Kill process | "kill process Safari" |
| Network connections | "network connections" |
| Battery detail | "battery detail" |

### Network Tools
| Command | Example |
|---------|---------|
| IP address | "my IP address" |
| Ping | "ping google.com" |
| Speed test | "speed test" |
| Port scan | "scan ports localhost" |
| DNS lookup | "dns lookup google.com" |

### Window Management
| Command | Example |
|---------|---------|
| Minimize app | "minimize Safari" |
| Minimize all | "minimize all" |
| Fullscreen | "fullscreen Chrome" |
| Bring to front | "focus Safari" |
| Close windows | "close all windows Safari" |
| List windows | "list windows" |
| Hide app | "hide Safari" |
| Hide others | "hide all others" |

### Git
| Command | Example |
|---------|---------|
| Status | "git status" |
| Log | "git log" |
| Branches | "git branches" |
| Repo info | "git info" |
| Pull | "git pull" |
| Push | "git push" |

### Music
| Command | Example |
|---------|---------|
| Play | "play music" |
| Pause | "pause music" |
| Next | "next track" |
| Previous | "previous track" |

### Advanced
| Command | Example |
|---------|---------|
| Password | "generate password 20" |
| Word count | "count words in hello world" |
| Base64 encode | "base64 encode hello" |
| Base64 decode | "base64 decode aGVsbG8=" |
| Timer | "set timer for 5 minutes" |
| Clipboard history | "clipboard history" |
| Clear cache | "clear cache" |
| Clear screen | "clear screen" |
| Mac say | "say hello world" |
| Quote | "inspire me" |
| Dice | "roll dice" or "roll 2d20" |

### Basic
| Command | Example |
|---------|---------|
| Time | "what time is it" |
| Date | "what's the date" |
| Weather | "weather in Stockholm" |
| Open website | "open YouTube", "open Google" |
| Web search | "search for Python tutorials" |
| Joke | "tell me a joke" |
| Help | "help" |
| Exit | "exit", "quit", "goodbye" |

## Project Structure

```
jarvis_assistant/
├── main.py              # Entry point with CLI argument parsing
├── assistant.py         # Core interaction loop (ties everything together)
├── speech.py            # TTS (text-to-speech) and STT (speech-to-text) helpers
├── commands.py          # Command routing registry (integrates all modules)
├── llm.py               # Optional AI conversation + command interpretation layer
├── macos_control.py     # macOS automation via AppleScript (apps, volume, brightness, etc.)
├── file_ops.py          # File operations (create, read, list, search, delete)
├── shell_executor.py    # Shell command execution with safety checks
├── system_monitor.py    # System monitoring (CPU, memory, processes, alerts)
├── network_tools.py     # Network diagnostics (ping, IP, speed test, port scan)
├── window_manager.py    # macOS window management (minimize, fullscreen, etc.)
├── git_tools.py         # Git repository management
├── advanced_tools.py    # Clipboard history, code execution, password gen, text utils
├── requirements.txt     # Core Python dependencies
├── requirements-voice.txt  # Optional voice input dependencies
├── .env.example         # Template for environment variables
└── README.md            # This file
```

## Platform Notes

### PyAudio Installation (for voice input)

PyAudio can be tricky to install. Here are platform-specific instructions:

**macOS (with Homebrew):**
```bash
brew install portaudio
pip install pyaudio
```

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**Windows:**
```bash
pip install pyaudio
```

**If PyAudio fails:** Run in text mode (`python main.py --text` or just `python main.py`). All features except voice input work without PyAudio.

### Brightness Control (macOS)

Brightness control requires the `brightness` CLI tool:
```bash
brew install brightness
```

### TTS (pyttsx3)

pyttsx3 works offline and uses macOS's native speech synthesis. If it fails, JARVIS falls back to text-only output automatically.

## Configuration

### Environment Variables (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (empty) | API key for AI conversation mode |
| `OPENAI_API_BASE` | `https://api.openai.com/v1` | Base URL (change for other providers) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model name to use |

### Using Local LLMs (no API key needed)

JARVIS supports local LLMs via Ollama or LM Studio. Set these in your `.env`:

**Ollama:**
```env
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_MODEL=llama3
```

**LM Studio:**
```env
OPENAI_API_BASE=http://localhost:1234/v1
OPENAI_MODEL=local-model
```

When the base URL points to localhost, JARVIS automatically works without an API key.

### Other OpenAI-Compatible Providers

- **Groq**: `OPENAI_API_BASE=https://api.groq.com/openai/v1`, `OPENAI_MODEL=llama-3.3-70b-versatile`
- **Together AI**: `OPENAI_API_BASE=https://api.together.xyz/v1`, `OPENAI_MODEL=meta-llama/Llama-3-70b-chat-hf`

## Extending JARVIS

### Add a New Command

1. Write a handler function (in an existing or new module):
```python
def cmd_my_command(text: str) -> str:
    return "My custom response!"
```

2. Register it in the `COMMANDS` list in `commands.py`:
```python
(["my command", "custom command"], cmd_my_command, 13),
```

The number is priority (lower = checked first). JARVIS matches commands by checking if any trigger keyword appears in the user's input.

### Add a New Module

Create a new Python file (e.g., `home_automation.py`) and import/call it from `commands.py` or `assistant.py`.

## macOS Permissions

JARVIS controls your Mac via AppleScript and system commands. On first use, macOS will prompt you to grant permissions. You may need to manually approve them in **System Settings > Privacy & Security**:

| Permission | Needed For | How to Grant |
|-----------|-----------|---------------|
| **Accessibility** | Window management, app control via System Events | System Settings > Privacy & Security > Accessibility > Add Terminal/iTerm |
| **Automation** | Controlling other apps (Spotify, Safari, etc.) | Granted via popup on first use per app |
| **Microphone** | Voice input mode | System Settings > Privacy & Security > Microphone > Enable Terminal |
| **Screen Recording** | Screenshots | System Settings > Privacy & Security > Screen Recording > Enable Terminal |
| **Full Disk Access** | File operations outside home directory | System Settings > Privacy & Security > Full Disk Access > Add Terminal |

If JARVIS says it can't perform an action, check these permissions first.

## Safety

JARVIS includes safety features:
- Dangerous shell commands (e.g., `rm -rf /`) are blocked outright
- Destructive commands (e.g., `rm`, `mv`, `chmod`, `kill`, `git push`) are flagged with a `[CAUTION]` warning
- File operations are restricted to the user's home directory
- File deletion uses `send2trash` to move to Trash (recoverable) instead of permanent deletion
- Shell command execution has a 30-second timeout

## Disclaimer

This is a project inspired by the fictional JARVIS from Marvel's Iron Man. It is not an autonomous system and should not be used for critical or safety-related tasks. Use responsibly.
