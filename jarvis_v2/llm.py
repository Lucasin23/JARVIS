"""
LLM module - Optional AI conversation layer.
Uses OpenAI-compatible API for natural language responses when no built-in command matches.
Supports: OpenAI, Groq, Together AI, Ollama (local), and any OpenAI-compatible endpoint.
Falls back gracefully if no API key is configured.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SYSTEM_PROMPT = """You are JARVIS, a sophisticated AI assistant inspired by Iron Man's JARVIS.
You are witty, efficient, and loyal. Address the user as "sir" unless told otherwise.
Keep responses concise and helpful. You have a dry British sense of humor.
You can help with questions, writing, coding, explanations, calculations, and general knowledge.
When you don't know something, say so honestly.

You are running on the user's Mac and can control the system. If the user asks you to do
something you can't do through conversation (like opening an app or running a command),
suggest they phrase it as a direct command (e.g., 'open Safari', 'run command ls -la')."""

conversation_history: list[dict] = []

_api_key = os.getenv("OPENAI_API_KEY", "").strip()
_api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").strip()
_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

# Support local LLMs (Ollama, LM Studio, etc.) that don't need a real API key.
# If the base URL is localhost/127.0.0.1, treat it as available even without a key.
_is_local = "localhost" in _api_base or "127.0.0.1" in _api_base
_llm_available = bool(_api_key) or _is_local

# For local LLMs, set a dummy key if none provided
if _is_local and not _api_key:
    _api_key = "local"


def is_llm_available() -> bool:
    return _llm_available


def get_model_info() -> str:
    if not _llm_available:
        return "No LLM configured (set OPENAI_API_KEY in .env to enable AI responses)"
    return f"LLM: {_model} via {_api_base}"


def ask_llm(user_input: str) -> str:
    """
    Send user input to the LLM and get a response.
    Maintains conversation history for context.
    """
    if not _llm_available:
        return (
            "I'm not sure how to respond to that, sir. "
            "You can enable AI responses by setting OPENAI_API_KEY in the .env file. "
            "Type 'help' to see what I can do."
        )

    conversation_history.append({"role": "user", "content": user_input})

    if len(conversation_history) > 20:
        conversation_history[:] = conversation_history[-20:]

    try:
        from openai import OpenAI

        client = OpenAI(api_key=_api_key, base_url=_api_base)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

        response = client.chat.completions.create(
            model=_model,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        reply = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": reply})
        return reply

    except ImportError:
        return "The 'openai' package is not installed. Run: pip install openai"
    except Exception as e:
        if conversation_history and conversation_history[-1].get("content") == user_input:
            conversation_history.pop()
        return f"I encountered an error contacting the AI service: {e}"


def clear_history() -> None:
    conversation_history.clear()


def interpret_command(user_input: str) -> dict | None:
    """
    Use the LLM to interpret ambiguous natural language commands into
    structured actions JARVIS can execute.

    Returns a dict with 'command' and 'args', or None if LLM is unavailable.
    """
    if not _llm_available:
        return None

    interpretation_prompt = f"""Analyze this user request and determine if it maps to a system command.
Respond in JSON format only:
{{"action": "<command_type>", "args": "<parameters>"}}

Available actions:
- open_app: args = app name (e.g., "Safari")
- close_app: args = app name
- set_volume: args = number 0-100
- set_brightness: args = number 0-100
- toggle_dark_mode: args = ""
- sleep: args = ""
- lock_screen: args = ""
- screenshot: args = ""
- run_shell: args = shell command
- search_web: args = search query
- open_website: args = site name or URL
- weather: args = location
- play_music: args = ""
- pause_music: args = ""
- none: if it's a conversational question, not a system command

User request: "{user_input}"
Respond:"""

    try:
        from openai import OpenAI
        import json as _json

        client = OpenAI(api_key=_api_key, base_url=_api_base)
        response = client.chat.completions.create(
            model=_model,
            messages=[{"role": "user", "content": interpretation_prompt}],
            max_tokens=100,
            temperature=0,
        )

        result = response.choices[0].message.content.strip()
        # Parse JSON
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]

        return _json.loads(result)
    except Exception:
        return None
