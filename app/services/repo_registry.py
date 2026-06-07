from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGISTRY_DIR = Path("./data")
REGISTRY_FILE = REGISTRY_DIR / "repo_registry.json"


def _ensure_registry() -> None:
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.write_text(json.dumps({}, indent=2))


def load_registry() -> dict[str, Any]:
    _ensure_registry()
    try:
        return json.loads(REGISTRY_FILE.read_text())
    except Exception:
        return {}


def save_registry(data: dict[str, Any]) -> None:
    _ensure_registry()
    REGISTRY_FILE.write_text(json.dumps(data, indent=2))


def get_repo_entry(repo_url: str) -> dict[str, Any] | None:
    registry = load_registry()
    return registry.get(repo_url)


def upsert_repo_entry(repo_url: str, entry: dict[str, Any]) -> None:
    registry = load_registry()
    registry[repo_url] = entry
    save_registry(registry)


def mark_repo_indexed(repo_url: str, indexed: bool = True) -> None:
    registry = load_registry()
    entry = registry.get(repo_url, {})
    entry["indexed"] = indexed
    registry[repo_url] = entry
    save_registry(registry)


def list_registered_repos() -> list[dict[str, Any]]:
    registry = load_registry()
    output = []
    for repo_url, data in registry.items():
        output.append(
            {
                "repo_url": repo_url,
                "local_repo_path": data.get("local_repo_path"),
                "indexed": data.get("indexed", False),
            }
        )
    return output
