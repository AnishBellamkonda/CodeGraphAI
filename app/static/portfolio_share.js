function renderPortfolioShareResponse(data) {
  const root = clearOutput();
  const share = data.portfolio_share || {};

  root.appendChild(renderSummaryCard("Portfolio / Share Mode", share.preview_title || share.repo_name || "Repository"));

  appendIfNode(root, renderMetadata({
    repo_path: share.repo_path,
    share_path: share.share_path,
    deployment_score: share.deployment_score,
    test_coverage_percent: share.test_coverage_percent
  }));

  if (share.share_path) {
    root.appendChild(renderSummaryCard("Saved Share Path", share.share_path));
  }

  if (data.local_repo_path) {
    root.appendChild(renderSummaryCard("Local Cache Path", data.local_repo_path));
  }
}

const __originalRenderResponsePortfolio = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.portfolio_share) {
    renderPortfolioShareResponse(data);
    return;
  }
  __originalRenderResponsePortfolio(data);
};

async function createLocalPortfolioShare() {
  const repoPath = getRepoPath();

  if (!repoPath) {
    renderError({ error: true, detail: "Enter a local repo path first." });
    return;
  }

  await postData("/portfolio/share", {
    repo_path: repoPath
  });
}

async function createGithubPortfolioShare() {
  const repoUrl = getRepoUrl();

  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  const data = await postData("/github/portfolio/share", {
    repo_url: repoUrl
  });

  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}
