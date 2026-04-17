import json
import os

CONFIG_PATH = "config.json"

DEFAULT = {
    "channels": {
        "world_map":     None,
        "world_events":  None,
        "turn_log":      None,
        "menu":          None,
        "commands":      None,
        "battle_reports":None,
        "leaderboard":   None,
        "public_log":    None,
        "gm_alerts":     None,
    },
    "gm_role":       None,
    "menu_message":  None,
    "setup_complete": False,
}

class ConfigManager:
    def __init__(self):
        if not os.path.exists(CONFIG_PATH):
            self._write(DEFAULT)
        self.data = self._read()

    def _read(self):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    def _write(self, data):
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=4)

    def get_channel(self, name):
        return self.data["channels"].get(name)

    def set_channel(self, name, channel_id):
        self.data["channels"][name] = channel_id
        self._write(self.data)

    def get_gm_role(self):
        return self.data.get("gm_role")

    def set_gm_role(self, role_id):
        self.data["gm_role"] = role_id
        self._write(self.data)

    def get_menu_message(self):
        return self.data.get("menu_message")

    def set_menu_message(self, message_id):
        self.data["menu_message"] = message_id
        self._write(self.data)

    def is_setup_complete(self):
        return self.data.get("setup_complete", False)

    def mark_setup_complete(self):
        self.data["setup_complete"] = True
        self._write(self.data)

    def get_missing_channels(self):
        return [k for k, v in self.data["channels"].items() if v is None]
