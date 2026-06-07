from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.schemas import (
    AnalyzeRequest,
    ArchitectureMapRequest,
    ArchitectureDiffRequest,
    AskRequest,
    CompareReposRequest,
    CopilotRequest,
    DependencyInsightsRequest,
    DeploymentReadinessRequest,
    SystemDesignExplainRequest,
    TestCoverageHeuristicsRequest,
    ExportReportRequest,
    ShareSnapshotRequest,
    PortfolioShareRequest,
    FileContentRequest,
    FileTreeRequest,
    GithubArchitectureMapRequest,
    GithubArchitectureDiffRequest,
    GithubAskRequest,
    GithubCompareReposRequest,
    GithubContributorMapRequest,
    GithubCopilotRequest,
    GithubDependencyInsightsRequest,
    GithubDeploymentReadinessRequest,
    GithubSystemDesignExplainRequest,
    GithubTestCoverageHeuristicsRequest,
    GithubExportReportRequest,
    GithubShareSnapshotRequest,
    GithubPortfolioShareRequest,
    GithubIndexRequest,
    GithubIssueDashboardRequest,
    GithubOnboardingGuideRequest,
    GithubPRAnalysisRequest,
    GithubPRDashboardRequest,
    GithubReleaseReadinessRequest,
    GithubSummarizeRequest,
    HealthResponse,
    IndexRequest,
    OnboardingGuideRequest,
    SummarizeRequest,
    WatchCreateRequest,
    WatchDeleteRequest,
    WatchCheckRequest,
)
from app.services.ai_service import answer_repository_question, summarize_repository
from app.services.architecture_map import build_architecture_map
from app.services.architecture_diff import build_architecture_diff
from app.services.dependency_insights import build_dependency_insights
from app.services.deployment_readiness import build_deployment_readiness
from app.services.engineering_copilot import ask_engineering_copilot
from app.services.file_browser import build_file_tree, read_repo_file
from app.services.github_api import build_pull_request_dashboard
from app.services.github_contributors import build_contributor_ownership_map
from app.services.github_issues import build_issue_dashboard
from app.services.github_pr_ai import analyze_pull_request
from app.services.github_repo_health import compute_release_readiness
from app.services.history_store import append_history_event, clear_history, list_history
from app.services.onboarding_assistant import build_onboarding_guide
from app.services.rag_service import index_repository, search_repository
from app.services.repo_compare import compare_repositories
from app.services.repo_loader import clone_github_repo, normalize_github_url
from app.services.repo_registry import get_repo_entry, list_registered_repos, mark_repo_indexed
from app.services.repo_scanner import scan_repository
from app.services.report_exporter import build_markdown_report
from app.services.share_mode import build_share_snapshot
from app.services.portfolio_share import build_portfolio_share
from app.services.system_design_explainer import build_system_design_explanation
from app.services.test_coverage_heuristics import build_test_coverage_heuristics
from app.services.team_dashboard import build_team_dashboard
from app.services.watch_mode import check_all_watches, clear_watches, create_watch, delete_watch, list_watches

app = FastAPI(title="CodeGraph AI API", version="1.7.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/repos")
def repos():
    return {"success": True, "repos": list_registered_repos()}


@app.get("/history")
def history():
    return {"success": True, "history": list_history()}


@app.get("/dashboard/team")
def dashboard_team():
    try:
        result = build_team_dashboard()
        return {"success": True, "team_dashboard": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/history/clear")
def history_clear():
    clear_history()
    return {"success": True, "history_cleared": True}


@app.get("/watch/list")
def watch_list():
    return {"success": True, "watches": list_watches()}


@app.post("/watch/create")
def watch_create(payload: WatchCreateRequest):
    try:
        watch = create_watch(
            name=payload.name,
            source_type=payload.source_type,
            repo_path=payload.repo_path,
            repo_url=payload.repo_url,
            min_deployment_score=payload.min_deployment_score,
            min_test_coverage=payload.min_test_coverage,
            max_risky_untested=payload.max_risky_untested,
        )

        append_history_event(
            event_type="watch_create",
            source_type=payload.source_type,
            label=payload.name,
            repo_path=payload.repo_path,
            repo_url=payload.repo_url,
            payload_summary=watch["thresholds"],
        )

        return {"success": True, "watch_create": watch}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/watch/check")
def watch_check(payload: WatchCheckRequest):
    try:
        results = check_all_watches(force_refresh_github=payload.force_refresh_github)

        append_history_event(
            event_type="watch_check",
            source_type="workspace",
            label=f"{len(results)} watches checked",
            payload_summary={"alerts": sum(1 for item in results if item.get("status") == "alert")},
        )

        return {"success": True, "watch_check": results}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/watch/delete")
def watch_delete(payload: WatchDeleteRequest):
    try:
        deleted = delete_watch(payload.watch_id)
        return {"success": True, "watch_deleted": deleted}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/watch/clear")
def watch_clear():
    try:
        clear_watches()
        return {"success": True, "watch_cleared": True}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/analyze")
def analyze_repo(payload: AnalyzeRequest):
    try:
        result = scan_repository(payload.repo_path)
        return {"success": True, "data": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/summarize")
def summarize_repo(payload: SummarizeRequest):
    try:
        scan_result = scan_repository(payload.repo_path)
        summary = summarize_repository(scan_result)

        append_history_event(
            event_type="summary",
            source_type="local",
            label=scan_result["repo_name"],
            repo_path=scan_result["repo_path"],
            payload_summary={
                "frameworks": scan_result["frameworks"],
                "total_files": scan_result["total_files"],
            },
        )

        return {
            "success": True,
            "repo_name": scan_result["repo_name"],
            "repo_path": scan_result["repo_path"],
            "summary": summary,
            "metadata": {
                "languages": scan_result["languages"],
                "frameworks": scan_result["frameworks"],
                "total_files": scan_result["total_files"],
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/index")
def index_repo(payload: IndexRequest):
    try:
        result = index_repository(payload.repo_path)
        return {"success": True, "repo_path": payload.repo_path, "data": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/ask")
def ask_repo(payload: AskRequest):
    try:
        contexts = search_repository(payload.repo_path, payload.question, n_results=5)
        answer = answer_repository_question(payload.question, contexts)
        return {
            "success": True,
            "repo_path": payload.repo_path,
            "question": payload.question,
            "answer": answer,
            "contexts": contexts,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/copilot/ask")
def local_copilot(payload: CopilotRequest):
    try:
        result = ask_engineering_copilot(payload.repo_path, payload.question)

        append_history_event(
            event_type="copilot",
            source_type="local",
            label=result["repo_name"],
            repo_path=result["repo_path"],
            payload_summary={"question": payload.question},
        )

        return {"success": True, "copilot_answer": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/architecture/map")
def architecture_map(payload: ArchitectureMapRequest):
    try:
        result = build_architecture_map(payload.repo_path)

        append_history_event(
            event_type="architecture_map",
            source_type="local",
            label=result["repo_name"],
            repo_path=result["repo_path"],
            payload_summary={"total_scanned_files": result["total_scanned_files"]},
        )

        return {"success": True, "repo_path": payload.repo_path, "architecture_map": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/onboarding/guide")
def onboarding_guide(payload: OnboardingGuideRequest):
    try:
        result = build_onboarding_guide(payload.repo_path)

        append_history_event(
            event_type="onboarding_guide",
            source_type="local",
            label=result["repo_name"],
            repo_path=result["repo_path"],
            payload_summary={"first_files": len(result["first_files_to_read"])},
        )

        return {"success": True, "repo_path": payload.repo_path, "onboarding_guide": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/report/export")
def export_report(payload: ExportReportRequest):
    try:
        result = build_markdown_report(payload.repo_path)

        append_history_event(
            event_type="report_export",
            source_type="local",
            label=result["repo_name"],
            repo_path=result["repo_path"],
            payload_summary={"report_path": result["report_path"]},
        )

        return {"success": True, "repo_path": payload.repo_path, "report_export": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/share/snapshot")
def share_snapshot(payload: ShareSnapshotRequest):
    try:
        result = build_share_snapshot(payload.repo_path)

        append_history_event(
            event_type="share_snapshot",
            source_type="local",
            label=result["repo_name"],
            repo_path=result["repo_path"],
            payload_summary={"share_path": result["share_path"]},
        )

        return {"success": True, "repo_path": payload.repo_path, "share_snapshot": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/portfolio/share")
def portfolio_share(payload: PortfolioShareRequest):
    try:
        result = build_portfolio_share(payload.repo_path)

        append_history_event(
            event_type="portfolio_share",
            source_type="local",
            label=result["repo_name"],
            repo_path=result["repo_path"],
            payload_summary={"share_path": result["share_path"]},
        )

        return {"success": True, "repo_path": payload.repo_path, "portfolio_share": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/compare/repos")
def compare_local_repos(payload: CompareReposRequest):
    try:
        result = compare_repositories(payload.repo_path_a, payload.repo_path_b)

        append_history_event(
            event_type="repo_compare",
            source_type="local",
            label=f"{result['repo_a']['label']} vs {result['repo_b']['label']}",
            repo_path=f"{result['repo_a']['repo_path']} | {result['repo_b']['repo_path']}",
            payload_summary={
                "repo_a_files": result["repo_a"]["total_files"],
                "repo_b_files": result["repo_b"]["total_files"],
            },
        )

        return {"success": True, "repo_compare": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/architecture/diff")
def architecture_diff(payload: ArchitectureDiffRequest):
    try:
        result = build_architecture_diff(payload.repo_path_a, payload.repo_path_b)

        append_history_event(
            event_type="architecture_diff",
            source_type="local",
            label=f"{result['repo_a']['label']} vs {result['repo_b']['label']}",
            repo_path=f"{result['repo_a']['repo_path']} | {result['repo_b']['repo_path']}",
            payload_summary={
                "repo_a_files": result["repo_a"]["total_scanned_files"],
                "repo_b_files": result["repo_b"]["total_scanned_files"],
            },
        )

        return {"success": True, "architecture_diff": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/dependencies/insights")
def dependency_insights(payload: DependencyInsightsRequest):
    try:
        result = build_dependency_insights(payload.repo_path)

        append_history_event(
            event_type="dependency_insights",
            source_type="local",
            label=result["repo_name"],
            repo_path=result["repo_path"],
            payload_summary={"package_managers": result["package_managers"]},
        )

        return {"success": True, "repo_path": payload.repo_path, "dependency_insights": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/deployment/readiness")
def deployment_readiness(payload: DeploymentReadinessRequest):
    try:
        result = build_deployment_readiness(payload.repo_path)

        append_history_event(
            event_type="deployment_readiness",
            source_type="local",
            label=result["repo_name"],
            repo_path=result["repo_path"],
            payload_summary={"score": result["score"], "level": result["level"]},
        )

        return {"success": True, "repo_path": payload.repo_path, "deployment_readiness": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/system-design/explain")
def system_design_explain(payload: SystemDesignExplainRequest):
    try:
        result = build_system_design_explanation(payload.repo_path)

        append_history_event(
            event_type="system_design_explain",
            source_type="local",
            label=result["repo_name"],
            repo_path=result["repo_path"],
            payload_summary={"package_managers": result["metadata"]["package_managers"]},
        )

        return {"success": True, "repo_path": payload.repo_path, "system_design": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/tests/heuristics")
def test_coverage_heuristics(payload: TestCoverageHeuristicsRequest):
    try:
        result = build_test_coverage_heuristics(payload.repo_path)

        append_history_event(
            event_type="test_coverage_heuristics",
            source_type="local",
            label=result["repo_name"],
            repo_path=result["repo_path"],
            payload_summary={"coverage_heuristic_percent": result["counts"]["coverage_heuristic_percent"]},
        )

        return {"success": True, "repo_path": payload.repo_path, "test_coverage": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/files/tree")
def repo_file_tree(payload: FileTreeRequest):
    try:
        items = build_file_tree(payload.repo_path)
        return {"success": True, "repo_path": payload.repo_path, "items": items}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/files/content")
def repo_file_content(payload: FileContentRequest):
    try:
        result = read_repo_file(payload.repo_path, payload.file_path)
        return {"success": True, "repo_path": payload.repo_path, **result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/summarize")
def github_summarize_repo(payload: GithubSummarizeRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(payload.repo_url, force_refresh=payload.force_refresh)
        scan_result = scan_repository(local_repo_path)
        summary = summarize_repository(scan_result)

        append_history_event(
            event_type="summary",
            source_type="github",
            label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
            repo_path=local_repo_path,
            repo_url=normalized_url,
            payload_summary={
                "frameworks": scan_result["frameworks"],
                "total_files": scan_result["total_files"],
            },
        )

        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "repo_name": scan_result["repo_name"],
            "summary": summary,
            "metadata": {
                "languages": scan_result["languages"],
                "frameworks": scan_result["frameworks"],
                "total_files": scan_result["total_files"],
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/index")
def github_index_repo(payload: GithubIndexRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        entry = get_repo_entry(normalized_url)
        if entry and entry.get("indexed") and not payload.force_refresh:
            return {
                "success": True,
                "repo_url": normalized_url,
                "local_repo_path": local_repo_path,
                "data": {"status": "already_indexed"},
            }
        result = index_repository(local_repo_path)
        mark_repo_indexed(normalized_url, True)
        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "data": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/ask")
def github_ask_repo(payload: GithubAskRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        entry = get_repo_entry(normalized_url)
        if not (entry and entry.get("indexed")) or payload.force_refresh:
            index_repository(local_repo_path)
            mark_repo_indexed(normalized_url, True)
        contexts = search_repository(local_repo_path, payload.question, n_results=5)
        answer = answer_repository_question(payload.question, contexts)
        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "question": payload.question,
            "answer": answer,
            "contexts": contexts,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/copilot/ask")
def github_copilot(payload: GithubCopilotRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        result = ask_engineering_copilot(local_repo_path, payload.question)

        append_history_event(
            event_type="copilot",
            source_type="github",
            label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
            repo_path=local_repo_path,
            repo_url=normalized_url,
            payload_summary={"question": payload.question},
        )

        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "copilot_answer": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/architecture/map")
def github_architecture_map(payload: GithubArchitectureMapRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        result = build_architecture_map(local_repo_path)

        append_history_event(
            event_type="architecture_map",
            source_type="github",
            label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
            repo_path=local_repo_path,
            repo_url=normalized_url,
            payload_summary={"total_scanned_files": result["total_scanned_files"]},
        )

        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "architecture_map": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/onboarding/guide")
def github_onboarding_guide(payload: GithubOnboardingGuideRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        result = build_onboarding_guide(local_repo_path)

        append_history_event(
            event_type="onboarding_guide",
            source_type="github",
            label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
            repo_path=local_repo_path,
            repo_url=normalized_url,
            payload_summary={"first_files": len(result["first_files_to_read"])},
        )

        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "onboarding_guide": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/report/export")
def github_export_report(payload: GithubExportReportRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        result = build_markdown_report(
            local_repo_path,
            repo_label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
        )

        append_history_event(
            event_type="report_export",
            source_type="github",
            label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
            repo_path=local_repo_path,
            repo_url=normalized_url,
            payload_summary={"report_path": result["report_path"]},
        )

        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "report_export": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/share/snapshot")
def github_share_snapshot(payload: GithubShareSnapshotRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        result = build_share_snapshot(
            local_repo_path,
            repo_label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
        )

        append_history_event(
            event_type="share_snapshot",
            source_type="github",
            label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
            repo_path=local_repo_path,
            repo_url=normalized_url,
            payload_summary={"share_path": result["share_path"]},
        )

        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "share_snapshot": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/portfolio/share")
def github_portfolio_share(payload: GithubPortfolioShareRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        result = build_portfolio_share(
            local_repo_path,
            repo_label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
        )

        append_history_event(
            event_type="portfolio_share",
            source_type="github",
            label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
            repo_path=local_repo_path,
            repo_url=normalized_url,
            payload_summary={"share_path": result["share_path"]},
        )

        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "portfolio_share": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/compare/repos")
def compare_github_repos(payload: GithubCompareReposRequest):
    try:
        normalized_a = normalize_github_url(payload.repo_url_a)
        normalized_b = normalize_github_url(payload.repo_url_b)

        local_a = clone_github_repo(normalized_a, force_refresh=payload.force_refresh)
        local_b = clone_github_repo(normalized_b, force_refresh=payload.force_refresh)

        result = compare_repositories(
            local_a,
            local_b,
            label_a=normalized_a.replace("https://github.com/", "").replace(".git", ""),
            label_b=normalized_b.replace("https://github.com/", "").replace(".git", ""),
        )

        append_history_event(
            event_type="repo_compare",
            source_type="github",
            label=f"{result['repo_a']['label']} vs {result['repo_b']['label']}",
            repo_path=f"{local_a} | {local_b}",
            repo_url=f"{normalized_a} | {normalized_b}",
            payload_summary={
                "repo_a_files": result["repo_a"]["total_files"],
                "repo_b_files": result["repo_b"]["total_files"],
            },
        )

        return {
            "success": True,
            "repo_compare": result,
            "local_repo_a": local_a,
            "local_repo_b": local_b,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/architecture/diff")
def github_architecture_diff(payload: GithubArchitectureDiffRequest):
    try:
        normalized_a = normalize_github_url(payload.repo_url_a)
        normalized_b = normalize_github_url(payload.repo_url_b)

        local_a = clone_github_repo(normalized_a, force_refresh=payload.force_refresh)
        local_b = clone_github_repo(normalized_b, force_refresh=payload.force_refresh)

        result = build_architecture_diff(
            local_a,
            local_b,
            label_a=normalized_a.replace("https://github.com/", "").replace(".git", ""),
            label_b=normalized_b.replace("https://github.com/", "").replace(".git", ""),
        )

        append_history_event(
            event_type="architecture_diff",
            source_type="github",
            label=f"{result['repo_a']['label']} vs {result['repo_b']['label']}",
            repo_path=f"{local_a} | {local_b}",
            repo_url=f"{normalized_a} | {normalized_b}",
            payload_summary={
                "repo_a_files": result["repo_a"]["total_scanned_files"],
                "repo_b_files": result["repo_b"]["total_scanned_files"],
            },
        )

        return {
            "success": True,
            "architecture_diff": result,
            "local_repo_a": local_a,
            "local_repo_b": local_b,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/dependencies/insights")
def github_dependency_insights(payload: GithubDependencyInsightsRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        result = build_dependency_insights(local_repo_path)

        append_history_event(
            event_type="dependency_insights",
            source_type="github",
            label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
            repo_path=local_repo_path,
            repo_url=normalized_url,
            payload_summary={"package_managers": result["package_managers"]},
        )

        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "dependency_insights": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/deployment/readiness")
def github_deployment_readiness(payload: GithubDeploymentReadinessRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        result = build_deployment_readiness(local_repo_path)

        append_history_event(
            event_type="deployment_readiness",
            source_type="github",
            label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
            repo_path=local_repo_path,
            repo_url=normalized_url,
            payload_summary={"score": result["score"], "level": result["level"]},
        )

        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "deployment_readiness": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/system-design/explain")
def github_system_design_explain(payload: GithubSystemDesignExplainRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        result = build_system_design_explanation(local_repo_path)

        append_history_event(
            event_type="system_design_explain",
            source_type="github",
            label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
            repo_path=local_repo_path,
            repo_url=normalized_url,
            payload_summary={"package_managers": result["metadata"]["package_managers"]},
        )

        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "system_design": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/tests/heuristics")
def github_test_coverage_heuristics(payload: GithubTestCoverageHeuristicsRequest):
    try:
        normalized_url = normalize_github_url(payload.repo_url)
        local_repo_path = clone_github_repo(normalized_url, force_refresh=payload.force_refresh)
        result = build_test_coverage_heuristics(local_repo_path)

        append_history_event(
            event_type="test_coverage_heuristics",
            source_type="github",
            label=normalized_url.replace("https://github.com/", "").replace(".git", ""),
            repo_path=local_repo_path,
            repo_url=normalized_url,
            payload_summary={"coverage_heuristic_percent": result["counts"]["coverage_heuristic_percent"]},
        )

        return {
            "success": True,
            "repo_url": normalized_url,
            "local_repo_path": local_repo_path,
            "test_coverage": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/issues/dashboard")
def github_issue_dashboard(payload: GithubIssueDashboardRequest):
    try:
        dashboard = build_issue_dashboard(payload.repo_url)
        return {"success": True, "repo_url": dashboard["repo_url"], "issue_dashboard": dashboard}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/contributors/map")
def github_contributor_map(payload: GithubContributorMapRequest):
    try:
        dashboard = build_contributor_ownership_map(payload.repo_url)
        return {"success": True, "repo_url": dashboard["repo_url"], "contributor_map": dashboard}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/prs/dashboard")
def github_pr_dashboard(payload: GithubPRDashboardRequest):
    try:
        dashboard = build_pull_request_dashboard(payload.repo_url)
        return {"success": True, "repo_url": dashboard["repo_url"], "pr_dashboard": dashboard}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/prs/analyze")
def github_pr_analyze(payload: GithubPRAnalysisRequest):
    try:
        result = analyze_pull_request(payload.repo_url, payload.pull_number)
        return {"success": True, "repo_url": result["repo_url"], "pr_analysis": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/github/release/readiness")
def github_release_readiness(payload: GithubReleaseReadinessRequest):
    try:
        result = compute_release_readiness(payload.repo_url)
        return {"success": True, "repo_url": result["repo_url"], "release_readiness": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
