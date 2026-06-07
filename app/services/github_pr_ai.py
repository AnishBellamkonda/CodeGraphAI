from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from app.services.github_api import get_pull_request_bundle

load_dotenv()


CRITICAL_PATH_HINTS = [
    "auth",
    "security",
    "permission",
    "role",
    "token",
    "secret",
    "login",
    "payment",
    "billing",
    "invoice",
    "checkout",
    "db",
    "database",
    "migration",
    "schema",
    "sql",
    "infra",
    "terraform",
    "docker",
    "k8s",
    "kubernetes",
    "helm",
    ".github/workflows",
    "config",
]


def _gemini_chat(prompt: str) -> str:
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing in .env")

    genai.configure(api_key=api_key)
    llm = genai.GenerativeModel(model)
    response = llm.generate_content(prompt)

    if hasattr(response, "text") and response.text:
        return response.text

    return "No response generated."


def _openai_chat(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing in .env")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert software architect and pull request reviewer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content or "No response generated."


def _risk_level(score: int) -> str:
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


def _compute_pr_risk(bundle: dict[str, Any]) -> dict[str, Any]:
    detail = bundle["detail"]
    files = bundle["files"]
    reviews = bundle["reviews"]
    requested = bundle["requested_reviewers"]

    changed_files = detail.get("changed_files") or len(files)
    additions = detail.get("additions") or 0
    deletions = detail.get("deletions") or 0
    commits = detail.get("commits") or 0

    filenames = [item.get("filename", "") for item in files]
    lowered = [name.lower() for name in filenames]

    critical_paths = sorted(
        {name for name in filenames if any(hint in name.lower() for hint in CRITICAL_PATH_HINTS)}
    )

    tests_touched = any(
        "test" in name.lower() or "spec" in name.lower()
        for name in filenames
    )

    approved_reviews = sum(1 for review in reviews if review.get("state") == "APPROVED")
    requested_users = requested.get("users", [])
    requested_teams = requested.get("teams", [])

    score = 0
    reasons = []

    if changed_files >= 25:
        score += 25
        reasons.append("Large number of files changed")
    elif changed_files >= 10:
        score += 12
        reasons.append("Moderate number of files changed")

    total_line_delta = additions + deletions
    if total_line_delta >= 1500:
        score += 25
        reasons.append("Very large code delta")
    elif total_line_delta >= 500:
        score += 12
        reasons.append("Moderate code delta")

    if commits >= 10:
        score += 10
        reasons.append("Many commits in a single PR")
    elif commits >= 5:
        score += 5
        reasons.append("Several commits in this PR")

    if critical_paths:
        score += 20
        reasons.append("Touches critical or sensitive paths")

    if not tests_touched and changed_files >= 5:
        score += 10
        reasons.append("No obvious test files changed")

    if approved_reviews == 0:
        score += 8
        reasons.append("No approvals yet")

    if len(requested_users) + len(requested_teams) == 0:
        score += 5
        reasons.append("No reviewers requested")

    if detail.get("draft"):
        score = max(score - 5, 0)

    score = min(score, 100)

    return {
        "score": score,
        "level": _risk_level(score),
        "critical_paths": critical_paths[:20],
        "tests_touched": tests_touched,
        "approved_reviews": approved_reviews,
        "requested_reviewers": {
            "users": [user.get("login") for user in requested_users],
            "teams": [team.get("name") for team in requested_teams],
        },
        "reasons": reasons,
    }


def _build_pr_prompt(bundle: dict[str, Any], risk: dict[str, Any]) -> str:
    detail = bundle["detail"]
    files = bundle["files"]
    reviews = bundle["reviews"]
    requested = bundle["requested_reviewers"]

    file_summary_lines = []
    for item in files[:40]:
        file_summary_lines.append(
            f"- {item.get('filename')} | status={item.get('status')} | additions={item.get('additions')} | deletions={item.get('deletions')}"
        )

    review_lines = []
    for review in reviews[:20]:
        review_lines.append(
            f"- reviewer={((review.get('user') or {}).get('login'))} | state={review.get('state')} | submitted_at={review.get('submitted_at')}"
        )

    requested_users = [user.get("login") for user in requested.get("users", [])]
    requested_teams = [team.get("name") for team in requested.get("teams", [])]

    return f"""
You are an expert software engineer reviewing a pull request.

Analyze this pull request and write a grounded technical summary.

Pull request:
- Number: {detail.get("number")}
- Title: {detail.get("title")}
- State: {detail.get("state")}
- Draft: {detail.get("draft")}
- Author: {(detail.get("user") or {}).get("login")}
- Created at: {detail.get("created_at")}
- Updated at: {detail.get("updated_at")}
- Merged at: {detail.get("merged_at")}
- Changed files: {detail.get("changed_files")}
- Additions: {detail.get("additions")}
- Deletions: {detail.get("deletions")}
- Commits: {detail.get("commits")}
- Body:
{detail.get("body") or "No PR description provided."}

Risk signals:
- Risk score: {risk["score"]}
- Risk level: {risk["level"]}
- Critical paths: {risk["critical_paths"]}
- Tests touched: {risk["tests_touched"]}
- Approved reviews: {risk["approved_reviews"]}
- Requested reviewers (users): {requested_users}
- Requested reviewers (teams): {requested_teams}
- Risk reasons: {risk["reasons"]}

Changed files:
{chr(10).join(file_summary_lines)}

Reviews:
{chr(10).join(review_lines) if review_lines else "No reviews yet."}

Return exactly these sections:

1. PR Summary
2. Impacted Areas
3. Risk Assessment
4. Review Checklist
5. Suggested Tests
6. Unknowns / Missing Context

Keep it practical, concise, and grounded in the provided data.
Do not invent implementation details that are not visible here.
""".strip()


def _mock_pr_analysis(bundle: dict[str, Any], risk: dict[str, Any]) -> str:
    detail = bundle["detail"]
    files = bundle["files"]

    top_files = "\n".join(f"- {item.get('filename')}" for item in files[:10]) or "- No files found"

    return f"""
1. PR Summary
This PR appears to update {detail.get("changed_files")} files with {detail.get("additions")} additions and {detail.get("deletions")} deletions across {detail.get("commits")} commits. Title: {detail.get("title")}.

2. Impacted Areas
Likely impacted files and modules:
{top_files}

3. Risk Assessment
The current heuristic risk score is {risk["score"]} ({risk["level"]}). Main reasons: {", ".join(risk["reasons"]) if risk["reasons"] else "No major risk signals detected"}.

4. Review Checklist
- Verify correctness of core file changes
- Validate edge cases in modified flows
- Confirm reviewer coverage on sensitive paths
- Check if tests are sufficient

5. Suggested Tests
- Re-run unit and integration coverage around changed modules
- Test the highest-churn files first
- Validate critical-path behavior if auth, database, payment, or infra files changed

6. Unknowns / Missing Context
This is a mock-mode analysis. Retrieval and risk scoring are real, but the final AI explanation is placeholder text until OpenAI or Gemini is enabled.
""".strip()


def analyze_pull_request(repo_url: str, pull_number: int) -> dict[str, Any]:
    bundle = get_pull_request_bundle(repo_url, pull_number)
    risk = _compute_pr_risk(bundle)

    provider = os.getenv("AI_PROVIDER", "mock").lower()
    prompt = _build_pr_prompt(bundle, risk)

    if provider == "mock":
        ai_summary = _mock_pr_analysis(bundle, risk)
    elif provider == "openai":
        ai_summary = _openai_chat(prompt)
    elif provider == "gemini":
        ai_summary = _gemini_chat(prompt)
    else:
        raise ValueError("Unsupported AI_PROVIDER. Use mock, openai, or gemini.")

    detail = bundle["detail"]
    files = bundle["files"]

    return {
        "repo_url": bundle["repo_url"],
        "pull_number": pull_number,
        "title": detail.get("title"),
        "author": (detail.get("user") or {}).get("login"),
        "state": detail.get("state"),
        "draft": detail.get("draft"),
        "html_url": detail.get("html_url"),
        "stats": {
            "changed_files": detail.get("changed_files"),
            "additions": detail.get("additions"),
            "deletions": detail.get("deletions"),
            "commits": detail.get("commits"),
            "reviews": len(bundle["reviews"]),
        },
        "risk": risk,
        "top_files": [item.get("filename") for item in files[:20]],
        "ai_summary": ai_summary,
    }
