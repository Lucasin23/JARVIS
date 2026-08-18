from __future__ import annotations
import importlib, os, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
Brain=importlib.import_module("01_Brain.brain").JarvisBrain
Voice=importlib.import_module("02_Voice.voice").JarvisVoice
Wake=importlib.import_module("02_Voice.wake").JarvisWake
speak=importlib.import_module("02_Voice.tts").speak
Memory=importlib.import_module("03_Memory.memory").Memory
Status=importlib.import_module("06_UI.status").Status
UI=importlib.import_module("06_UI.ui").UI
apps=importlib.import_module("09_Skills.apps")
browser=importlib.import_module("09_Skills.browser")
Permission=importlib.import_module("05_Security.permission").PermissionManager

class JarvisManager:
    def __init__(self):
        load_env=importlib.import_module('08_Configuration.config').load_env
        load_env()

        self.status=Status(); self.brain=Brain(); self.voice=Voice(); self.wake=Wake()
        self.memory=Memory(); self.ui=UI(self.status); self.perm=Permission()
        self.history=[]
    def say(self,text):
        self.status.set(state="speaking",response=text)
        print("JARVIS >",text); speak(text)
        self.status.set(state="idle")
    def handle(self,text):
        t=text.strip()
        if not t:return
        self.status.set(heard=t,state="thinking")
        low=t.lower()
        if low in {"shutdown","exit","quit","goodbye"}:
            self.say("Shutting down."); raise SystemExit
        if low.startswith("remember that ") and " is " in low:
            x=t[14:]; k,v=x.split(" is ",1); self.memory.remember(k,v); self.say(f"I'll remember that {k} is {v}."); return
        for p in ("what is my ","what's my ","do you remember my "):
            if low.startswith(p):
                k=t[len(p):].rstrip("?"); v=self.memory.recall(k)
                self.say(f"Your {k} is {v}." if v else f"I don't remember your {k}."); return
        c=self.brain.classify(t); intent,target=c["intent"],c["target"]
        if intent=="open":
            ok=browser.open_browser(target) if target in {"youtube","google","spotify","github","safari","chrome"} else apps.open_app(target)
            self.say(f"Opening {target}." if ok else f"I couldn't open {target}."); return
        if intent=="search":
            self.say("Searching."); browser.search_web(target); return
        if intent=="close":
            ok=apps.close_app(target); self.say("Okay." if ok else f"I couldn't close {target}."); return
        if intent=="hud":
            self.say("The interface is already online."); return
        response=self.brain.chat(target,self.history)
        self.history += [{"role":"user","content":t},{"role":"assistant","content":response}]
        self.history=self.history[-12:]
        self.status.set(state="idle",response=response)
        speak(response)
    def start(self):
        self.ui.start()
        self.status.set(state="idle",provider=os.getenv("JARVIS_LLM_PROVIDER","openai"),memory=len(self.memory.all()))
        self.say("Systems online. JARVIS is ready.")
        self.status.set(state="idle")
        try:
            while True:
                self.status.set(state="listening")
                activated=self.wake.wait_for_wake_word(self.voice)
                if not activated: continue
                self.say("Yes, sir?")
                command=self.voice.listen(timeout=8,phrase_time_limit=12)
                if command: self.handle(command)
        finally:
            self.wake.close()
