from __future__ import annotations

from typing import Any

from app.services.architecture_map import build_architecture_map
from app.services.repo_scanner import scan_repository


def _unique_keep_order(items: list[str]) -> list[str]:
    seen = set()
    output = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output


def _pick_first_files(architecture_map: dict[str, Any]) -> list[str]:
    files = []

    files.extend(architecture_map.get("docs", [])[:3])
    files.extend(architecture_map.get("entry_points", [])[:3])
    files.extend(architecture_map.get("config_infra", [])[:3])
    files.extend(architecture_map.get("api_routes", [])[:4])
    files.extend(architecture_map.get("services", [])[:4])
    files.extend(architecture_map.get("data_access", [])[:3])
    files.extend(architecture_map.get("data_models", [])[:3])
    files.extend(architecture_map.get("frontend", [])[:3])
    files.extend(architecture_map.get("tests", [])[:3])

    return _unique_keep_order(files)[:15]


def _build_learning_path(architecture_map: dict[str, Any]) -> list[str]:
    steps = []

    if architecture_map.get("docs"):
        steps.append("Start with README/docs to understand project purpose, setup, and developer workflow.")

    if architecture_map.get("entry_points"):
        steps.append("Read the entry-point files next to see how the application starts and which modules are wired first.")

    if architecture_map.get("config_infra"):
        steps.append("Review config/infrastructure files to understand runtime settings, environments, and deployment assumptions.")

    if architecture_map.get("api_routes"):
        steps.append("Move to API routes/controllers to understand how requests enter the system.")

    if architecture_map.get("services"):
        steps.append("Read the service layer after that to understand business logic and orchestration.")

    if architecture_map.get("data_access") or architecture_map.get("data_models"):
        steps.append("Then inspect data-access and model files to understand persistence, schemas, and domain objects.")

    if architecture_map.get("frontend"):
        steps.append("If this repo has UI code, read the frontend/pages/components after backend flow is clear.")

    if architecture_map.get("tests"):
        steps.append("Finish with tests to understand expected behavior, edge cases, and validation strategy.")

    if not steps:
        steps.append("No strong structure pattern was detected, so start with the top modules and main source files first.")

    return steps


def _build_focus_areas(architecture_map: dict[str, Any], scan_result: dict[str, Any]) -> list[str]:
    focus = []

    top_modules = architecture_map.get("top_modules", [])[:5]
    if top_modules:
        focus.append(
            "Top modules by file count: "
            + ", ".join(f"{item['module']} ({item['files']})" for item in top_modules)
        )

    frameworks = scan_result.get("frameworks", [])
    if frameworks:
        focus.append("Detected frameworks/runtime signals: " + ", ".join(frameworks))

    languages = scan_result.get("languages", {})
    if languages:
        focus.append(
            "Primary languages: "
            + ", ".join(f"{lang} ({count})" for lang, count in list(languages.items())[:5])
        )

    if architecture_map.get("api_routes"):
        focus.append("This repo likely has an API-oriented flow, so focus on request entry points and service orchestration.")

    if architecture_map.get("frontend"):
        focus.append("This repo includes frontend code, so you may need to understand both UI flow and backend integration.")

    if architecture_map.get("config_infra"):
        focus.append("Config/infrastructure files are present, so runtime behavior may depend on environment or deployment setup.")

    return focus[:8]


def _build_workflows(architecture_map: dict[str, Any]) -> list[str]:
    workflows = []

    if architecture_map.get("entry_points") and architecture_map.get("api_routes") and architecture_map.get("services"):
        workflows.append("Request handling flow: entry point -> API/controller -> service layer.")

    if architecture_map.get("services") and (architecture_map.get("data_access") or architecture_map.get("data_models")):
        workflows.append("Business flow: service layer -> repository/data access -> models/schemas.")

    if architecture_map.get("frontend") and architecture_map.get("api_routes"):
        workflows.append("UI flow: frontend/pages/components -> API routes -> backend services.")

    if architecture_map.get("tests"):
        workflows.append("Validation flow: implementation modules -> nearby tests/specs.")

    if architecture_map.get("config_infra"):
        workflows.append("Environment/deployment flow: config/infrastructure files influence runtime behavior.")

    if not workflows:
        workflows.append("No strong workflow was inferred from file organization alone.")

    return workflows


def build_onboarding_guide(repo_path: str) -> dict[str, Any]:
    architecture_map = build_architecture_map(repo_path)
    scan_result = scan_repository(repo_path)

    first_files = _pick_first_files(architecture_map)
    learning_path = _build_learning_path(architecture_map)
    focus_areas = _build_focus_areas(architecture_map, scan_result)
    workflows = _build_workflows(architecture_map)

    return {
        "repo_name": architecture_map["repo_name"],
        "repo_path": architecture_map["repo_path"],
        "first_files_to_read": first_files,
        "learning_path": learning_path,
        "focus_areas": focus_areas,
        "likely_workflows": workflows,
        "metadata": {
            "total_scanned_files": architecture_map["total_scanned_files"],
            "frameworks": scan_result.get("frameworks", []),
            "languages": scan_result.get("languages", {}),
            "top_modules": architecture_map.get("top_modules", []),
        },
    }
