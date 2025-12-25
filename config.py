import json
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

def load_config():
    if not CONFIG_FILE.exists():
        # Fallback defaults if config.json is missing
        return {
            "EXTENSION_MAP": {
                "Documents": [".pdf", ".docx", ".doc", ".txt"],
                "Images": [".jpg", ".png", ".jpeg"],
                "Others": []
            },
            "RETENTION_POLICIES": {},
            "OTHERS_FOLDER": "Others",
            "LOG_FILENAME": "triage.log"
        }
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

_config = load_config()

EXTENSION_MAP = _config.get("EXTENSION_MAP", {})
RETENTION_POLICIES = _config.get("RETENTION_POLICIES", {})
OTHERS_FOLDER = _config.get("OTHERS_FOLDER", "Others")
LOG_FILENAME = _config.get("LOG_FILENAME", "triage.log")
