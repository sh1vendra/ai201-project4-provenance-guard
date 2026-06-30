import json
import os
from datetime import datetime, timezone

LOG_PATH = os.path.join(os.path.dirname(__file__), "audit_log.json")


def _read_log() -> list:
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r") as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []


def log_entry(entry: dict) -> None:
    entries = _read_log()
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    entries.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(entries, f, indent=2)


def get_log(limit: int = 20) -> list:
    entries = _read_log()
    return list(reversed(entries))[:limit]
