from __future__ import annotations

from typing import Any

from app.services.architecture_map import build_architecture_map
from app.services.repo_scanner import scan_repository


def _to_set(items: list[str]) -> set[str]:
    return set(items or [])


def _module_dict(modules: list[dict[str, Any]]) -> dict[str, int]:
    return {item["module"]: item["files"] for item in (modules or []) if "module" in item}


def _presence_summary(arch: dict[str, Any]) -> dict[str, bool]:
    return {
        "entry_points": bool(arch.get("entry_points")),
        "api_routes": bool(arch.get("api_routes")),
        "services": bool(arch.get("services")),
        "data_models": bool(arch.get("data_models")),
        "data_access": bool(arch.get("data_access")),
        "frontend": bool(arch.get("frontend")),
        "config_infra": bool(arch.get("config_infra")),
        "tests": bool(arch.get("tests")),
        "docs": bool(arch.get("docs")),
    }


def _build_difference_notes(scan_a: dict[str, Any], scan_b: dict[str, Any], arch_a: dict[str, Any], arch_b: dict[str, Any]) -> list[str]:
    notes: list[str] = []

    frameworks_a = set(scan_a.get("frameworks", []))
    frameworks_b = set(scan_b.get("frameworks", []))

    if frameworks_a != frameworks_b:
        only_a = frameworks_a - frameworks_b
        only_b = frameworks_b - frameworks_a
        if only_a:
            notes.append(f"Repo A has unique framework/runtime signals: {', '.join(sorted(only_a))}")
        if only_b:
            notes.append(f"Repo B has unique framework/runtime signals: {', '.join(sorted(only_b))}")

    languages_a = set(scan_a.get("languages", {}).keys())
    languages_b = set(scan_b.get("languages", {}).keys())
    if languages_a != languages_b:
        if languages_a - languages_b:
            notes.append(f"Repo A includes additional languages: {', '.join(sorted(languages_a - languages_b))}")
        if languages_b - languages_a:
            notes.append(f"Repo B includes additional languages: {', '.join(sorted(languages_b - languages_a))}")

    presence_a = _presence_summary(arch_a)
    presence_b = _presence_summary(arch_b)
    for key in presence_a:
        if presence_a[key] != presence_b[key]:
            if presence_a[key]:
                notes.append(f"Repo A includes {key.replace('_', ' ')} while Repo B does not")
            else:
                notes.append(f"Repo B includes {key.replace('_', ' ')} while Repo A does not")

    if scan_a.get("total_files", 0) != scan_b.get("total_files", 0):
        notes.append(
            f"Repo size differs: Repo A has {scan_a.get('total_files', 0)} files vs Repo B {scan_b.get('total_files', 0)}"
        )

    top_a = _module_dict(arch_a.get("top_modules", []))
    top_b = _module_dict(arch_b.get("top_modules", []))

    only_modules_a = set(top_a) - set(top_b)
    only_modules_b = set(top_b) - set(top_a)

    if only_modules_a:
        notes.append(f"Repo A has unique top-level modules: {', '.join(sorted(list(only_modules_a))[:8])}")
    if only_modules_b:
        notes.append(f"Repo B has unique top-level modules: {', '.join(sorted(list(only_modules_b))[:8])}")

    if not notes:
        notes.append("The two repositories have very similar high-level architecture signals.")

    return notes[:12]


def compare_repositories(repo_path_a: str, repo_path_b: str, label_a: str | None = None, label_b: str | None = None) -> dict[str, Any]:
    scan_a = scan_repository(repo_path_a)
    scan_b = scan_repository(repo_path_b)

    arch_a = build_architecture_map(repo_path_a)
    arch_b = build_architecture_map(repo_path_b)

    frameworks_a = _to_set(scan_a.get("frameworks", []))
    frameworks_b = _to_set(scan_b.get("frameworks", []))

    languages_a = set(scan_a.get("languages", {}).keys())
    languages_b = set(scan_b.get("languages", {}).keys())

    top_modules_a = arch_a.get("top_modules", [])
    top_modules_b = arch_b.get("top_modules", [])

    return {
        "repo_a": {
            "label": label_a or scan_a["repo_name"],
            "repo_path": scan_a["repo_path"],
            "total_files": scan_a["total_files"],
            "languages": scan_a["languages"],
            "frameworks": scan_a["frameworks"],
            "top_modules": top_modules_a,
            "presence": _presence_summary(arch_a),
        },
        "repo_b": {
            "label": label_b or scan_b["repo_name"],
            "repo_path": scan_b["repo_path"],
            "total_files": scan_b["total_files"],
            "languages": scan_b["languages"],
            "frameworks": scan_b["frameworks"],
            "top_modules": top_modules_b,
            "presence": _presence_summary(arch_b),
        },
        "comparison": {
            "shared_frameworks": sorted(frameworks_a & frameworks_b),
            "frameworks_only_in_a": sorted(frameworks_a - frameworks_b),
            "frameworks_only_in_b": sorted(frameworks_b - frameworks_a),
            "shared_languages": sorted(languages_a & languages_b),
            "languages_only_in_a": sorted(languages_a - languages_b),
            "languages_only_in_b": sorted(languages_b - languages_a),
            "difference_notes": _build_difference_notes(scan_a, scan_b, arch_a, arch_b),
        },
    }
