from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.deployment_readiness import build_deployment_readiness
from app.services.repo_loader import clone_github_repo, normalize_github_url
from app.services.test_coverage_heuristics import build_test_coverage_heuristics

DATA_DIR = Path("./data")
WATCH_FILE = DATA_DIR / "watchlist.json"


def _ensure_watch_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not WATCH_FILE.exists():
        WATCH_FILE.write_text("[]", encoding="utf-8")


def _read_watches() -> list[dict[str, Any]]:
    _ensure_watch_file()
    try:
        data = json.loads(WATCH_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def _write_watches(items: list[dict[str, Any]]) -> None:
    _ensure_watch_file()
    WATCH_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")


def create_watch(
    name: str,
    source_type: str,
    repo_path: str | None = None,
    repo_url: str | None = None,
    min_deployment_score: int = 60,
    min_test_coverage: float = 40.0,
    max_risky_untested: int = 10,
) -> dict[str, Any]:
    items = _read_watches()

    watch = {
        "id": str(uuid4()),
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "name": name,
        "source_type": source_type,
        "repo_path": repo_path,
        "repo_url": repo_url,
        "thresholds": {
            "min_deployment_score": min_deployment_score,
            "min_test_coverage": min_test_coverage,
            "max_risky_untested": max_risky_untested,
        },
    }

    items.insert(0, watch)
    _write_watches(items[:100])
    return watch


def list_watches() -> list[dict[str, Any]]:
    return _read_watches()


def delete_watch(watch_id: str) -> bool:
    items = _read_watches()
    updated = [item for item in items if item.get("id") != watch_id]
    changed = len(updated) != len(items)
    _write_watches(updated)
    return changed


def clear_watches() -> None:
    _write_watches([])


def _resolve_repo_path(watch: dict[str, Any], force_refresh_github: bool = False) -> str:
    source_type = watch.get("source_type")

    if source_type == "local":
        repo_path = watch.get("repo_path")
        if not repo_path:
            raise ValueError("Local watch is missing repo_path")
        return str(Path(repo_path).expanduser().resolve())

    if source_type == "github":
        repo_url = watch.get("repo_url")
        if not repo_url:
            raise ValueError("GitHub watch is missing repo_url")
        normalized = normalize_github_url(repo_url)
        return clone_github_repo(normalized, force_refresh=force_refresh_github)

    raise ValueError("Unsupported watch source_type. Use local or github.")


def evaluate_watch(watch: dict[str, Any], force_refresh_github: bool = False) -> dict[str, Any]:
    repo_path = _resolve_repo_path(watch, force_refresh_github=force_refresh_github)

    deployment = build_deployment_readiness(repo_path)
    tests = build_test_coverage_heuristics(repo_path)

    thresholds = watch.get("thresholds", {})
    min_deployment_score = thresholds.get("min_deployment_score", 60)
    min_test_coverage = thresholds.get("min_test_coverage", 40.0)
    max_risky_untested = thresholds.get("max_risky_untested", 10)

    alerts: list[dict[str, str]] = []

    if deployment["score"] < min_deployment_score:
        alerts.append({
            "severity": "high",
            "message": f"Deployment readiness score {deployment['score']} is below threshold {min_deployment_score}.",
        })

    coverage_pct = tests["counts"]["coverage_heuristic_percent"]
    if coverage_pct < min_test_coverage:
        alerts.append({
            "severity": "medium",
            "message": f"Test heuristic coverage {coverage_pct}% is below threshold {min_test_coverage}%.",
        })

    risky_untested_count = len(tests.get("risky_untested_files", []))
    if risky_untested_count > max_risky_untested:
        alerts.append({
            "severity": "high",
            "message": f"Risky untested files count {risky_untested_count} is above threshold {max_risky_untested}.",
        })

    if not tests.get("detected_test_frameworks"):
        alerts.append({
            "severity": "medium",
            "message": "No obvious test framework signal was detected.",
        })

    if not deployment.get("detected", {}).get("ci_cd_files"):
        alerts.append({
            "severity": "medium",
            "message": "No CI/CD workflow files were detected.",
        })

    status = "alert" if alerts else "ok"

    return {
        "id": watch["id"],
        "name": watch["name"],
        "source_type": watch["source_type"],
        "repo_path": repo_path,
        "repo_url": watch.get("repo_url"),
        "status": status,
        "deployment_score": deployment["score"],
        "deployment_level": deployment["level"],
        "test_coverage_percent": coverage_pct,
        "risky_untested_count": risky_untested_count,
        "alerts": alerts,
        "checked_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


def check_all_watches(force_refresh_github: bool = False) -> list[dict[str, Any]]:
    results = []
    for watch in _read_watches():
        try:
            results.append(evaluate_watch(watch, force_refresh_github=force_refresh_github))
        except Exception as exc:
            results.append({
                "id": watch.get("id"),
                "name": watch.get("name"),
                "source_type": watch.get("source_type"),
                "repo_path": watch.get("repo_path"),
                "repo_url": watch.get("repo_url"),
                "status": "error",
                "alerts": [{"severity": "high", "message": str(exc)}],
                "checked_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            })
    return results
