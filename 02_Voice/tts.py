"""
JARVIS Text-to-Speech router.

Two voice backends are configured in 08_Configuration/voices.json:

  - "kokoro"     : the original local JARVIS voice (Kokoro, "bm_george")
  - "elevenlabs" : ElevenLabs cloud TTS using the winning Jarvis voice
                  (voice_id xbpwjFFJpcRThvL5EyVi, Paul-Bettany-like)

The ElevenLabs voice is used when ELEVENLABS_API_KEY is set; otherwise JARVIS
gracefully falls back to the local Kokoro voice so the interface keeps talking.
The old voice is always available as a fallback — switch back to it anytime by
setting "active" to "kokoro" in 08_Configuration/voices.json.
"""

import json
import os
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

CONFIG_PATH = (
    Path(__file__).resolve().parent.parent / "08_Configuration" / "voices.json"
)


def _load_dotenv():
    """
    Minimal .env loader (no third-party dependency).
    Reads KEY=VALUE pairs from the project-root .env into os.environ so that
    copying .env.example to .env is enough to configure the ElevenLabs key.
    """
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        pass


_load_dotenv()

# Original Kokoro command — kept as the always-available fallback voice.
DEFAULT_KOKORO_COMMAND = [
    "uv", "tool", "run", "kokoro-tts-tool", "synthesize",
    "-v", "bm_george",
]


def _load_config():
    """Load the voice configuration, falling back to Kokoro if missing."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"active": "kokoro", "voices": {}}


def _kokoro_speak(text, speed="1.0"):
    """Speak using the original local Kokoro voice."""
    command = list(DEFAULT_KOKORO_COMMAND)
    if speed and speed != "1.0":
        command += ["--speed", speed]
    command.append(text)
    subprocess.run(command)


def _elevenlabs_speak(text, voice_config):
    """
    Speak using the winning ElevenLabs Jarvis voice.

    Returns True on success, False if the API key is missing or the request
    failed (so the caller can fall back to the local Kokoro voice).
    """
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        return False

    voice_id = voice_config.get("voice_id", "xbpwjFFJpcRThvL5EyVi")
    model_id = voice_config.get("model_id", "eleven_multilingual_v2")
    settings = voice_config.get("voice_settings", {})
    output_format = voice_config.get("output_format", "mp3_44100_128")

    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        f"?output_format={output_format}"
    )
    payload = json.dumps({
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": settings.get("stability", 0.75),
            "similarity_boost": settings.get("similarity_boost", 0.85),
            "style": settings.get("style", 0.0),
            "use_speaker_boost": settings.get("use_speaker_boost", True),
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            audio = resp.read()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        return False

    if not audio:
        return False

    # Play the generated audio. afplay ships with macOS.
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(audio)
        tmp_path = tmp.name

    try:
        subprocess.run(["afplay", tmp_path], check=False)
    except FileNotFoundError:
        # No afplay available → fall back to the local Kokoro voice.
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    return True


def speak(text, speed="1.0"):
    """Speak text using the configured voice backend."""
    if not text:
        return

    config = _load_config()
    active = config.get("active", "kokoro")
    voices = config.get("voices", {})

    if active == "elevenlabs" and "elevenlabs" in voices:
        if _elevenlabs_speak(text, voices["elevenlabs"]):
            return
        # No API key / request failed → fall back to the old Kokoro voice.
        _kokoro_speak(text, speed)
        return

    _kokoro_speak(text, speed)
