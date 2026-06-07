from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from app.services.repo_scanner import IGNORE_DIRS, IGNORE_FILES


TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
    ".json", ".yaml", ".yml", ".md", ".sql", ".html", ".css", ".scss",
    ".sh", ".txt", ".xml"
}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts.intersection(IGNORE_DIRS):
        return True
    if path.name in IGNORE_FILES:
        return True
    return False


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in {
        "Dockerfile",
        "README.md",
        "requirements.txt",
        "pyproject.toml",
        "package.json",
        "pom.xml",
        "build.gradle",
        "go.mod",
    }


def classify_file(relative_path: str) -> str:
    rp = relative_path.lower()
    name = Path(relative_path).name.lower()

    if name in {"main.py", "app.py", "server.py", "index.js", "index.ts", "main.ts", "main.js"}:
        return "entry_points"

    if any(token in rp for token in ["/routes/", "/route/", "/api/", "controller", "endpoint"]):
        return "api_routes"

    if any(token in rp for token in ["/service/", "/services/", "/usecase/", "/business/"]):
        return "services"

    if any(token in rp for token in ["/model/", "/models/", "/schema/", "/schemas/", "/entity/", "/entities/", "/dto/"]):
        return "data_models"

    if any(token in rp for token in ["/db/", "/database/", "/repository/", "/repositories/", "/dao/", "migration", "migrations"]):
        return "data_access"

    if any(token in rp for token in ["/config/", "/configs/", ".env", "dockerfile", "k8s", "kubernetes", "helm", ".github/workflows", "terraform"]):
        return "config_infra"

    if any(token in rp for token in ["/test/", "/tests/", "__tests__", "spec.", "test_"]):
        return "tests"

    if any(token in rp for token in ["/components/", "/pages/", "/views/", "/frontend/", "/ui/", ".tsx", ".jsx", ".css", ".scss", ".html"]):
        return "frontend"

    if name == "readme.md" or rp.startswith("docs/") or "/docs/" in rp:
        return "docs"

    return "other"


def infer_modules(relative_paths: list[str]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()

    for rp in relative_paths:
        parts = Path(rp).parts
        if not parts:
            continue

        top = parts[0]
        if top.startswith("."):
            continue

        counter[top] += 1

    modules = [
        {"module": module, "files": count}
        for module, count in counter.most_common(12)
    ]
    return modules


def infer_request_flow(buckets: dict[str, list[str]]) -> list[str]:
    flow = []

    if buckets.get("entry_points"):
        flow.append("Entry points initialize the application and route incoming requests.")

    if buckets.get("api_routes"):
        flow.append("API route/controller files likely receive requests and map them to handlers.")

    if buckets.get("services"):
        flow.append("Service layer likely contains the main business logic and orchestration.")

    if buckets.get("data_access") or buckets.get("data_models"):
        flow.append("Data layer likely interacts with databases, repositories, or persistence models.")

    if buckets.get("frontend"):
        flow.append("Frontend/UI files likely render views and call API routes or backend services.")

    if buckets.get("config_infra"):
        flow.append("Config and infrastructure files likely control environment setup, deployment, and runtime behavior.")

    if not flow:
        flow.append("No strong architecture pattern was detected from file paths alone.")

    return flow


def build_architecture_map(repo_path_str: str) -> dict[str, Any]:
    repo_path = Path(repo_path_str).expanduser().resolve()

    if not repo_path.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")

    if not repo_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {repo_path}")

    buckets: dict[str, list[str]] = defaultdict(list)
    relative_paths: list[str] = []

    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        if not is_text_file(path):
            continue

        relative_path = str(path.relative_to(repo_path))
        relative_paths.append(relative_path)

        bucket = classify_file(relative_path)
        buckets[bucket].append(relative_path)

    for key in list(buckets.keys()):
        buckets[key] = sorted(buckets[key])[:30]

    modules = infer_modules(relative_paths)
    likely_flow = infer_request_flow(buckets)

    summary = {
        "repo_name": repo_path.name,
        "repo_path": str(repo_path),
        "total_scanned_files": len(relative_paths),
        "top_modules": modules,
        "entry_points": buckets.get("entry_points", []),
        "api_routes": buckets.get("api_routes", []),
        "services": buckets.get("services", []),
        "data_models": buckets.get("data_models", []),
        "data_access": buckets.get("data_access", []),
        "frontend": buckets.get("frontend", []),
        "config_infra": buckets.get("config_infra", []),
        "tests": buckets.get("tests", []),
        "docs": buckets.get("docs", []),
        "other": buckets.get("other", [])[:20],
        "likely_request_flow": likely_flow,
    }

    return summary
