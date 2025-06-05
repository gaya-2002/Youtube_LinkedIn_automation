import json
from pathlib import Path

class SharedState:
    _instance = None  # Singleton instance

    def __new__(cls,filename=str(Path(__file__).parent) + r"\state.json"):
        if cls._instance is None:
            cls._instance = super(SharedState, cls).__new__(cls)
            cls._instance.filename = filename
            cls._instance.state = cls._instance._load()
        return cls._instance

    def _load(self):
        try:
            with open(self.filename, "r", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            with open(self.filename,"w",encoding='utf-8') as f:
                pass
            return {}

    def _save(self):
        with open(self.filename, "w") as f:
            json.dump(self.state, f, indent=2)

    def set(self, key, value):
        self.state[key] = value
        self._save()

    def get(self, key):
        return self.state.get(key)

    def all(self):
        return self.state
