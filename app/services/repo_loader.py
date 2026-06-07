from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from app.services.repo_registry import get_repo_entry, upsert_repo_entry

CACHE_DIR = Path("./repo_cache")


def normalize_github_url(repo_url: str) -> str:
    repo_url = repo_url.strip()

    if repo_url.endswith("/"):
        repo_url = repo_url[:-1]

    parsed = urlparse(repo_url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("GitHub URL must start with http:// or https://")

    if "github.com" not in parsed.netloc.lower():
        raise ValueError("Only github.com URLs are supported right now")

    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) < 2:
        raise ValueError("GitHub URL must look like https://github.com/owner/repo")

    owner = path_parts[0]
    repo = path_parts[1]

    if repo.endswith(".git"):
        repo = repo[:-4]

    return f"https://github.com/{owner}/{repo}.git"


def _safe_repo_dir_name(repo_url: str) -> str:
    parsed = urlparse(repo_url)
    repo_name = Path(parsed.path).stem or "repo"
    digest = hashlib.md5(repo_url.encode("utf-8")).hexdigest()[:10]
    return f"{repo_name}_{digest}"


def clone_github_repo(repo_url: str, force_refresh: bool = False) -> str:
    normalized_url = normalize_github_url(repo_url)

    existing = get_repo_entry(normalized_url)
    if existing and existing.get("local_repo_path") and not force_refresh:
        local_path = Path(existing["local_repo_path"])
        if local_path.exists() and local_path.is_dir():
            return str(local_path.resolve())

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    repo_dir = CACHE_DIR / _safe_repo_dir_name(normalized_url)

    if repo_dir.exists():
        shutil.rmtree(repo_dir)

    cmd = [
        "git",
        "clone",
        "--depth",
        "1",
        normalized_url,
        str(repo_dir),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        stderr = result.stderr.strip() or "unknown git clone error"
        raise RuntimeError(f"Failed to clone repo: {stderr}")

    upsert_repo_entry(
        normalized_url,
        {
            "repo_url": normalized_url,
            "local_repo_path": str(repo_dir.resolve()),
            "indexed": False,
        },
    )

    return str(repo_dir.resolve())
