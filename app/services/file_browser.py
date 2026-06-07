from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.repo_scanner import IGNORE_DIRS, IGNORE_FILES


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts.intersection(IGNORE_DIRS):
        return True
    if path.name in IGNORE_FILES:
        return True
    return False


def build_file_tree(repo_path_str: str) -> list[dict[str, Any]]:
    repo_path = Path(repo_path_str).expanduser().resolve()

    if not repo_path.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")

    if not repo_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {repo_path}")

    items: list[dict[str, Any]] = []

    for path in sorted(repo_path.rglob("*")):
        if should_skip(path):
            continue

        try:
            relative_path = str(path.relative_to(repo_path))
        except Exception:
            continue

        depth = len(Path(relative_path).parts) - 1

        items.append(
            {
                "path": relative_path,
                "name": path.name,
                "type": "dir" if path.is_dir() else "file",
                "depth": depth,
            }
        )

    return items


def read_repo_file(repo_path_str: str, file_path: str, max_chars: int = 30000) -> dict[str, Any]:
    repo_path = Path(repo_path_str).expanduser().resolve()
    target = (repo_path / file_path).resolve()

    if not str(target).startswith(str(repo_path)):
        raise ValueError("Invalid file path")

    if not target.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not target.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    try:
        content = target.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        raise ValueError(f"Could not read file: {file_path}") from exc

    return {
        "file_path": file_path,
        "content": content[:max_chars],
        "truncated": len(content) > max_chars,
    }
