from __future__ import annotations
class Context:
    def __init__(self): self.history=[]
    def add(self,user,assistant): self.history += [{"role":"user","content":user},{"role":"assistant","content":assistant}]
