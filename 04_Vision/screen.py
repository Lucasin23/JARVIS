from __future__ import annotations
import subprocess, tempfile, os
def screenshot(path=None):
    path=path or os.path.join(tempfile.gettempdir(),"jarvis_screen.png")
    subprocess.run(["screencapture","-x",path],check=False)
    return path
