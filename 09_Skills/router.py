from __future__ import annotations
def route(text):
    t=text.lower().strip()
    if t.startswith("remember that ") and " is " in t:
        x=t[14:]; k,v=x.split(" is ",1); return "remember",(k,v)
    for p in ("what is my ","what's my ","do you remember my "):
        if t.startswith(p): return "recall",t[len(p):].rstrip("?")
    return None,None
