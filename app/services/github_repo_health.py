from __future__ import annotations

from typing import Any

from app.services.github_api import _github_get, _parse_owner_repo, build_pull_request_dashboard


def list_recent_issues(repo_url: str, max_pages: int = 3) -> list[dict[str, Any]]:
    owner, repo, normalized = _parse_owner_repo(repo_url)
    issues: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        data = _github_get(
            f"/repos/{owner}/{repo}/issues",
            params={
                "state": "open",
                "sort": "updated",
                "direction": "desc",
                "per_page": 100,
                "page": page,
            },
        )

        if not data:
            break

        # GitHub issues endpoint includes PRs too; filter them out
        data = [item for item in data if "pull_request" not in item]
        issues.extend(data)

        if len(data) < 100:
            break

    return issues


def get_repo_stats(repo_url: str) -> dict[str, Any]:
    owner, repo, normalized = _parse_owner_repo(repo_url)
    data = _github_get(f"/repos/{owner}/{repo}")

    return {
        "repo": f"{owner}/{repo}",
        "repo_url": normalized,
        "stargazers_count": data.get("stargazers_count"),
        "forks_count": data.get("forks_count"),
        "open_issues_count": data.get("open_issues_count"),
        "watchers_count": data.get("watchers_count"),
        "default_branch": data.get("default_branch"),
        "updated_at": data.get("updated_at"),
        "pushed_at": data.get("pushed_at"),
        "language": data.get("language"),
    }


def compute_release_readiness(repo_url: str) -> dict[str, Any]:
    pr_dashboard = build_pull_request_dashboard(repo_url)
    repo_stats = get_repo_stats(repo_url)
    open_issues = list_recent_issues(repo_url, max_pages=2)

    score = 100
    reasons = []
    actions = []

    open_prs = pr_dashboard["counts"]["open_prs"]
    draft_prs = pr_dashboard["counts"]["draft_prs"]
    closed_without_merge = pr_dashboard["counts"]["closed_without_merge"]
    avg_merge_hours = pr_dashboard.get("average_merge_hours")
    open_issue_count = len(open_issues)

    if open_prs >= 30:
        score -= 25
        reasons.append("Large number of open pull requests")
        actions.append("Reduce PR backlog before release")
    elif open_prs >= 10:
        score -= 12
        reasons.append("Moderate open pull request backlog")
        actions.append("Review pending pull requests")

    if draft_prs >= 10:
        score -= 12
        reasons.append("Many draft pull requests are still in progress")
        actions.append("Finalize or close unfinished PRs")
    elif draft_prs >= 3:
        score -= 6
        reasons.append("Several draft pull requests still open")

    if closed_without_merge >= 10:
        score -= 8
        reasons.append("High number of recently closed unmerged pull requests")

    if avg_merge_hours is not None:
        if avg_merge_hours >= 96:
            score -= 10
            reasons.append("Slow pull request merge turnaround")
            actions.append("Improve review speed on active PRs")
        elif avg_merge_hours >= 48:
            score -= 5
            reasons.append("Moderate pull request merge delays")

    if open_issue_count >= 100:
        score -= 20
        reasons.append("Large number of open issues")
        actions.append("Triage active open issues before release")
    elif open_issue_count >= 25:
        score -= 10
        reasons.append("Moderate number of open issues")

    recent_prs = pr_dashboard.get("recent_pull_requests", [])
    largest_recent = pr_dashboard.get("largest_recent_pull_requests", [])

    if largest_recent:
        if any((pr.get("changed_files") or 0) >= 50 for pr in largest_recent):
            score -= 12
            reasons.append("Recent very large pull requests increase release risk")
            actions.append("Review large PRs carefully before rollout")
        elif any((pr.get("changed_files") or 0) >= 20 for pr in largest_recent):
            score -= 6
            reasons.append("Recent large pull requests may affect release confidence")

    if recent_prs:
        if any(pr.get("draft") for pr in recent_prs[:5]):
            score -= 4
            reasons.append("Recent PR activity includes draft work")

    score = max(score, 0)

    if score >= 85:
        level = "Ready"
    elif score >= 65:
        level = "Watch"
    elif score >= 40:
        level = "Risky"
    else:
        level = "Blocked"

    if not reasons:
        reasons.append("No major release blockers detected in current repository signals")

    if not actions:
        actions.append("Continue standard review and validation before release")

    return {
        "repo": repo_stats["repo"],
        "repo_url": repo_stats["repo_url"],
        "score": score,
        "level": level,
        "signals": {
            "open_prs": open_prs,
            "draft_prs": draft_prs,
            "closed_without_merge": closed_without_merge,
            "average_merge_hours": avg_merge_hours,
            "recent_open_issues_sampled": open_issue_count,
            "repo_open_issues_count": repo_stats["open_issues_count"],
            "updated_at": repo_stats["updated_at"],
            "pushed_at": repo_stats["pushed_at"],
            "default_branch": repo_stats["default_branch"],
            "primary_language": repo_stats["language"],
        },
        "reasons": reasons,
        "recommended_actions": actions,
        "top_recent_issue_titles": [item.get("title") for item in open_issues[:10]],
        "pr_dashboard": pr_dashboard,
    }
