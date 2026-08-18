# JARVIS

A private, voice-controlled AI assistant for macOS. Say **"Jarvis"** to wake it,
then speak naturally — it listens, understands intent, talks back, opens apps
and websites, searches the web, and remembers things you tell it.

- **Brain:** local LLM via [Ollama](https://ollama.com) (`gemma3:4b`) — no cloud, no API key required
- **Voice in:** offline speech recognition ([SpeechRecognition](https://pypi.org/project/SpeechRecognition/))
- **Wake word:** [openwakeword](https://pypi.org/project/openwakeword/) ("Jarvis")
- **Voice out (TTS):** ElevenLabs winning Jarvis voice when an API key is set, otherwise the local Kokoro voice — automatic fallback
- **Memory:** simple local JSON store
- **Skills:** open/close apps, open websites, web search (macOS via `open`/`osascript`)

> **Platform:** macOS only at runtime (uses `open`, `osascript`, `afplay`). The
> included `jarvis_v2/` and `jarvis/` directories are alternative versions — see
> [Included alternatives](#included-alternatives) below.

---

## Quick start

### 1. Install prerequisites

| Dependency | How |
|------------|-----|
| **Python 3.10+** | [python.org/downloads](https://www.python.org/downloads) |
| **Ollama** | [ollama.com/download](https://ollama.com/download) |
| **PortAudio** (for PyAudio) | `brew install portaudio` |

### 2. Get the code

```bash
git clone https://github.com/Lucasin23/JARVIS.git
cd JARVIS
```

### 3. Install Python dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 4. Pull the chat model (one-time, ~3 GB)

```bash
ollama pull gemma3:4b
```

Start Ollama if it is not running:

```bash
ollama serve
```

### 5. (Optional) Configure the ElevenLabs voice

Copy the env example and add your ElevenLabs API key to use the winning
Paul-Bettany-like Jarvis voice. When the key is absent, JARVIS automatically
falls back to the local Kokoro voice.

```bash
cp .env.example .env
# then edit .env and set: ELEVENLABS_API_KEY=...
```

Get a key at [elevenlabs.io → Developers](https://elevenlabs.io).

### 6. Verify your setup

```bash
python3 check_setup.py
```

This checks dependencies, module imports, and Ollama — without touching the
microphone.

### 7. Run JARVIS

Double-click **`run_jarvis.command`** in Finder, or from a terminal:

```bash
bash run_jarvis.sh
```

JARVIS calibrates the microphone, then listens. Say **"Jarvis"** to wake it,
then speak your request. Say **"shutdown"** to stop the conversation loop.

---

## Configuration

### Voice backends — `08_Configuration/voices.json`

| Key | Purpose |
|-----|---------|
| `active` | Which voice to use: `"elevenlabs"` or `"kokoro"` |
| `voices.kokoro` | Local Kokoro voice (`bm_george`) via `uv tool run kokoro-tts-tool` |
| `voices.elevenlabs` | ElevenLabs cloud TTS (`voice_id` `xbpwjFFJpcRThvL5EyVi`) |

The ElevenLabs voice is used automatically when `ELEVENLABS_API_KEY` is set;
otherwise JARVIS falls back to Kokoro. To force the local voice, set
`"active": "kokoro"`.

> The Kokoro backend requires [`uv`](https://docs.astral.sh/uv/) and runs
> `uv tool run kokoro-tts-tool synthesize ...`. If `uv` is not installed, install
> it or just use the ElevenLabs voice.

### Chat model — `01_Brain/brain.py`

The brain calls Ollama at `http://localhost:11434/api/chat` with the model
`gemma3:4b`. To use a different model, edit `01_Brain/brain.py` (the `_ask_ollama`
method) and `ollama pull` the new model.

### Environment — `.env`

| Variable | Required | Purpose |
|----------|----------|---------|
| `ELEVENLABS_API_KEY` | No | Enables the ElevenLabs Jarvis voice. Falls back to Kokoro if unset. |

---

## How it works

```
main.py
  ├── 02_Voice/wake.py        Wake-word detection (openwakeword + PyAudio)
  ├── 02_Voice/voice.py       Speech → text (SpeechRecognition + microphone)
  ├── 02_Voice/tts.py         Text → speech (ElevenLabs / Kokoro)
  ├── 01_Brain/brain.py       Intent + answers via Ollama (gemma3:4b)
  ├── 09_Skills/router.py     Command routing fallback
  ├── 09_Skills/apps.py       Open / close macOS apps
  ├── 09_Skills/browser.py    Open websites / web search
  └── 03_Memory/memory.py     Remember / recall facts (memory.json)
```

### Conversation commands

- **"Jarvis"** — wake word (say it anywhere in your sentence)
- **"remember that X is Y"** — store a fact
- **"what is my X?"** — recall a stored fact
- **"open [website]"** — opens it in the browser
- **"open [app]"** / **"close [app]"** — control macOS apps
- **"search [query]"** — Google search
- **"shutdown"** — exit the command loop

---

## Project structure

```
JARVIS/
├── main.py                 # Entry point — the prototype JARVIS
├── run_jarvis.command      # macOS double-click launcher
├── run_jarvis.sh           # Shell launcher with prerequisite checks
├── check_setup.py          # Verify deps + Ollama without a microphone
├── requirements.txt        # Python dependencies
├── .env.example             # Copy to .env and add your ElevenLabs key
├── 01_Brain/               # Ollama brain
├── 02_Voice/                # Wake word, STT, TTS
├── 03_Memory/               # Local JSON memory
├── 04_Vision/               # (stub) screen / vision
├── 05_Security/             # (stub) permission
├── 06_UI/                   # (stub) UI / status
├── 08_Configuration/       # voices.json, config
├── 09_Skills/               # App + browser skills
├── 10_Core/                 # (stub) core scaffolding
└── 11_Tools/                # (stub) tools
```

---

## Included alternatives

This repo also bundles two other JARVIS variants. The root prototype above is
the recommended starting point; these are kept for reference.

- **[`jarvis_v2/`](jarvis_v2/README.md)** — an advanced, modular macOS assistant
  with full system control (volume, brightness, dark mode, screenshots, shell
  execution, system monitoring, Git). Has its own `requirements.txt` and README.
- **[`jarvis/`](jarvis/README.md)** — a vendored copy of the upstream
  [`isair/jarvis`](https://github.com/isair/jarvis) production app: a 100% local,
  offline voice assistant with memory, MCP integration, and a desktop HUD.
  See its README for full setup.

---

## Troubleshooting

- **`ModuleNotFoundError: No module named 'pyaudio'`** — install PortAudio first:
  `brew install portaudio`, then `pip install -r requirements.txt`.
- **`Ollama is not running`** — start it with `ollama serve`.
- **`Chat model 'gemma3:4b' is not pulled`** — run `ollama pull gemma3:4b`.
- **No voice output** — without an ElevenLabs key you need `uv` installed for the
  Kokoro fallback: `brew install uv`.
- **Microphone not detected** — grant Terminal/iTerm microphone permission in
  macOS → System Settings → Privacy & Security → Microphone.
- **Wake word does not trigger** — openwakeword downloads its model on first
  run; ensure you have network access the first time, or pre-download the model.

---

## License

Personal use. See the included `jarvis/LICENSE` for the upstream project's terms.
