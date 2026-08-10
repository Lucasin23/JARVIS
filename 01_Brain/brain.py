import urllib.request 
import json 

class JarvisBrain:
    def think(self, message):
        data = json.dumps({
    "model": "gemma3:1b",
    "messages": [
        {
            "role": "system",
            "content": "You are JARVIS, a fast intelligant personal AI assistant. Speak naturally, calmly, confidently and professionally. Keep answers short and direct. For simple questions, answer in one or two sentences if possible. Do not you bullet points unless specifically asked. Do not over-explain if not asked."
        },
        {
            "role": "user",
            "content": message
        }
    ],
    "stream": False,
    "keep_alive": "10m",
    "options": {
        "num_predict": 50
    }
}).encode("utf-8")

        request = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=data,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen (request) as response:
            result = json.loads(response.read().decode("utf-8"))

        return result["message"]["content"]