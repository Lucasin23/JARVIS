from __future__ import annotations
class Events:
    def __init__(self): self.listeners={}
    def on(self,name,fn): self.listeners.setdefault(name,[]).append(fn)
    def emit(self,name,**data):
        for fn in self.listeners.get(name,[]): fn(**data)
