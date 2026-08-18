#!/usr/bin/env bash
#
# JARVIS — launcher for the root prototype (main.py).
# Double-clickable on macOS (saved as run_jarvis.command) or run from a shell:
#   bash run_jarvis.sh
#
# What this does:
#   1. Verifies Python 3 is available.
#   2. Installs Python dependencies from requirements.txt (once / if missing).
#   3. Checks that Ollama is running and the chat model (gemma3:4b) is present.
#   4. Starts JARVIS:  python3 main.py
#
# JARVIS is macOS-only at runtime (it uses `open`, `osascript`, and `afplay`).
set -euo pipefail

cd "$(dirname "$0")"

# Prefer the venv created by setup_mac.sh if it exists.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -z "${PYTHON:-}" ] && [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
  PYTHON="$SCRIPT_DIR/.venv/bin/python"
elif [ -z "${PYTHON:-}" ]; then
  PYTHON="python3"
fi

# --- 1. Python ---------------------------------------------------------------
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "✗ Python 3 not found. Install Python 3.10+ from https://www.python.org/downloads"
  exit 1
fi
echo "✓ Python: $($PYTHON --version)"

# --- 2. Python dependencies --------------------------------------------------
if ! "$PYTHON" -c "import speech_recognition, pyaudio, numpy, openwakeword" >/dev/null 2>&1; then
  echo "→ Installing Python dependencies (requirements.txt)..."
  "$PYTHON" -m pip install --upgrade pip >/dev/null 2>&1 || true
  "$PYTHON" -m pip install -r requirements.txt
fi
echo "✓ Python dependencies installed"

# --- 3. Ollama + chat model --------------------------------------------------
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
CHAT_MODEL="${CHAT_MODEL:-gemma3:4b}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "✗ Ollama CLI not found. Install it from https://ollama.com/download"
  exit 1
fi

if ! curl -sf "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
  echo "→ Ollama server not responding. Starting it..."
  ollama serve >/dev/null 2>&1 &
  sleep 2
fi

if ! curl -sf "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
  echo "✗ Ollama is not running. Start it with:  ollama serve"
  exit 1
fi
echo "✓ Ollama is running"

if ! ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$CHAT_MODEL"; then
  echo "→ Chat model '$CHAT_MODEL' not found. Pulling it (one-time, ~3GB)..."
  ollama pull "$CHAT_MODEL"
fi
echo "✓ Chat model ready: $CHAT_MODEL"

# --- 4. Launch JARVIS --------------------------------------------------------
echo
echo "JARVIS starting — say \"Jarvis\" to wake it, then speak."
echo "Press Ctrl+C to stop."
echo
exec "$PYTHON" main.py
