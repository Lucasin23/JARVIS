#!/usr/bin/env bash
#
# JARVIS 2.1 — one-shot macOS setup.
# Run with:
#   curl -fsSL https://raw.githubusercontent.com/Lucasin23/JARVIS/main/setup_mac.sh | bash
#
# Or, after cloning:
#   bash setup_mac.sh
#
# Idempotent: safe to re-run if a step failed.
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/JARVIS}"
CHAT_MODEL="${CHAT_MODEL:-gemma3:4b}"

echo "============================================================"
echo " JARVIS 2.1 — macOS setup"
echo "============================================================"

# --- 1. macOS version check ---------------------------------------------------
if ! sw_vers >/dev/null 2>&1; then
  echo "✗ This script is for macOS only."
  exit 1
fi
echo "✓ macOS $(sw_vers -productVersion)"

# --- 2. Homebrew --------------------------------------------------------------
if ! command -v brew >/dev/null 2>&1; then
  echo "→ Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi
echo "✓ Homebrew: $(brew --version | head -1)"

# --- 3. System prerequisites -------------------------------------------------
echo "→ Installing system prerequisites (portaudio, ollama, uv)..."
brew install portaudio
brew install --cask ollama || brew install ollama
brew install uv
echo "✓ System prerequisites installed"

# --- 4. Start Ollama server ---------------------------------------------------
echo "→ Starting Ollama..."
open -a Ollama 2>/dev/null || ollama serve >/dev/null 2>&1 &
echo "   Waiting for Ollama to respond..."
for _ in $(seq 1 30); do
  if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "✗ Ollama did not start. Open the Ollama app, then re-run this script."
  exit 1
fi
echo "✓ Ollama is running"

# --- 5. Clone / update the repo ----------------------------------------------
if [ -d "$REPO_DIR/.git" ]; then
  echo "→ Updating existing checkout at $REPO_DIR..."
  git -C "$REPO_DIR" pull --ff-only
else
  echo "→ Cloning JARVIS to $REPO_DIR..."
  git clone https://github.com/Lucasin23/JARVIS.git "$REPO_DIR"
fi
cd "$REPO_DIR"
echo "✓ Repository ready at $REPO_DIR"

# --- 6. Python virtual environment ------------------------------------------
echo "→ Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install --upgrade pip >/dev/null 2>&1 || true
echo "→ Installing Python dependencies (this can take a minute)..."
.venv/bin/python -m pip install -r requirements.txt
echo "✓ Python dependencies installed in .venv"

# --- 7. Pull the chat model (one-time, ~3 GB) -------------------------------
if ! ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$CHAT_MODEL"; then
  echo "→ Pulling chat model '$CHAT_MODEL' (one-time, ~3 GB)..."
  ollama pull "$CHAT_MODEL"
fi
echo "✓ Chat model ready: $CHAT_MODEL"

# --- 8. Verify setup ----------------------------------------------------------
echo "→ Verifying setup..."
.venv/bin/python check_setup.py || echo "   (fix any issues flagged above, then continue)"

# --- 9. Done -----------------------------------------------------------------
echo
echo "============================================================"
echo " ✓ Setup complete!"
echo "============================================================"
echo
echo "Next steps:"
echo "  1. Grant microphone permission:"
echo "     System Settings → Privacy & Security → Microphone → enable Terminal"
echo "  2. (Optional) ElevenLabs voice:"
echo "     cp .env.example .env  &&  open -e .env   # set ELEVENLABS_API_KEY"
echo "  3. Run JARVIS:"
echo "     cd $REPO_DIR && .venv/bin/python main.py"
echo
echo "Say \"Jarvis\" to wake it, then speak. Say \"shutdown\" to stop."
