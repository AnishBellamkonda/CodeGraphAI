from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.repo_scanner import IGNORE_DIRS, IGNORE_FILES


def _should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts.intersection(IGNORE_DIRS):
        return True
    if path.name in IGNORE_FILES:
        return True
    return False


def build_deployment_readiness(repo_path_str: str) -> dict[str, Any]:
    repo_path = Path(repo_path_str).expanduser().resolve()

    if not repo_path.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")

    if not repo_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {repo_path}")

    detected = {
        "docker_files": [],
        "ci_cd_files": [],
        "infra_files": [],
        "env_files": [],
        "runtime_config_files": [],
        "deployment_docs": [],
    }

    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue
        if _should_skip(path):
            continue

        rel = str(path.relative_to(repo_path))
        name = path.name
        lowered = rel.lower()

        if name == "Dockerfile" or "docker-compose" in lowered:
            detected["docker_files"].append(rel)

        if ".github/workflows/" in lowered or "jenkinsfile" == name.lower() or "azure-pipelines" in lowered or ".gitlab-ci" in lowered:
            detected["ci_cd_files"].append(rel)

        if lowered.endswith(".tf") or "k8s" in lowered or "kubernetes" in lowered or "helm" in lowered or "charts/" in lowered:
            detected["infra_files"].append(rel)

        if name.startswith(".env") or "/env/" in lowered or "/config/" in lowered:
            detected["env_files"].append(rel)

        if any(token in lowered for token in ["application.yml", "application.yaml", "application.properties", "settings.py", "config.py"]):
            detected["runtime_config_files"].append(rel)

        if "deploy" in lowered or "deployment" in lowered or "ops" in lowered or "runbook" in lowered:
            detected["deployment_docs"].append(rel)

    for key in detected:
        detected[key] = sorted(list(dict.fromkeys(detected[key])))[:30]

    score = 0
    reasons = []
    actions = []

    if detected["docker_files"]:
        score += 20
        reasons.append("Containerization files detected")
    else:
        actions.append("Add Dockerfile or compose setup for consistent packaging")

    if detected["ci_cd_files"]:
        score += 20
        reasons.append("CI/CD workflow files detected")
    else:
        actions.append("Add CI/CD workflow definitions for build/test/deploy automation")

    if detected["infra_files"]:
        score += 20
        reasons.append("Infrastructure/deployment files detected")
    else:
        actions.append("Add infra-as-code or deployment manifests if deployment is required")

    if detected["env_files"] or detected["runtime_config_files"]:
        score += 20
        reasons.append("Runtime configuration/environment files detected")
    else:
        actions.append("Add clear environment/configuration setup")

    if detected["deployment_docs"]:
        score += 10
        reasons.append("Deployment-related docs or ops files detected")
    else:
        actions.append("Add deployment docs or runbook for smoother handoff")

    if detected["ci_cd_files"] and detected["docker_files"] and detected["runtime_config_files"]:
        score += 10
        reasons.append("Core deployment building blocks appear present")

    score = min(score, 100)

    if score >= 85:
        level = "Strong"
    elif score >= 65:
        level = "Moderate"
    elif score >= 40:
        level = "Weak"
    else:
        level = "Very Weak"

    if not reasons:
        reasons.append("Very few deployment-readiness signals were detected.")

    if not actions:
        actions.append("Current repository shows solid deployment-readiness signals.")

    return {
        "repo_name": repo_path.name,
        "repo_path": str(repo_path),
        "score": score,
        "level": level,
        "detected": detected,
        "reasons": reasons,
        "recommended_actions": actions,
        "notes": [
            "This is a structural readiness heuristic, not a real deployment validation.",
            "Presence of files does not guarantee correctness of deployment pipelines or manifests.",
        ],
    }
