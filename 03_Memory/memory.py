import json
from pathlib import Path


class Memory:

    def __init__(self):
        self.file = Path(__file__).parent / "memory.json"
        self.data = self.load()

    def load(self):
        if self.file.exists():
            with open(self.file, "r", encoding="utf-8") as f:
                return json.load(f)

        return {}

    def save(self):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def remember(self, key, value):
        self.data[key] = value
        self.save()

    def recall(self, key):
        return self.data.get(key)

