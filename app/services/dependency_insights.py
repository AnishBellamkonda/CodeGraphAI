from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.repo_scanner import IGNORE_DIRS, IGNORE_FILES


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts.intersection(IGNORE_DIRS):
        return True
    if path.name in IGNORE_FILES:
        return True
    return False


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _extract_requirements(lines: list[str]) -> list[str]:
    deps = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-r "):
            continue
        dep = (
            line.split("==")[0]
            .split(">=")[0]
            .split("<=")[0]
            .split("~=")[0]
            .split("[")[0]
            .strip()
        )
        if dep:
            deps.append(dep)
    return deps[:50]


def _extract_package_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(_safe_read_text(path))
    except Exception:
        return {"dependencies": [], "devDependencies": []}

    return {
        "dependencies": sorted(list((data.get("dependencies") or {}).keys()))[:50],
        "devDependencies": sorted(list((data.get("devDependencies") or {}).keys()))[:50],
    }


def _extract_pyproject(path: Path) -> list[str]:
    text = _safe_read_text(path)
    deps = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("dependencies = ["):
            continue
        if stripped.startswith('"') or stripped.startswith("'"):
            dep = stripped.strip(",").strip('"').strip("'")
            dep = dep.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
            if dep:
                deps.append(dep)

    return deps[:50]


def _extract_pom_xml(path: Path) -> list[str]:
    text = _safe_read_text(path)
    deps = []
    for line in text.splitlines():
        if "<artifactId>" in line:
            dep = line.replace("<artifactId>", "").replace("</artifactId>", "").strip()
            if dep and dep not in {"project", "parent"}:
                deps.append(dep)
    return deps[:50]


def _extract_go_mod(path: Path) -> list[str]:
    deps = []
    for line in _safe_read_text(path).splitlines():
        line = line.strip()
        if not line or line.startswith("module ") or line.startswith("go ") or line.startswith("require (") or line == ")":
            continue
        parts = line.split()
        if parts:
            deps.append(parts[0])
    return deps[:50]


def _extract_gradle(path: Path) -> list[str]:
    deps = []
    for line in _safe_read_text(path).splitlines():
        line = line.strip()
        if any(token in line for token in ["implementation", "api", "testImplementation", "compileOnly", "runtimeOnly"]):
            deps.append(line)
    return deps[:50]


def build_dependency_insights(repo_path_str: str) -> dict[str, Any]:
    repo_path = Path(repo_path_str).expanduser().resolve()

    if not repo_path.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")

    if not repo_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {repo_path}")

    files_found: dict[str, str] = {}
    package_managers: list[str] = []
    dependency_summary: dict[str, Any] = {}
    infra_files: list[str] = []

    interesting_files = {
        "requirements.txt",
        "pyproject.toml",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "go.mod",
        "go.sum",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "terraform.tf",
    }

    for path in repo_path.rglob("*"):
        if should_skip(path):
            continue
        if not path.is_file():
            continue

        rel = str(path.relative_to(repo_path))
        name = path.name

        if name in interesting_files or name.startswith(".env") or ".github/workflows" in rel:
            files_found[name] = rel

        lowered = rel.lower()
        if (
            name == "Dockerfile"
            or lowered.endswith(".tf")
            or "docker-compose" in lowered
            or ".github/workflows" in lowered
            or "k8s" in lowered
            or "kubernetes" in lowered
            or "helm" in lowered
        ):
            infra_files.append(rel)

    if "requirements.txt" in files_found:
        package_managers.append("pip")
        req_path = repo_path / files_found["requirements.txt"]
        dependency_summary["python_requirements"] = _extract_requirements(_safe_read_text(req_path).splitlines())

    if "pyproject.toml" in files_found:
        package_managers.append("pyproject")
        dependency_summary["pyproject_dependencies"] = _extract_pyproject(repo_path / files_found["pyproject.toml"])

    if "package.json" in files_found:
        package_managers.append("npm/yarn/pnpm")
        dependency_summary["node_package_json"] = _extract_package_json(repo_path / files_found["package.json"])

    if "pom.xml" in files_found:
        package_managers.append("maven")
        dependency_summary["maven_dependencies"] = _extract_pom_xml(repo_path / files_found["pom.xml"])

    if "build.gradle" in files_found or "build.gradle.kts" in files_found:
        package_managers.append("gradle")
        gradle_file = files_found.get("build.gradle") or files_found.get("build.gradle.kts")
        dependency_summary["gradle_dependencies"] = _extract_gradle(repo_path / gradle_file)

    if "go.mod" in files_found:
        package_managers.append("go modules")
        dependency_summary["go_modules"] = _extract_go_mod(repo_path / files_found["go.mod"])

    package_managers = sorted(list(dict.fromkeys(package_managers)))
    infra_files = sorted(list(dict.fromkeys(infra_files)))[:30]

    return {
        "repo_name": repo_path.name,
        "repo_path": str(repo_path),
        "package_managers": package_managers,
        "dependency_files": files_found,
        "dependency_summary": dependency_summary,
        "infra_files": infra_files,
    }
