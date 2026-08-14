import urllib.request
import json


class JarvisBrain:

    def _ask_ollama(self, messages, num_predict=40):

        data = json.dumps({
            "model": "gemma3:4b",
            "messages": messages,
            "stream": False,
            "keep_alive": "10m",
            "options": {
                "num_predict": num_predict
            }
        }).encode("utf-8")

        request = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=data,
            headers={
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(request) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        return result["message"]["content"].strip()


    # -----------------------------------------
    # NORMAL AI RESPONSE
    # -----------------------------------------

    def think(self, message):

        messages = [
            {
                "role": "system",
                "content": (
                    "You are JARVIS, a fast and intelligent personal AI assistant. "
                    "Speak naturally, calmly and professionally. "
                    "Keep answers short, direct and useful. "
                    "For simple questions, answer in one or two sentences. "
                    "Do not use bullet points unless asked. "
                    "Do not over-explain."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ]

        return self._ask_ollama(messages, 40)


    # -----------------------------------------
    # COMMAND UNDERSTANDING
    # -----------------------------------------

    def understand_command(self, message):

        messages = [
            {
                "role": "system",
                "content": """
You are JARVIS's command parser.

Return ONLY valid JSON.

Allowed intents:
open_website
open_app
search_web
close_app
question

Examples:

User: open YouTube
{"intent":"open_website","target":"youtube"}

User: launch Safari
{"intent":"open_app","target":"safari"}

User: take me to Google
{"intent":"open_website","target":"google"}

User: search Google for Minecraft
{"intent":"search_web","target":"Minecraft"}

User: close Safari
{"intent":"close_app","target":"safari"}

User: what is the capital of Japan
{"intent":"question","target":"what is the capital of Japan"}

If the user asks a normal question, use "question".

Return ONLY JSON.
"""
            },
            {
                "role": "user",
                "content": message
            }
        ]

        response = self._ask_ollama(messages, 30)

        try:
            result = json.loads(response)

            if "intent" not in result or "target" not in result:
                return {
                    "intent": "question",
                    "target": message
                }

            return result

        except json.JSONDecodeError:

            return {
                "intent": "question",
                "target": message
            }