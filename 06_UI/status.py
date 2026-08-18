from __future__ import annotations
import threading
class Status:
    def __init__(self):
        self.lock=threading.Lock()
        self.data={"state":"offline","heard":"","response":"","task":"","provider":"","memory":0}
    def set(self,**kwargs):
        with self.lock: self.data.update(kwargs)
    def get(self):
        with self.lock: return dict(self.data)
