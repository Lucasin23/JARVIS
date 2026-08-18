from __future__ import annotations
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
def load_env():
    p=ROOT/".env"
    if p.exists():
        for line in p.read_text().splitlines():
            line=line.strip()
            if line and not line.startswith("#") and "=" in line:
                k,v=line.split("=",1)
                os.environ.setdefault(k.strip(),v.strip().strip('"').strip("'"))
load_env()
