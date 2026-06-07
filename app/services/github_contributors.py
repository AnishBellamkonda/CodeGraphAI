from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from app.services.github_api import _github_get, _parse_owner_repo, list_pull_requests


def list_repository_contributors(repo_url: str, max_pages: int = 3) -> list[dict[str, Any]]:
    owner, repo, normalized = _parse_owner_repo(repo_url)
    contributors: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        data = _github_get(
            f"/repos/{owner}/{repo}/contributors",
            params={
                "per_page": 100,
                "page": page,
            },
        )

        if not data:
            break

        contributors.extend(data)

        if len(data) < 100:
            break

    return contributors


def _top_level_module(file_path: str) -> str:
    parts = Path(file_path).parts
    if not parts:
        return "root"
    first = parts[0]
    return first if first else "root"


def build_contributor_ownership_map(repo_url: str) -> dict[str, Any]:
    owner, repo, normalized = _parse_owner_repo(repo_url)

    contributors = list_repository_contributors(normalized, max_pages=3)
    pulls = list_pull_requests(normalized, state="all", max_pages=3)

    contributor_rows = []
    anonymous_contributors = 0

    for item in contributors:
        login = item.get("login")
        if not login:
            anonymous_contributors += 1

        contributor_rows.append(
            {
                "login": login or "anonymous",
                "contributions": item.get("contributions", 0),
                "html_url": item.get("html_url"),
                "type": item.get("type"),
            }
        )

    contributor_rows = sorted(
        contributor_rows,
        key=lambda x: x.get("contributions", 0),
        reverse=True,
    )

    top_contributors = contributor_rows[:12]

    total_contributions = sum(item.get("contributions", 0) for item in contributor_rows) or 1
    top_contributor_share = round(
        ((top_contributors[0]["contributions"] / total_contributions) * 100), 2
    ) if top_contributors else 0

    module_owner_map: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for pr in pulls[:60]:
        author = (pr.get("user") or {}).get("login")
        if not author:
            continue

        pr_number = pr.get("number")
        if not pr_number:
            continue

        try:
            files = _github_get(
                f"/repos/{owner}/{repo}/pulls/{pr_number}/files",
                params={"per_page": 100, "page": 1},
            )
        except Exception:
            files = []

        for file_item in files:
            filename = file_item.get("filename")
            if not filename:
                continue
            module = _top_level_module(filename)
            module_owner_map[module][author] += 1

    ownership_summary = []
    for module, owners in module_owner_map.items():
        sorted_owners = sorted(owners.items(), key=lambda kv: kv[1], reverse=True)
        top_owner, top_count = sorted_owners[0]
        ownership_summary.append(
            {
                "module": module,
                "top_owner": top_owner,
                "changed_files_or_pr_touches": top_count,
                "other_owners": [
                    {"login": login, "count": count}
                    for login, count in sorted_owners[1:4]
                ],
            }
        )

    ownership_summary = sorted(
        ownership_summary,
        key=lambda x: x["changed_files_or_pr_touches"],
        reverse=True,
    )[:12]

    if top_contributor_share >= 50:
        ownership_signal = "High concentration"
    elif top_contributor_share >= 30:
        ownership_signal = "Moderate concentration"
    else:
        ownership_signal = "Distributed"

    return {
        "repo": f"{owner}/{repo}",
        "repo_url": normalized,
        "top_contributors": top_contributors,
        "anonymous_contributors": anonymous_contributors,
        "ownership_summary": ownership_summary,
        "ownership_signal": ownership_signal,
        "top_contributor_share_percent": top_contributor_share,
        "notes": [
            "Contributor counts come from GitHub's contributors endpoint and may be slightly stale.",
            "Ownership is inferred heuristically from recent pull-request file touches, not from explicit CODEOWNERS rules.",
        ],
    }
