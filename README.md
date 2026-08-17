# JARVIS workspace

The production JARVIS application lives in [`jarvis/`](jarvis/README.md).
Run, test, package, and modify the assistant from that directory. The
root-level prototype and archived files are retained as historical material
and are not part of the supported runtime.

## JARVIS v2 — Advanced macOS Assistant

[`jarvis_v2/`](jarvis_v2/README.md) is an advanced, modular Python AI assistant with full macOS system control:
- Voice + text input modes with graceful fallbacks
- macOS automation (apps, volume, brightness, dark mode, sleep, screenshots)
- File operations, shell command execution, system monitoring
- Network tools, window management, Git integration
- AI conversation via OpenAI-compatible APIs (OpenAI, Groq, Ollama, etc.)
- Proactive system alerts (high CPU, low battery, low disk)

See the [v2 README](jarvis_v2/README.md) for setup and full command reference.

For development and launch instructions, see the [production README](jarvis/README.md).
