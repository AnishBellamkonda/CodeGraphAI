function renderDeploymentReadinessResponse(data) {
  const root = clearOutput();
  const dr = data.deployment_readiness || {};

  root.appendChild(renderSummaryCard("Deployment Readiness View", dr.repo_name || data.repo_url || "Repository"));

  appendIfNode(root, renderMetadata({
    repo_path: dr.repo_path,
    score: dr.score,
    level: dr.level
  }));

  if (dr.detected) {
    root.appendChild(renderSummaryCard("Detected Signals", JSON.stringify(dr.detected, null, 2)));
  }

  if (dr.reasons?.length) {
    root.appendChild(renderSummaryCard("Why This Score", dr.reasons.join("\n")));
  }

  if (dr.recommended_actions?.length) {
    root.appendChild(renderSummaryCard("Recommended Actions", dr.recommended_actions.join("\n")));
  }

  if (dr.notes?.length) {
    root.appendChild(renderSummaryCard("Notes", dr.notes.join("\n")));
  }

  if (data.local_repo_path) {
    root.appendChild(renderSummaryCard("Local Cache Path", data.local_repo_path));
  }
}

const __originalRenderResponseDeployment = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.deployment_readiness) {
    renderDeploymentReadinessResponse(data);
    return;
  }
  __originalRenderResponseDeployment(data);
};

async function loadLocalDeploymentReadiness() {
  const repoPath = getRepoPath();

  if (!repoPath) {
    renderError({ error: true, detail: "Enter a local repo path first." });
    return;
  }

  await postData("/deployment/readiness", {
    repo_path: repoPath
  });
}

async function loadGithubDeploymentReadiness() {
  const repoUrl = getRepoUrl();

  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  const data = await postData("/github/deployment/readiness", {
    repo_url: repoUrl
  });

  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}
