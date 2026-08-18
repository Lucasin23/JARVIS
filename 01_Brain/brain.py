from __future__ import annotations
import json, os, urllib.request, urllib.error

SYSTEM = """You are JARVIS, a concise, capable personal AI assistant running on a MacBook Pro with Apple Silicon.
Be calm, professional and helpful. You may explain actions, but never claim an action succeeded unless the tool reports success.
Keep ordinary answers short unless the user asks for detail."""

class JarvisBrain:
    def __init__(self):
        self.provider = os.getenv("JARVIS_LLM_PROVIDER", "openai").lower()

    def _openai(self, messages):
        key = os.getenv("OPENAI_API_KEY", "").strip()
        if not key:
            return None
        base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        body = json.dumps({"model": model, "messages": messages, "temperature": 0.4}).encode()
        req = urllib.request.Request(base + "/chat/completions", data=body,
            headers={"Content-Type":"application/json","Authorization":"Bearer "+key}, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()

    def _ollama(self, messages):
        base = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
        model = os.getenv("OLLAMA_MODEL", "gemma3:4b")
        body = json.dumps({"model": model, "messages": messages, "stream": False,
                           "keep_alive":"10m", "options":{"num_predict":300}}).encode()
        req = urllib.request.Request(base + "/api/chat", data=body,
            headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["message"]["content"].strip()

    def chat(self, text, history=None):
        messages = [{"role":"system","content":SYSTEM}]
        if history:
            messages.extend(history[-12:])
        messages.append({"role":"user","content":text})
        providers = [self.provider] + [p for p in ("openai","ollama") if p != self.provider]
        for p in providers:
            try:
                result = self._openai(messages) if p == "openai" else self._ollama(messages)
                if result:
                    return result
            except Exception:
                continue
        return "I’m online, but no language-model provider is configured. Add an OpenAI key or start Ollama."

    def classify(self, text):
        t = text.lower().strip()
        for prefix in ("open ", "launch ", "start "):
            if t.startswith(prefix):
                target=t[len(prefix):].strip()
                if target in {"youtube","google","spotify","github","safari","chrome"}:
                    return {"intent":"open","target":target}
        for prefix in ("search for ", "search google for ", "google "):
            if t.startswith(prefix):
                return {"intent":"search","target":text[len(prefix):].strip()}
        for prefix in ("close ", "quit "):
            if t.startswith(prefix):
                return {"intent":"close","target":text[len(prefix):].strip()}
        if t in {"show interface","open interface","show hud"}:
            return {"intent":"hud","target":""}
        return {"intent":"chat","target":text}
