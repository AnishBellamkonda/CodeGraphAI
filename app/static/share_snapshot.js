function renderShareSnapshotResponse(data) {
  const root = clearOutput();
  const snap = data.share_snapshot || {};

  root.appendChild(renderSummaryCard("Portfolio / Share Snapshot", snap.repo_name || data.repo_url || "Repository"));

  appendIfNode(root, renderMetadata({
    repo_path: snap.repo_path,
    share_path: snap.share_path,
    generated_at: snap.generated_at
  }));

  if (snap.highlights) {
    root.appendChild(renderSummaryCard("Highlights", JSON.stringify(snap.highlights, null, 2)));
  }

  if (data.local_repo_path) {
    root.appendChild(renderSummaryCard("Local Cache Path", data.local_repo_path));
  }
}

const __originalRenderResponseShare = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.share_snapshot) {
    renderShareSnapshotResponse(data);
    return;
  }
  __originalRenderResponseShare(data);
};

async function createLocalShareSnapshot() {
  const repoPath = getRepoPath();

  if (!repoPath) {
    renderError({ error: true, detail: "Enter a local repo path first." });
    return;
  }

  await postData("/share/snapshot", {
    repo_path: repoPath
  });
}

async function createGithubShareSnapshot() {
  const repoUrl = getRepoUrl();

  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  const data = await postData("/github/share/snapshot", {
    repo_url: repoUrl
  });

  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}
