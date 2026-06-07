function renderTestCoverageResponse(data) {
  const root = clearOutput();
  const tc = data.test_coverage || {};

  root.appendChild(renderSummaryCard("Test Coverage Heuristics", tc.repo_name || data.repo_url || "Repository"));

  appendIfNode(root, renderMetadata(tc.counts));

  appendIfNode(root, renderArchitectureSection("Detected Test Frameworks", tc.detected_test_frameworks || []));
  appendIfNode(root, renderArchitectureSection("Sample Test Files", tc.test_files_sample || []));
  appendIfNode(root, renderArchitectureSection("Risky Untested Files", tc.risky_untested_files || []));

  if (tc.likely_tested_examples?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Likely Tested Examples"));

    tc.likely_tested_examples.forEach((item) => {
      const card = el("div", "context-card");

      const header = el("div", "context-header");
      header.appendChild(el("div", "", item.source_file || "source"));
      header.appendChild(el("div", "", `${(item.matched_tests || []).length} matched tests`));

      const body = el(
        "div",
        "context-text",
        (item.matched_tests || []).join("\n") || "No matched tests"
      );

      card.appendChild(header);
      card.appendChild(body);
      block.appendChild(card);
    });

    root.appendChild(block);
  }

  if (tc.notes?.length) {
    root.appendChild(renderSummaryCard("Notes", tc.notes.join("\n")));
  }

  if (data.local_repo_path) {
    root.appendChild(renderSummaryCard("Local Cache Path", data.local_repo_path));
  }
}

const __originalRenderResponseTestCoverage = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.test_coverage) {
    renderTestCoverageResponse(data);
    return;
  }
  __originalRenderResponseTestCoverage(data);
};

async function loadLocalTestCoverage() {
  const repoPath = getRepoPath();

  if (!repoPath) {
    renderError({ error: true, detail: "Enter a local repo path first." });
    return;
  }

  await postData("/tests/heuristics", {
    repo_path: repoPath
  });
}

async function loadGithubTestCoverage() {
  const repoUrl = getRepoUrl();

  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  const data = await postData("/github/tests/heuristics", {
    repo_url: repoUrl
  });

  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}
