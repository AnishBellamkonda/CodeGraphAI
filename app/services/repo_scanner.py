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
    ".vscode",
    ".mypy_cache",
    ".pytest_cache",
    "coverage",
}

IGNORE_FILES = {
    ".DS_Store",
}

SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript React",
    ".jsx": "JavaScript React",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sh": "Shell",
}


def detect_frameworks(file_paths: list[str], file_names: set[str]) -> list[str]:
    frameworks = set()

    normalized_paths = [p.lower() for p in file_paths]
    normalized_names = {name.lower() for name in file_names}

    if "package.json" in normalized_names:
        frameworks.add("Node.js")

    if "requirements.txt" in normalized_names or "pyproject.toml" in normalized_names:
        frameworks.add("Python Project")

    if "pom.xml" in normalized_names or "build.gradle" in normalized_names:
        frameworks.add("Java Project")

    if "go.mod" in normalized_names:
        frameworks.add("Go Project")

    if "dockerfile" in normalized_names:
        frameworks.add("Docker")

    if any("fastapi" in p for p in normalized_paths):
        frameworks.add("FastAPI")

    if any("spring" in p for p in normalized_paths):
        frameworks.add("Spring")

    if any("react" in p for p in normalized_paths) or any(
        name in normalized_names for name in {"vite.config.ts", "vite.config.js"}
    ):
        frameworks.add("React")

    if any("next" in p for p in normalized_paths):
        frameworks.add("Next.js")

    if any("angular" in p for p in normalized_paths):
        frameworks.add("Angular")

    return sorted(frameworks)


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts.intersection(IGNORE_DIRS):
        return True
    if path.name in IGNORE_FILES:
        return True
    return False


def read_text_file(path: Path, max_chars: int = 2500) -> str:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        return content[:max_chars]
    except Exception:
        return ""


def get_top_level_structure(repo_path: Path) -> list[str]:
    items = []
    try:
        for child in sorted(repo_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            if should_skip(child):
                continue
            prefix = "[DIR]" if child.is_dir() else "[FILE]"
            items.append(f"{prefix} {child.name}")
    except Exception:
        return []
    return items[:50]


def scan_repository(repo_path_str: str) -> dict[str, Any]:
    repo_path = Path(repo_path_str).expanduser().resolve()

    if not repo_path.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")

    if not repo_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {repo_path}")

    all_files: list[Path] = []
    language_counter: Counter[str] = Counter()
    important_files: list[dict[str, str]] = []
    file_names: set[str] = set()

    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue

        relative_path = str(path.relative_to(repo_path))
        all_files.append(path)
        file_names.add(path.name)

        language = SUPPORTED_EXTENSIONS.get(path.suffix.lower())
        if language:
            language_counter[language] += 1

        important_name_set = {
            "README.md",
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "pom.xml",
            "build.gradle",
            "go.mod",
            "Dockerfile",
            ".env.example",
        }

        if path.name in important_name_set or path.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".java", ".go"}:
            preview = read_text_file(path, max_chars=1200)
            if preview.strip():
                important_files.append(
                    {
                        "path": relative_path,
                        "preview": preview,
                    }
                )

    relative_file_paths = [str(p.relative_to(repo_path)) for p in all_files]
    frameworks = detect_frameworks(relative_file_paths, file_names)

    result = {
        "repo_name": repo_path.name,
        "repo_path": str(repo_path),
        "total_files": len(all_files),
        "languages": dict(language_counter.most_common()),
        "frameworks": frameworks,
        "top_level_structure": get_top_level_structure(repo_path),
        "important_files": important_files[:20],
    }

    return result
