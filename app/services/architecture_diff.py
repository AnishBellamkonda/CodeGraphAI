from __future__ import annotations

from typing import Any

from app.services.architecture_map import build_architecture_map


def _as_set(items: list[str]) -> set[str]:
    return set(items or [])


def _module_map(modules: list[dict[str, Any]]) -> dict[str, int]:
    return {item["module"]: item["files"] for item in (modules or []) if "module" in item}


def _sorted_list(values: set[str]) -> list[str]:
    return sorted(list(values))[:50]


def _diff_section(map_a: dict[str, Any], map_b: dict[str, Any], key: str) -> dict[str, Any]:
    a = _as_set(map_a.get(key, []))
    b = _as_set(map_b.get(key, []))
    return {
        "only_in_a": _sorted_list(a - b),
        "only_in_b": _sorted_list(b - a),
        "shared_count": len(a & b),
    }


def build_architecture_diff(
    repo_path_a: str,
    repo_path_b: str,
    label_a: str | None = None,
    label_b: str | None = None,
) -> dict[str, Any]:
    map_a = build_architecture_map(repo_path_a)
    map_b = build_architecture_map(repo_path_b)

    modules_a = _module_map(map_a.get("top_modules", []))
    modules_b = _module_map(map_b.get("top_modules", []))

    module_names_a = set(modules_a.keys())
    module_names_b = set(modules_b.keys())

    shared_modules = []
    for name in sorted(module_names_a & module_names_b):
        shared_modules.append(
            {
                "module": name,
                "files_in_a": modules_a.get(name, 0),
                "files_in_b": modules_b.get(name, 0),
                "delta": modules_b.get(name, 0) - modules_a.get(name, 0),
            }
        )

    shared_modules = sorted(shared_modules, key=lambda x: abs(x["delta"]), reverse=True)[:20]

    sections = [
        "entry_points",
        "api_routes",
        "services",
        "data_models",
        "data_access",
        "frontend",
        "config_infra",
        "tests",
        "docs",
    ]

    section_diffs = {section: _diff_section(map_a, map_b, section) for section in sections}

    summary_notes = []

    if map_a.get("total_scanned_files") != map_b.get("total_scanned_files"):
        summary_notes.append(
            f"Repo B total scanned files: {map_b.get('total_scanned_files')} vs Repo A: {map_a.get('total_scanned_files')}."
        )

    only_modules_a = sorted(list(module_names_a - module_names_b))[:15]
    only_modules_b = sorted(list(module_names_b - module_names_a))[:15]

    if only_modules_a:
        summary_notes.append("Repo A unique top modules: " + ", ".join(only_modules_a))
    if only_modules_b:
        summary_notes.append("Repo B unique top modules: " + ", ".join(only_modules_b))

    if section_diffs["entry_points"]["only_in_a"] or section_diffs["entry_points"]["only_in_b"]:
        summary_notes.append("Entry-point structure differs between the two repos.")

    if section_diffs["api_routes"]["only_in_a"] or section_diffs["api_routes"]["only_in_b"]:
        summary_notes.append("API route/controller structure differs between the two repos.")

    if section_diffs["services"]["only_in_a"] or section_diffs["services"]["only_in_b"]:
        summary_notes.append("Service-layer structure differs between the two repos.")

    if section_diffs["frontend"]["only_in_a"] or section_diffs["frontend"]["only_in_b"]:
        summary_notes.append("Frontend/UI structure differs between the two repos.")

    if section_diffs["tests"]["only_in_a"] or section_diffs["tests"]["only_in_b"]:
        summary_notes.append("Test-layer structure differs between the two repos.")

    if not summary_notes:
        summary_notes.append("The two repositories have very similar high-level architecture structure.")

    return {
        "repo_a": {
            "label": label_a or map_a["repo_name"],
            "repo_path": map_a["repo_path"],
            "total_scanned_files": map_a["total_scanned_files"],
            "top_modules": map_a.get("top_modules", []),
        },
        "repo_b": {
            "label": label_b or map_b["repo_name"],
            "repo_path": map_b["repo_path"],
            "total_scanned_files": map_b["total_scanned_files"],
            "top_modules": map_b.get("top_modules", []),
        },
        "module_diff": {
            "only_in_a": only_modules_a,
            "only_in_b": only_modules_b,
            "shared_modules_with_size_delta": shared_modules,
        },
        "section_diffs": section_diffs,
        "summary_notes": summary_notes[:12],
    }
