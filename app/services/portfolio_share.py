from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from app.services.architecture_map import build_architecture_map
from app.services.dependency_insights import build_dependency_insights
from app.services.deployment_readiness import build_deployment_readiness
from app.services.onboarding_assistant import build_onboarding_guide
from app.services.repo_scanner import scan_repository
from app.services.system_design_explainer import build_system_design_explanation
from app.services.test_coverage_heuristics import build_test_coverage_heuristics

SHARES_DIR = Path("./shares")


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")


def _json_like(value: Any) -> str:
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            parts.append(f"{escape(str(k))}: {escape(str(v))}")
        return "<br>".join(parts)
    if isinstance(value, list):
        return "<br>".join(f"• {escape(str(item))}" for item in value) if value else "None"
    return escape(str(value))


def _kv_cards(mapping: dict[str, Any]) -> str:
    cards = []
    for key, value in mapping.items():
        cards.append(
            f"""
            <div class="kv-card">
              <div class="kv-title">{escape(str(key))}</div>
              <div class="kv-value">{_json_like(value)}</div>
            </div>
            """
        )
    return "\n".join(cards)


def _list_section(title: str, items: list[str]) -> str:
    if not items:
        items_html = "<li>None</li>"
    else:
        items_html = "\n".join(f"<li>{escape(str(item))}</li>" for item in items[:30])

    return f"""
    <section class="panel">
      <h3>{escape(title)}</h3>
      <ul>{items_html}</ul>
    </section>
    """


def _module_section(modules: list[dict[str, Any]]) -> str:
    rows = []
    for item in modules[:20]:
        rows.append(
            f"<li><strong>{escape(item['module'])}</strong> — {escape(str(item['files']))} files</li>"
        )
    if not rows:
        rows = ["<li>None</li>"]

    return f"""
    <section class="panel">
      <h3>Top Modules</h3>
      <ul>
        {''.join(rows)}
      </ul>
    </section>
    """


def _tested_examples_section(examples: list[dict[str, Any]]) -> str:
    blocks = []
    for item in examples[:8]:
        tests = "".join(f"<li>{escape(test)}</li>" for test in item.get("matched_tests", []))
        blocks.append(
            f"""
            <div class="mini-card">
              <div class="mini-title">{escape(item.get("source_file", "source"))}</div>
              <ul>{tests or "<li>No matched tests</li>"}</ul>
            </div>
            """
        )

    if not blocks:
        blocks.append('<div class="mini-card"><div class="mini-title">No tested examples detected</div></div>')

    return f"""
    <section class="panel">
      <h3>Likely Tested Examples</h3>
      <div class="mini-grid">
        {''.join(blocks)}
      </div>
    </section>
    """


def build_portfolio_share(repo_path: str, repo_label: str | None = None) -> dict[str, Any]:
    scan_result = scan_repository(repo_path)
    architecture = build_architecture_map(repo_path)
    onboarding = build_onboarding_guide(repo_path)
    dependencies = build_dependency_insights(repo_path)
    system_design = build_system_design_explanation(repo_path)
    tests = build_test_coverage_heuristics(repo_path)
    deployment = build_deployment_readiness(repo_path)

    repo_name = repo_label or scan_result["repo_name"]
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    top_metadata = {
        "Repo Name": repo_name,
        "Repo Path": scan_result["repo_path"],
        "Generated At": generated_at,
        "Total Files": scan_result["total_files"],
        "Languages": ", ".join(f"{k} ({v})" for k, v in scan_result.get("languages", {}).items()) or "None",
        "Frameworks": ", ".join(scan_result.get("frameworks", [])) or "None",
        "Package Managers": ", ".join(dependencies.get("package_managers", [])) or "None",
        "Deployment Readiness": f"{deployment['score']} / 100 ({deployment['level']})",
        "Test Heuristic Coverage": f"{tests['counts']['coverage_heuristic_percent']}%",
    }

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(repo_name)} — Portfolio Share</title>
  <style>
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0b1020;
      color: #e8ecf4;
      line-height: 1.5;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 20px 60px;
    }}
    .hero {{
      padding: 24px;
      border-radius: 18px;
      background: linear-gradient(135deg, #17203b, #0f172a);
      border: 1px solid rgba(255,255,255,0.08);
      margin-bottom: 24px;
    }}
    h1, h2, h3 {{
      margin: 0 0 12px 0;
    }}
    .sub {{
      color: #a9b5d1;
      margin-top: 8px;
    }}
    .grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      margin: 20px 0 28px;
    }}
    .kv-card, .panel, .mini-card {{
      background: #12192e;
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 16px;
      padding: 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    }}
    .kv-title {{
      font-size: 12px;
      color: #95a3c3;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}
    .kv-value {{
      font-size: 14px;
      color: #eef3ff;
      word-break: break-word;
    }}
    .section-grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      margin-bottom: 24px;
    }}
    .mini-grid {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }}
    .mini-title {{
      font-weight: 600;
      margin-bottom: 10px;
      color: #dbe7ff;
    }}
    ul {{
      margin: 0;
      padding-left: 18px;
    }}
    li {{
      margin: 6px 0;
    }}
    .narrative {{
      white-space: pre-wrap;
      color: #eaf1ff;
    }}
    .footer {{
      margin-top: 36px;
      color: #95a3c3;
      font-size: 13px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="hero">
      <h1>{escape(repo_name)} — Portfolio Share</h1>
      <div class="sub">Generated by CodeGraph AI • {escape(generated_at)}</div>
    </div>

    <div class="grid">
      {_kv_cards(top_metadata)}
    </div>

    <div class="section-grid">
      <section class="panel">
        <h3>System Design Narrative</h3>
        <div class="narrative">{escape(system_design['narrative'])}</div>
      </section>

      <section class="panel">
        <h3>Design Risks / Gaps</h3>
        <ul>
          {''.join(f"<li>{escape(item)}</li>" for item in system_design.get('design_risks', []))}
        </ul>
      </section>
    </div>

    <div class="section-grid">
      {_module_section(architecture.get("top_modules", []))}
      {_list_section("Entry Points", architecture.get("entry_points", []))}
      {_list_section("API Routes", architecture.get("api_routes", []))}
      {_list_section("Services", architecture.get("services", []))}
      {_list_section("Data Access", architecture.get("data_access", []))}
      {_list_section("Frontend", architecture.get("frontend", []))}
      {_list_section("Config / Infra", architecture.get("config_infra", []))}
      {_list_section("Tests", architecture.get("tests", []))}
    </div>

    <div class="section-grid">
      {_list_section("Onboarding — First Files To Read", onboarding.get("first_files_to_read", []))}
      {_list_section("Onboarding — Learning Path", onboarding.get("learning_path", []))}
      {_list_section("Dependency Package Managers", dependencies.get("package_managers", []))}
      {_list_section("Deployment Readiness Actions", deployment.get("recommended_actions", []))}
      {_list_section("Risky Untested Files", tests.get("risky_untested_files", []))}
      {_list_section("Detected Test Frameworks", tests.get("detected_test_frameworks", []))}
    </div>

    {_tested_examples_section(tests.get("likely_tested_examples", []))}

    <div class="footer">
      This share page is a static artifact generated from repository structure and local analysis heuristics.
    </div>
  </div>
</body>
</html>
""".strip()

    SHARES_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{_safe_name(repo_name)}_portfolio_share_{stamp}.html"
    output_path = SHARES_DIR / filename
    output_path.write_text(html, encoding="utf-8")

    return {
        "repo_name": repo_name,
        "repo_path": scan_result["repo_path"],
        "share_path": str(output_path.resolve()),
        "preview_title": f"{repo_name} — Portfolio Share",
        "deployment_score": deployment["score"],
        "test_coverage_percent": tests["counts"]["coverage_heuristic_percent"],
    }
