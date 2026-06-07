from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    repo_path: str


class SummarizeRequest(BaseModel):
    repo_path: str


class IndexRequest(BaseModel):
    repo_path: str


class AskRequest(BaseModel):
    repo_path: str
    question: str


class ArchitectureMapRequest(BaseModel):
    repo_path: str


class OnboardingGuideRequest(BaseModel):
    repo_path: str


class ExportReportRequest(BaseModel):
    repo_path: str


class ShareSnapshotRequest(BaseModel):
    repo_path: str


class PortfolioShareRequest(BaseModel):
    repo_path: str


class CompareReposRequest(BaseModel):
    repo_path_a: str
    repo_path_b: str


class ArchitectureDiffRequest(BaseModel):
    repo_path_a: str
    repo_path_b: str


class CopilotRequest(BaseModel):
    repo_path: str
    question: str


class DependencyInsightsRequest(BaseModel):
    repo_path: str


class SystemDesignExplainRequest(BaseModel):
    repo_path: str


class TestCoverageHeuristicsRequest(BaseModel):
    repo_path: str


class DeploymentReadinessRequest(BaseModel):
    repo_path: str


class FileTreeRequest(BaseModel):
    repo_path: str


class FileContentRequest(BaseModel):
    repo_path: str
    file_path: str


class GithubIndexRequest(BaseModel):
    repo_url: str
    force_refresh: bool = False


class GithubSummarizeRequest(BaseModel):
    repo_url: str
    force_refresh: bool = False


class GithubAskRequest(BaseModel):
    repo_url: str
    question: str
    force_refresh: bool = False


class GithubPRDashboardRequest(BaseModel):
    repo_url: str


class GithubPRAnalysisRequest(BaseModel):
    repo_url: str
    pull_number: int


class GithubReleaseReadinessRequest(BaseModel):
    repo_url: str


class GithubArchitectureMapRequest(BaseModel):
    repo_url: str
    force_refresh: bool = False


class GithubOnboardingGuideRequest(BaseModel):
    repo_url: str
    force_refresh: bool = False


class GithubExportReportRequest(BaseModel):
    repo_url: str
    force_refresh: bool = False


class GithubShareSnapshotRequest(BaseModel):
    repo_url: str
    force_refresh: bool = False


class GithubPortfolioShareRequest(BaseModel):
    repo_url: str
    force_refresh: bool = False


class GithubCompareReposRequest(BaseModel):
    repo_url_a: str
    repo_url_b: str
    force_refresh: bool = False


class GithubArchitectureDiffRequest(BaseModel):
    repo_url_a: str
    repo_url_b: str
    force_refresh: bool = False


class GithubCopilotRequest(BaseModel):
    repo_url: str
    question: str
    force_refresh: bool = False


class GithubIssueDashboardRequest(BaseModel):
    repo_url: str


class GithubContributorMapRequest(BaseModel):
    repo_url: str


class GithubDependencyInsightsRequest(BaseModel):
    repo_url: str
    force_refresh: bool = False


class GithubSystemDesignExplainRequest(BaseModel):
    repo_url: str
    force_refresh: bool = False


class GithubTestCoverageHeuristicsRequest(BaseModel):
    repo_url: str
    force_refresh: bool = False


class GithubDeploymentReadinessRequest(BaseModel):
    repo_url: str
    force_refresh: bool = False



class WatchCreateRequest(BaseModel):
    name: str
    source_type: str
    repo_path: str | None = None
    repo_url: str | None = None
    min_deployment_score: int = 60
    min_test_coverage: float = 40.0
    max_risky_untested: int = 10


class WatchDeleteRequest(BaseModel):
    watch_id: str


class WatchCheckRequest(BaseModel):
    force_refresh_github: bool = False


class HealthResponse(BaseModel):
    status: str
