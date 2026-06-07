from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.services.architecture_map import build_architecture_map
from app.services.repo_scanner import IGNORE_DIRS, IGNORE_FILES

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
    ".rb", ".php", ".c", ".cpp", ".cs", ".kt", ".swift"
}


def _should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts.intersection(IGNORE_DIRS):
        return True
    if path.name in IGNORE_FILES:
        return True
    return False


def _is_test_file(rel_path: str) -> bool:
    path = Path(rel_path)
    name = path.name.lower()
    parts = [p.lower() for p in path.parts]

    return (
        "tests" in parts
        or "test" in parts
        or "__tests__" in parts
        or "spec" in parts
        or name.startswith("test_")
        or "_test." in name
        or ".test." in name
        or ".spec." in name
    )


def _is_source_code_file(rel_path: str) -> bool:
    path = Path(rel_path)
    if _is_test_file(rel_path):
        return False
    if path.suffix.lower() not in CODE_EXTENSIONS:
        return False

    lowered = rel_path.lower()
    if any(token in lowered for token in ["/docs/", "readme", "/migrations/", "/dist/", "/build/"]):
        return False

    return True


def _normalize_name(value: str) -> str:
    value = value.lower()
    value = re.sub(r"(^test_|_test$|^spec_|_spec$)", "", value)
    value = value.replace(".test", "").replace(".spec", "")
    value = re.sub(r"[^a-z0-9]", "", value)
    return value


def _detect_test_frameworks(repo_path: Path, rel_paths: list[str]) -> list[str]:
    frameworks = set()
    lowered = [p.lower() for p in rel_paths]

    if any("pytest.ini" in p or "conftest.py" in p for p in lowered):
        frameworks.add("pytest")
    if any("jest.config" in p or "__tests__" in p for p in lowered):
        frameworks.add("jest")
    if any("vitest.config" in p for p in lowered):
        frameworks.add("vitest")
    if any("cypress.config" in p or "/cypress/" in p for p in lowered):
        frameworks.add("cypress")
    if any("playwright.config" in p for p in lowered):
        frameworks.add("playwright")
    if any(p.endswith("_test.go") for p in lowered):
        frameworks.add("go test")
    if any("/src/test/" in p.lower() or p.endswith("pom.xml") for p in lowered):
        frameworks.add("junit")
    if any(".spec.ts" in p or ".spec.js" in p for p in lowered):
        frameworks.add("spec-style tests")

    return sorted(frameworks)


def _match_tests_for_source(source_file: str, test_files: list[str]) -> list[str]:
    source_path = Path(source_file)
    source_parent = source_path.parent
    source_top = source_path.parts[0] if source_path.parts else ""
    source_stem = _normalize_name(source_path.stem)

    matches: list[tuple[int, str]] = []

    for test_file in test_files:
        test_path = Path(test_file)
        test_name = test_path.name.lower()
        test_stem = _normalize_name(test_path.stem)

        score = 0

        if source_stem and test_stem:
            if source_stem == test_stem:
                score += 4
            elif source_stem in test_name or test_stem in source_path.name.lower():
                score += 3

        if source_parent == test_path.parent:
            score += 2

        if source_parent.name and source_parent.name.lower() in [p.lower() for p in test_path.parts]:
            score += 1

        if source_top and test_path.parts and test_path.parts[0] == source_top:
            score += 1

        if score >= 3:
            matches.append((score, test_file))

    matches.sort(key=lambda x: (-x[0], x[1]))
    return [item[1] for item in matches[:5]]


def build_test_coverage_heuristics(repo_path_str: str) -> dict[str, Any]:
    repo_path = Path(repo_path_str).expanduser().resolve()

    if not repo_path.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")

    if not repo_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {repo_path}")

    rel_paths: list[str] = []

    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue
        if _should_skip(path):
            continue
        rel_paths.append(str(path.relative_to(repo_path)))

    source_files = sorted([p for p in rel_paths if _is_source_code_file(p)])
    test_files = sorted([p for p in rel_paths if _is_test_file(p)])

    tested_examples = []
    tested_source_files = []
    untested_source_files = []

    for source_file in source_files:
        matched_tests = _match_tests_for_source(source_file, test_files)
        if matched_tests:
            tested_source_files.append(source_file)
            if len(tested_examples) < 20:
                tested_examples.append({
                    "source_file": source_file,
                    "matched_tests": matched_tests,
                })
        else:
            untested_source_files.append(source_file)

    architecture_map = build_architecture_map(str(repo_path))

    priority_candidates = []
    priority_candidates.extend(architecture_map.get("entry_points", []))
    priority_candidates.extend(architecture_map.get("api_routes", []))
    priority_candidates.extend(architecture_map.get("services", []))
    priority_candidates.extend(architecture_map.get("data_access", []))
    priority_candidates.extend(architecture_map.get("data_models", []))

    risky_untested = []
    seen = set()

    for item in priority_candidates:
        if item in untested_source_files and item not in seen:
            seen.add(item)
            risky_untested.append(item)

    for item in untested_source_files:
        if item not in seen:
            seen.add(item)
            risky_untested.append(item)
        if len(risky_untested) >= 20:
            break

    total_sources = len(source_files)
    total_tests = len(test_files)
    tested_count = len(tested_source_files)
    untested_count = len(untested_source_files)
    coverage_pct = round((tested_count / total_sources) * 100, 2) if total_sources else 0.0

    return {
        "repo_name": repo_path.name,
        "repo_path": str(repo_path),
        "counts": {
            "total_source_files": total_sources,
            "total_test_files": total_tests,
            "likely_tested_source_files": tested_count,
            "likely_untested_source_files": untested_count,
            "coverage_heuristic_percent": coverage_pct,
        },
        "detected_test_frameworks": _detect_test_frameworks(repo_path, rel_paths),
        "test_files_sample": test_files[:30],
        "likely_tested_examples": tested_examples[:12],
        "risky_untested_files": risky_untested[:20],
        "notes": [
            "This is a heuristic estimate based on repo structure and file naming, not real coverage instrumentation.",
            "A source file is marked as likely tested when a nearby test file with a strong name/path match is found.",
        ],
    }
