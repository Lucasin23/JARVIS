from __future__ import annotations
import json, threading
from pathlib import Path

class Memory:
    def __init__(self):
        self.path=Path(__file__).with_name("memory.json")
        self.lock=threading.Lock()
        self.data=self._load()

    def _load(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception: return {}

    def save(self):
        with self.lock:
            self.path.write_text(json.dumps(self.data,indent=2,ensure_ascii=False),encoding="utf-8")

    def remember(self,key,value):
        self.data[key.strip().lower()]=value.strip()
        self.save()

    def recall(self,key):
        return self.data.get(key.strip().lower())

    def all(self):
        return dict(self.data)
