from __future__ import annotations

from typing import Any

from app.services.architecture_map import build_architecture_map
from app.services.dependency_insights import build_dependency_insights
from app.services.onboarding_assistant import build_onboarding_guide
from app.services.repo_scanner import scan_repository


def _component_list(architecture_map: dict[str, Any], dependency_insights: dict[str, Any]) -> list[str]:
    components: list[str] = []

    if architecture_map.get("entry_points"):
        components.append("Application entry points initialize the system and wire core modules.")
    if architecture_map.get("api_routes"):
        components.append("API/controller layer receives requests and maps them to handlers.")
    if architecture_map.get("services"):
        components.append("Service layer likely contains business logic and workflow orchestration.")
    if architecture_map.get("data_access"):
        components.append("Data access layer likely handles repositories, persistence, or database interactions.")
    if architecture_map.get("data_models"):
        components.append("Data models/schemas define domain entities or API contracts.")
    if architecture_map.get("frontend"):
        components.append("Frontend/UI layer likely renders views and interacts with backend APIs.")
    if architecture_map.get("config_infra"):
        components.append("Config/infrastructure layer controls runtime behavior, environments, and deployment.")
    if architecture_map.get("tests"):
        components.append("Test layer validates workflows and expected system behavior.")

    package_managers = dependency_insights.get("package_managers", [])
    if package_managers:
        components.append(f"Dependency management appears to use: {', '.join(package_managers)}.")

    return components[:10]


def _request_flow(architecture_map: dict[str, Any]) -> list[str]:
    flow: list[str] = []

    if architecture_map.get("entry_points"):
        flow.append("System starts from detected entry points.")
    if architecture_map.get("api_routes"):
        flow.append("Requests likely enter through API route/controller files.")
    if architecture_map.get("services"):
        flow.append("Requests are likely delegated to service-layer business logic.")
    if architecture_map.get("data_access") or architecture_map.get("data_models"):
        flow.append("Business logic likely reads/writes through repositories, database helpers, or schemas.")
    if architecture_map.get("frontend") and architecture_map.get("api_routes"):
        flow.append("Frontend likely calls backend APIs rather than embedding core business logic directly.")
    if architecture_map.get("tests"):
        flow.append("Critical flows likely have corresponding validation paths in tests.")

    if not flow:
        flow.append("No strong request flow pattern was detected from structure alone.")

    return flow


def _design_risks(
    scan_result: dict[str, Any],
    architecture_map: dict[str, Any],
    dependency_insights: dict[str, Any],
) -> list[str]:
    risks: list[str] = []

    total_files = scan_result.get("total_files", 0)
    if total_files > 250:
        risks.append("Large codebase size may increase onboarding and change complexity.")

    if architecture_map.get("services") and not architecture_map.get("tests"):
        risks.append("Service/business logic is present but no obvious test layer was detected.")

    if architecture_map.get("api_routes") and not architecture_map.get("data_access") and not architecture_map.get("services"):
        risks.append("API routes appear present without a clearly separated service/data layer, which may indicate tight coupling.")

    if architecture_map.get("config_infra") and not dependency_insights.get("infra_files"):
        risks.append("Infrastructure/config signals exist, but explicit infra/build files were not strongly detected.")

    if not architecture_map.get("docs"):
        risks.append("No strong documentation layer was detected, which may slow onboarding.")

    if architecture_map.get("frontend") and architecture_map.get("api_routes") and not architecture_map.get("tests"):
        risks.append("Full-stack structure exists, but obvious tests were not detected.")

    if not risks:
        risks.append("No major structural risks were detected from the current repository signals.")

    return risks[:8]


def _narrative(
    scan_result: dict[str, Any],
    architecture_map: dict[str, Any],
    onboarding_guide: dict[str, Any],
    dependency_insights: dict[str, Any],
) -> str:
    repo_name = scan_result.get("repo_name", "This repository")
    frameworks = ", ".join(scan_result.get("frameworks", [])) or "no strong framework signals"
    top_modules = ", ".join(
        f"{item['module']} ({item['files']})"
        for item in architecture_map.get("top_modules", [])[:5]
    ) or "no dominant modules detected"

    flow = onboarding_guide.get("likely_workflows", [])
    flow_text = " ".join(flow[:3]) if flow else "No strong workflow inference was detected."

    deps = dependency_insights.get("package_managers", [])
    dep_text = ", ".join(deps) if deps else "no obvious package manager signal"

    return (
        f"{repo_name} appears to be organized as a modular application with {frameworks}. "
        f"The most visible top-level areas are {top_modules}. "
        f"From the current structure, the likely design is that application entry points or routes hand work to service-layer logic, "
        f"which then interacts with persistence or supporting infrastructure where present. "
        f"Dependency/build tooling suggests {dep_text}. "
        f"The most likely runtime behavior inferred from structure is: {flow_text}"
    )


def build_system_design_explanation(repo_path: str) -> dict[str, Any]:
    scan_result = scan_repository(repo_path)
    architecture_map = build_architecture_map(repo_path)
    onboarding_guide = build_onboarding_guide(repo_path)
    dependency_insights = build_dependency_insights(repo_path)

    return {
        "repo_name": scan_result["repo_name"],
        "repo_path": scan_result["repo_path"],
        "narrative": _narrative(scan_result, architecture_map, onboarding_guide, dependency_insights),
        "components": _component_list(architecture_map, dependency_insights),
        "request_flow": _request_flow(architecture_map),
        "design_risks": _design_risks(scan_result, architecture_map, dependency_insights),
        "metadata": {
            "languages": scan_result.get("languages", {}),
            "frameworks": scan_result.get("frameworks", []),
            "top_modules": architecture_map.get("top_modules", []),
            "package_managers": dependency_insights.get("package_managers", []),
        },
    }
