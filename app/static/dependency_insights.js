function renderDependencyInsightsResponse(data) {
  const root = clearOutput();
  const dep = data.dependency_insights || {};

  root.appendChild(renderSummaryCard("Dependency / Package Insights", dep.repo_name || data.repo_url || "Repository"));

  appendIfNode(root, renderMetadata({
    repo_path: dep.repo_path,
    package_managers: (dep.package_managers || []).join(", ") || "None detected"
  }));

  if (dep.dependency_files && Object.keys(dep.dependency_files).length) {
    root.appendChild(renderSummaryCard("Dependency Files", JSON.stringify(dep.dependency_files, null, 2)));
  }

  if (dep.dependency_summary && Object.keys(dep.dependency_summary).length) {
    root.appendChild(renderSummaryCard("Dependency Summary", JSON.stringify(dep.dependency_summary, null, 2)));
  }

  appendIfNode(root, renderArchitectureSection("Infra / Build Files", dep.infra_files || []));

  if (data.local_repo_path) {
    root.appendChild(renderSummaryCard("Local Cache Path", data.local_repo_path));
  }
}

const __originalRenderResponseDeps = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.dependency_insights) {
    renderDependencyInsightsResponse(data);
    return;
  }
  __originalRenderResponseDeps(data);
};

async function loadLocalDependencyInsights() {
  const repoPath = getRepoPath();

  if (!repoPath) {
    renderError({ error: true, detail: "Enter a local repo path first." });
    return;
  }

  await postData("/dependencies/insights", {
    repo_path: repoPath
  });
}

async function loadGithubDependencyInsights() {
  const repoUrl = getRepoUrl();

  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  const data = await postData("/github/dependencies/insights", {
    repo_url: repoUrl
  });

  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}
