from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

DATA_DIR = Path("./data")
HISTORY_FILE = DATA_DIR / "history.json"


def _ensure_history_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def _read_history() -> list[dict[str, Any]]:
    _ensure_history_file()
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def _write_history(items: list[dict[str, Any]]) -> None:
    _ensure_history_file()
    HISTORY_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")


def append_history_event(
    event_type: str,
    source_type: str,
    label: str,
    repo_path: str | None = None,
    repo_url: str | None = None,
    payload_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    items = _read_history()

    event = {
        "id": str(uuid4()),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "event_type": event_type,
        "source_type": source_type,
        "label": label,
        "repo_path": repo_path,
        "repo_url": repo_url,
        "payload_summary": payload_summary or {},
    }

    items.insert(0, event)
    _write_history(items[:200])
    return event


def list_history(limit: int = 50) -> list[dict[str, Any]]:
    return _read_history()[:limit]


def clear_history() -> None:
    _write_history([])
