# JARVIS — Apple Silicon Edition

A modular personal AI assistant for macOS / Apple Silicon.

## Features
- Real JARVIS HUD at `http://127.0.0.1:8765`
- Wake-word engine with speech fallback
- Mac microphone STT
- OpenAI/Ollama brain fallback
- Mac app control
- Safari web/search control
- Persistent memory
- Screenshot foundation
- ElevenLabs optional voice
- Low-dependency Apple Silicon design

## Install

```bash
xcode-select --install
brew install python@3.11 portaudio
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-mac.txt
cp .env.example .env
```

Add your API key to `.env`, then:

```bash
python main.py
```

Grant Terminal microphone permission in System Settings > Privacy & Security > Microphone.

For the strongest M1 setup, use a cloud LLM and keep local models small. The wake-word TFLite path is optional; if it fails on Apple Silicon, JARVIS automatically falls back to speech recognition.

## Commands
Say "Hey Jarvis", then:
- open YouTube
- open Safari
- search for Minecraft
- close Safari
- remember that my favorite color is red
- what is my favorite color
- normal questions
- shutdown
