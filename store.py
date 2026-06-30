import json
import os

STORE_PATH = os.path.join(os.path.dirname(__file__), "submissions.json")


def _read() -> dict:
    if not os.path.exists(STORE_PATH):
        return {}
    with open(STORE_PATH, "r") as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return {}


def _write(data: dict) -> None:
    with open(STORE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def save_submission(record: dict) -> None:
    data = _read()
    data[record["content_id"]] = record
    _write(data)


def get_submission(content_id: str) -> dict | None:
    return _read().get(content_id)


def update_submission_status(content_id: str, status: str) -> bool:
    data = _read()
    if content_id not in data:
        return False
    data[content_id]["status"] = status
    _write(data)
    return True
