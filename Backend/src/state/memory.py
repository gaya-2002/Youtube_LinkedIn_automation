import json
from pathlib import Path

class SharedState:
    _instance = None 

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
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    def set_chat_id(self,chat_id):
        self.state[chat_id]={}
        self._save()

    def get_keys(self):
        return self.state.keys()

    def set(self,chat_id, key, value):
        self.state[chat_id][key] = value
        self._save()

    def get(self, chat_id,key):
        return self.state.get(chat_id,{}).get(key,{})

    def all(self):
        return self.state
