from __future__ import annotations
import subprocess
ALIASES={"vs code":"Visual Studio Code","vscode":"Visual Studio Code","code":"Visual Studio Code"}
def norm(name): return ALIASES.get(name.lower().strip(),name.strip())
def open_app(name):
    try: subprocess.run(["open","-a",norm(name)],check=True); return True
    except Exception:return False
def close_app(name):
    try: subprocess.run(["osascript","-e",f'tell application "{norm(name)}" to quit'],check=True); return True
    except Exception:return False
