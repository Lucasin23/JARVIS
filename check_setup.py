#!/usr/bin/env python3
"""
JARVIS setup checker — verifies that the root prototype can run.

It checks Python dependencies and the Ollama chat model WITHOUT touching the
microphone or starting the wake-word loop, so it is safe to run anytime.

Usage:
    python3 check_setup.py
"""
from __future__ import annotations

import importlib
import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
OLLAMA_URL = "http://localhost:11434"
CHAT_MODEL = "gemma3:4b"


def check_import(name: str) -> tuple[bool, str]:
    """Import a third-party module and report the installed version."""
    try:
        module = importlib.import_module(name)
    except Exception as error:  # noqa: BLE001 - any failure is a missing dep
        return False, f"missing — {error}"
    version = getattr(module, "__version__", "unknown")
    return True, version


def check_internal_modules() -> list[str]:
    """Confirm the digit-leading JARVIS packages resolve via importlib."""
    problems = []
    targets = [
        "01_Brain.brain",
        "02_Voice.voice",
        "02_Voice.wake",
        "02_Voice.tts",
        "03_Memory.memory",
        "09_Skills.router",
        "09_Skills.apps",
        "09_Skills.browser",
    ]
    for target in targets:
        try:
            importlib.import_module(target)
        except Exception as error:  # noqa: BLE001
            problems.append(f"  ✗ cannot import {target}: {error}")
    return problems


def check_ollama() -> list[str]:
    problems: list[str] = []
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3) as response:
            tags = json.loads(response.read().decode("utf-8"))
    except Exception:
        problems.append(
            f"  ✗ Ollama is not running at {OLLAMA_URL}. "
            "Start it with:  ollama serve"
        )
        return problems

    models = {model.get("name", "") for model in tags.get("models", [])}
    if not any(model.split(":")[0] == CHAT_MODEL.split(":")[0] for model in models):
        problems.append(
            f"  ✗ Chat model '{CHAT_MODEL}' is not pulled. "
            f"Run:  ollama pull {CHAT_MODEL}"
        )
    return problems


def main() -> int:
    print("JARVIS setup check\n" + "=" * 40)

    print("\nPython dependencies:")
    for name in ["speech_recognition", "pyaudio", "numpy", "openwakeword"]:
        ok, info = check_import(name)
        marker = "✓" if ok else "✗"
        print(f"  {marker} {name}: {info}")

    print("\nJARVIS modules:")
    module_problems = check_internal_modules()
    if module_problems:
        print("\n".join(module_problems))
    else:
        print("  ✓ all prototype modules import cleanly")

    print("\nOllama:")
    ollama_problems = check_ollama()
    if ollama_problems:
        print("\n".join(ollama_problems))
    else:
        print(f"  ✓ Ollama running with '{CHAT_MODEL}' available")

    print("\nVoice backends:")
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        has_key = "ELEVENLABS_API_KEY=" in env_path.read_text(encoding="utf-8")
        key_set = False
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("ELEVENLABS_API_KEY=") and len(line.split("=", 1)[1].strip()) > 0:
                key_set = True
        if key_set:
            print("  ✓ ElevenLabs API key set — using the winning Jarvis voice")
        else:
            print("  • ElevenLabs key not set — falling back to local Kokoro voice")
    else:
        print("  • No .env file — copy .env.example to .env to configure ElevenLabs")

    failed = bool(module_problems or ollama_problems)
    print("\n" + ("✗ Fix the issues above, then re-run." if failed else "✓ JARVIS is ready to launch with:  python3 main.py"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
