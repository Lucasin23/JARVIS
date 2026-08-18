from __future__ import annotations
import time
from importlib import import_module
JarvisManager = import_module('10_Core.manager').JarvisManager

# import JarvisManager

if __name__ == "__main__":
    manager = JarvisManager()
    manager.start()
