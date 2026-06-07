from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    "target",
    "venv",
    ".venv",
    "__pycache__",
    ".idea",
    ".pytest_cache",
}

TEXT_FILE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rs",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".sql",
    ".html",
    ".css",
    ".xml",
    ".sh",
    ".txt",
}

LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript React",
    ".jsx": "JavaScript React",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown",
    ".xml": "XML",
    ".sh": "Shell",
    ".txt": "Text",
}

MAX_PREVIEW_CHARS = 600
MAX_FILES_IN_RESPONSE = 50


def should_ignore(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)



def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_FILE_EXTENSIONS



def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="ignore")



def summarize_file(path: Path, repo_root: Path) -> dict[str, Any]:
    content = safe_read_text(path)
    relative_path = str(path.relative_to(repo_root))
    lines = content.splitlines()

    return {
        "path": relative_path,
        "language": LANGUAGE_MAP.get(path.suffix.lower(), "Unknown"),
        "line_count": len(lines),
        "preview": content[:MAX_PREVIEW_CHARS],
    }



def detect_frameworks(file_paths: list[str]) -> list[str]:
    detected = set()

    joined = " ".join(file_paths).lower()

    if "package.json" in joined:
        detected.add("Node.js")
    if "requirements.txt" in joined or "pyproject.toml" in joined:
        detected.add("Python")
    if "pom.xml" in joined or "build.gradle" in joined:
        detected.add("Java")
    if "go.mod" in joined:
        detected.add("Go")
    if "dockerfile" in joined:
        detected.add("Docker")
    if "kubernetes" in joined or "/k8s/" in joined or "helm" in joined:
        detected.add("Kubernetes")
    if "next.config" in joined:
        detected.add("Next.js")
    if "react" in joined or any(path.endswith((".jsx", ".tsx")) for path in file_paths):
        detected.add("React")

    return sorted(detected)



def analyze_repo(repo_path: str) -> dict[str, Any]:
    root = Path(repo_path).expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root}")

    all_files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and not should_ignore(path) and is_text_file(path):
            all_files.append(path)

    file_summaries = [summarize_file(path, root) for path in all_files[:MAX_FILES_IN_RESPONSE]]

    language_counter = Counter(
        LANGUAGE_MAP.get(path.suffix.lower(), "Unknown") for path in all_files
    )

    relative_paths = [str(path.relative_to(root)) for path in all_files]
    top_level_items = sorted(
        [p.name for p in root.iterdir() if p.name not in IGNORE_DIRS]
    )

    return {
        "project_root": str(root),
        "total_text_files_scanned": len(all_files),
        "top_level_items": top_level_items,
        "languages": dict(language_counter.most_common()),
        "detected_frameworks": detect_frameworks(relative_paths),
        "important_files_preview": file_summaries,
        "next_version": [
            "Add LLM-powered project summary",
            "Chunk files and create embeddings",
            "Store vectors in ChromaDB",
            "Add a /ask endpoint for repo Q&A",
        ],
    }
