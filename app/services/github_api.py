from __future__ import annotations

import os
from collections import Counter
from datetime import datetime
from typing import Any

import requests
from dotenv import load_dotenv

from app.services.repo_loader import normalize_github_url

load_dotenv()

API_BASE = "https://api.github.com"
API_VERSION = "2026-03-10"


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_owner_repo(repo_url: str) -> tuple[str, str, str]:
    normalized = normalize_github_url(repo_url)
    suffix = normalized.replace("https://github.com/", "").replace(".git", "")
    owner, repo = suffix.split("/", 1)
    return owner, repo, normalized


def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": "CodeGraph-AI",
    }

    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def _rate_limit_mode() -> str:
    return "authenticated" if os.getenv("GITHUB_TOKEN", "").strip() else "unauthenticated"


def _github_get(path: str, params: dict[str, Any] | None = None) -> Any:
    url = f"{API_BASE}{path}"
    response = requests.get(url, headers=_github_headers(), params=params, timeout=60)

    if response.status_code >= 400:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise RuntimeError(f"GitHub API error {response.status_code}: {detail}")

    return response.json()


def list_pull_requests(repo_url: str, state: str = "all", max_pages: int = 5) -> list[dict[str, Any]]:
    owner, repo, _ = _parse_owner_repo(repo_url)
    pulls: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        data = _github_get(
            f"/repos/{owner}/{repo}/pulls",
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

        pulls.extend(data)

        if len(data) < 100:
            break

    return pulls


def get_pull_request_detail(repo_url: str, pull_number: int) -> dict[str, Any]:
    owner, repo, _ = _parse_owner_repo(repo_url)
    return _github_get(f"/repos/{owner}/{repo}/pulls/{pull_number}")


def list_pull_request_files(repo_url: str, pull_number: int, max_pages: int = 10) -> list[dict[str, Any]]:
    owner, repo, _ = _parse_owner_repo(repo_url)
    files: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        data = _github_get(
            f"/repos/{owner}/{repo}/pulls/{pull_number}/files",
            params={"per_page": 100, "page": page},
        )

        if not data:
            break

        files.extend(data)

        if len(data) < 100:
            break

    return files


def list_pull_request_reviews(repo_url: str, pull_number: int) -> list[dict[str, Any]]:
    owner, repo, _ = _parse_owner_repo(repo_url)
    return _github_get(f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews")


def get_requested_reviewers(repo_url: str, pull_number: int) -> dict[str, Any]:
    owner, repo, _ = _parse_owner_repo(repo_url)
    return _github_get(f"/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers")


def get_pull_request_bundle(repo_url: str, pull_number: int) -> dict[str, Any]:
    owner, repo, normalized = _parse_owner_repo(repo_url)

    detail = get_pull_request_detail(normalized, pull_number)
    files = list_pull_request_files(normalized, pull_number, max_pages=10)
    reviews = list_pull_request_reviews(normalized, pull_number)
    requested_reviewers = get_requested_reviewers(normalized, pull_number)

    return {
        "repo": f"{owner}/{repo}",
        "repo_url": normalized,
        "detail": detail,
        "files": files,
        "reviews": reviews,
        "requested_reviewers": requested_reviewers,
        "rate_limit_mode": _rate_limit_mode(),
    }


def build_pull_request_dashboard(repo_url: str) -> dict[str, Any]:
    owner, repo, normalized = _parse_owner_repo(repo_url)
    pulls = list_pull_requests(normalized, state="all", max_pages=5)

    open_count = sum(1 for pr in pulls if pr.get("state") == "open")
    merged_count = sum(1 for pr in pulls if pr.get("merged_at"))
    closed_without_merge = sum(
        1 for pr in pulls if pr.get("state") == "closed" and not pr.get("merged_at")
    )
    draft_count = sum(1 for pr in pulls if pr.get("draft"))

    merged_durations = []
    for pr in pulls:
        created_at = _parse_datetime(pr.get("created_at"))
        merged_at = _parse_datetime(pr.get("merged_at"))
        if created_at and merged_at:
            merged_durations.append((merged_at - created_at).total_seconds() / 3600)

    average_merge_hours = round(sum(merged_durations) / len(merged_durations), 2) if merged_durations else None

    author_counts = Counter(
        pr["user"]["login"]
        for pr in pulls
        if pr.get("user") and pr["user"].get("login")
    )

    top_authors = [
        {"author": login, "pull_requests": count}
        for login, count in author_counts.most_common(8)
    ]

    detail_cache: dict[int, dict[str, Any]] = {}
    for pr in pulls[:10]:
        number = pr.get("number")
        if number is not None:
            try:
                detail_cache[number] = get_pull_request_detail(normalized, number)
            except Exception:
                detail_cache[number] = {}

    recent_pull_requests = []
    for pr in pulls[:10]:
        number = pr.get("number")
        detail = detail_cache.get(number, {})

        recent_pull_requests.append(
            {
                "number": number,
                "title": pr.get("title"),
                "state": pr.get("state"),
                "draft": pr.get("draft", False),
                "author": (pr.get("user") or {}).get("login"),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
                "merged_at": pr.get("merged_at"),
                "additions": detail.get("additions"),
                "deletions": detail.get("deletions"),
                "changed_files": detail.get("changed_files"),
                "commits": detail.get("commits"),
                "html_url": pr.get("html_url"),
            }
        )

    largest_recent_pull_requests = sorted(
        [item for item in recent_pull_requests if item.get("changed_files") is not None],
        key=lambda item: item.get("changed_files") or 0,
        reverse=True,
    )[:5]

    return {
        "repo": f"{owner}/{repo}",
        "repo_url": normalized,
        "sampled_pull_requests": len(pulls),
        "rate_limit_mode": _rate_limit_mode(),
        "counts": {
            "total_sampled_prs": len(pulls),
            "open_prs": open_count,
            "merged_prs": merged_count,
            "closed_without_merge": closed_without_merge,
            "draft_prs": draft_count,
        },
        "average_merge_hours": average_merge_hours,
        "top_authors": top_authors,
        "recent_pull_requests": recent_pull_requests,
        "largest_recent_pull_requests": largest_recent_pull_requests,
        "notes": [
            "Counts are based on the most recent pull requests fetched from GitHub.",
            "Add GITHUB_TOKEN in .env for better rate limits and private repo support.",
        ],
    }
