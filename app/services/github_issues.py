from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from app.services.github_api import _github_get, _parse_owner_repo


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def list_repository_issues(repo_url: str, state: str = "open", max_pages: int = 3) -> list[dict[str, Any]]:
    owner, repo, normalized = _parse_owner_repo(repo_url)
    issues: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        data = _github_get(
            f"/repos/{owner}/{repo}/issues",
            params={
                "state": state,
                "sort": "updated",
                "direction": "desc",
                "per_page": 100,
                "page": page,
            },
        )

        if not data:
            break

        # GitHub issues endpoints may include pull requests; filter them out.
        filtered = [item for item in data if "pull_request" not in item]
        issues.extend(filtered)

        if len(data) < 100:
            break

    return issues


def build_issue_dashboard(repo_url: str) -> dict[str, Any]:
    owner, repo, normalized = _parse_owner_repo(repo_url)
    issues = list_repository_issues(normalized, state="open", max_pages=3)

    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=30)

    stale_issues = []
    unlabeled_count = 0
    unassigned_count = 0

    label_counter: Counter[str] = Counter()
    assignee_counter: Counter[str] = Counter()

    recent_issues = []

    for issue in issues:
        updated_at = _parse_datetime(issue.get("updated_at"))
        if updated_at and updated_at < stale_cutoff:
            stale_issues.append(issue)

        labels = issue.get("labels", []) or []
        assignees = issue.get("assignees", []) or []

        if not labels:
            unlabeled_count += 1
        if not assignees:
            unassigned_count += 1

        for label in labels:
            name = label.get("name")
            if name:
                label_counter[name] += 1

        for assignee in assignees:
            login = assignee.get("login")
            if login:
                assignee_counter[login] += 1

        recent_issues.append(
            {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "updated_at": issue.get("updated_at"),
                "created_at": issue.get("created_at"),
                "comments": issue.get("comments"),
                "labels": [label.get("name") for label in labels if label.get("name")],
                "assignees": [assignee.get("login") for assignee in assignees if assignee.get("login")],
                "html_url": issue.get("html_url"),
            }
        )

    top_labels = [
        {"label": name, "count": count}
        for name, count in label_counter.most_common(10)
    ]

    top_assignees = [
        {"assignee": name, "count": count}
        for name, count in assignee_counter.most_common(10)
    ]

    return {
        "repo": f"{owner}/{repo}",
        "repo_url": normalized,
        "counts": {
            "open_issues_sampled": len(issues),
            "stale_issues": len(stale_issues),
            "unlabeled_issues": unlabeled_count,
            "unassigned_issues": unassigned_count,
        },
        "top_labels": top_labels,
        "top_assignees": top_assignees,
        "recent_issues": recent_issues[:15],
        "stale_issue_titles": [issue.get("title") for issue in stale_issues[:10]],
        "notes": [
            "Repository issues were filtered to exclude pull requests.",
            "Stale issues are defined here as open issues not updated in the last 30 days.",
        ],
    }
