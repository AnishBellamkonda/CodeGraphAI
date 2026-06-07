from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.dependency_insights import build_dependency_insights
from app.services.deployment_readiness import build_deployment_readiness
from app.services.history_store import list_history
from app.services.repo_registry import list_registered_repos
from app.services.repo_scanner import scan_repository
from app.services.test_coverage_heuristics import build_test_coverage_heuristics
from app.services.watch_mode import list_watches


def _repo_label(repo: dict[str, Any]) -> str:
    repo_url = repo.get("repo_url")
    if repo_url:
        return repo_url.replace("https://github.com/", "").replace(".git", "")
    local_path = repo.get("local_repo_path") or ""
    return Path(local_path).name if local_path else "unknown-repo"


def build_team_dashboard() -> dict[str, Any]:
    registered = list_registered_repos()
    watches = list_watches()
    history = list_history(limit=20)

    repo_cards: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for repo in registered:
        local_repo_path = repo.get("local_repo_path")
        repo_url = repo.get("repo_url")

        if not local_repo_path:
            errors.append({
                "repo": _repo_label(repo),
                "error": "Missing local_repo_path in registry entry.",
            })
            continue

        try:
            repo_path = str(Path(local_repo_path).expanduser().resolve())
            scan = scan_repository(repo_path)
            deployment = build_deployment_readiness(repo_path)
            tests = build_test_coverage_heuristics(repo_path)
            deps = build_dependency_insights(repo_path)

            matching_watches = [
                item for item in watches
                if (repo_url and item.get("repo_url") == repo_url)
                or (item.get("repo_path") and str(Path(item["repo_path"]).expanduser().resolve()) == repo_path)
            ]

            repo_cards.append({
                "label": _repo_label(repo),
                "repo_url": repo_url,
                "local_repo_path": repo_path,
                "indexed": repo.get("indexed", False),
                "total_files": scan.get("total_files", 0),
                "frameworks": scan.get("frameworks", []),
                "languages": scan.get("languages", {}),
                "package_managers": deps.get("package_managers", []),
                "deployment_score": deployment.get("score", 0),
                "deployment_level": deployment.get("level", "Unknown"),
                "test_coverage_percent": tests.get("counts", {}).get("coverage_heuristic_percent", 0.0),
                "risky_untested_count": len(tests.get("risky_untested_files", [])),
                "watch_count": len(matching_watches),
            })
        except Exception as exc:
            errors.append({
                "repo": _repo_label(repo),
                "error": str(exc),
            })

    total_repos = len(repo_cards)
    avg_deployment = round(
        sum(item["deployment_score"] for item in repo_cards) / total_repos, 2
    ) if total_repos else 0.0
    avg_test_coverage = round(
        sum(item["test_coverage_percent"] for item in repo_cards) / total_repos, 2
    ) if total_repos else 0.0

    weak_deployment = [item["label"] for item in repo_cards if item["deployment_score"] < 60][:10]
    low_tests = [item["label"] for item in repo_cards if item["test_coverage_percent"] < 40][:10]

    return {
        "summary": {
            "saved_repos": len(registered),
            "analyzed_repos": total_repos,
            "watch_count": len(watches),
            "history_events": len(history),
            "avg_deployment_score": avg_deployment,
            "avg_test_coverage_percent": avg_test_coverage,
            "repos_with_weak_deployment": weak_deployment,
            "repos_with_low_test_coverage": low_tests,
        },
        "repos": sorted(
            repo_cards,
            key=lambda x: (x["deployment_score"], x["test_coverage_percent"]),
            reverse=True,
        ),
        "watches": watches[:20],
        "recent_history": history[:12],
        "errors": errors[:20],
        "notes": [
            "This dashboard uses saved repos and local clone paths already known to the app.",
            "Scores are built from structural heuristics, not real runtime or CI execution.",
        ],
    }
