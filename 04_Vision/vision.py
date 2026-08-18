from __future__ import annotations
from .screen import screenshot
class JarvisVision:
    def capture(self): return screenshot()
    def describe(self, brain):
        path=self.capture()
        return brain.chat("A screenshot was captured at "+path+". Vision analysis is not connected yet; do not invent what is on screen.")
