function renderSystemDesignResponse(data) {
  const root = clearOutput();
  const sd = data.system_design || {};

  root.appendChild(renderSummaryCard("System Design Auto-Explain", sd.repo_name || data.repo_url || "Repository"));

  appendIfNode(root, renderMetadata(sd.metadata));

  if (sd.narrative) {
    root.appendChild(renderSummaryCard("Design Narrative", sd.narrative));
  }

  appendIfNode(root, renderArchitectureSection("Inferred Components", sd.components || []));

  if (sd.request_flow?.length) {
    root.appendChild(renderSummaryCard("Likely Request / Data Flow", sd.request_flow.join("\n")));
  }

  if (sd.design_risks?.length) {
    root.appendChild(renderSummaryCard("Design Risks / Gaps", sd.design_risks.join("\n")));
  }

  if (data.local_repo_path) {
    root.appendChild(renderSummaryCard("Local Cache Path", data.local_repo_path));
  }
}

const __originalRenderResponseSystemDesign = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.system_design) {
    renderSystemDesignResponse(data);
    return;
  }
  __originalRenderResponseSystemDesign(data);
};

async function loadLocalSystemDesign() {
  const repoPath = getRepoPath();

  if (!repoPath) {
    renderError({ error: true, detail: "Enter a local repo path first." });
    return;
  }

  await postData("/system-design/explain", {
    repo_path: repoPath
  });
}

async function loadGithubSystemDesign() {
  const repoUrl = getRepoUrl();

  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  const data = await postData("/github/system-design/explain", {
    repo_url: repoUrl
  });

  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}
