function renderPRDashboardResponse(data) {
  const root = clearOutput();
  const dashboard = data.pr_dashboard || {};

  root.appendChild(renderSummaryCard("Repository", dashboard.repo || data.repo_url || "Unknown"));

  root.appendChild(
    renderMetadata({
      rate_limit_mode: dashboard.rate_limit_mode,
      sampled_pull_requests: dashboard.sampled_pull_requests,
      average_merge_hours: dashboard.average_merge_hours ?? "N/A",
      open_prs: dashboard.counts?.open_prs ?? 0,
      merged_prs: dashboard.counts?.merged_prs ?? 0,
      closed_without_merge: dashboard.counts?.closed_without_merge ?? 0,
      draft_prs: dashboard.counts?.draft_prs ?? 0
    })
  );

  if (dashboard.top_authors && dashboard.top_authors.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Top PR Authors"));
    const wrap = el("div", "file-chip-wrap");

    dashboard.top_authors.forEach((item) => {
      wrap.appendChild(el("div", "file-chip", `${item.author} • ${item.pull_requests}`));
    });

    block.appendChild(wrap);
    root.appendChild(block);
  }

  if (dashboard.recent_pull_requests && dashboard.recent_pull_requests.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Recent Pull Requests"));

    dashboard.recent_pull_requests.forEach((pr) => {
      const card = el("div", "context-card");

      const header = el("div", "context-header");
      header.appendChild(el("div", "", `#${pr.number} • ${pr.title}`));
      header.appendChild(el("div", "", `${pr.state}${pr.draft ? " • draft" : ""}`));

      const body = el(
        "div",
        "context-text",
        [
          `Author: ${pr.author || "unknown"}`,
          `Created: ${pr.created_at || "N/A"}`,
          `Merged: ${pr.merged_at || "N/A"}`,
          `Changed files: ${pr.changed_files ?? "N/A"}`,
          `Additions: ${pr.additions ?? "N/A"}`,
          `Deletions: ${pr.deletions ?? "N/A"}`,
          `Commits: ${pr.commits ?? "N/A"}`,
          pr.html_url ? `URL: ${pr.html_url}` : ""
        ].filter(Boolean).join("\n")
      );

      card.appendChild(header);
      card.appendChild(body);
      block.appendChild(card);
    });

    root.appendChild(block);
  }

  if (dashboard.largest_recent_pull_requests && dashboard.largest_recent_pull_requests.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Largest Recent Pull Requests"));

    dashboard.largest_recent_pull_requests.forEach((pr) => {
      const card = el(
        "div",
        "context-card",
        `#${pr.number} • ${pr.title}\nChanged files: ${pr.changed_files ?? "N/A"} | Additions: ${pr.additions ?? "N/A"} | Deletions: ${pr.deletions ?? "N/A"}`
      );
      block.appendChild(card);
    });

    root.appendChild(block);
  }

  if (dashboard.notes && dashboard.notes.length) {
    root.appendChild(renderSummaryCard("Notes", dashboard.notes.join("\n")));
  }
}

function renderPRAnalysisResponse(data) {
  const root = clearOutput();
  const analysis = data.pr_analysis || {};

  root.appendChild(renderSummaryCard("PR", `#${analysis.pull_number} • ${analysis.title || "Unknown PR"}`));

  root.appendChild(
    renderMetadata({
      author: analysis.author || "unknown",
      state: analysis.state || "unknown",
      draft: analysis.draft,
      changed_files: analysis.stats?.changed_files ?? "N/A",
      additions: analysis.stats?.additions ?? "N/A",
      deletions: analysis.stats?.deletions ?? "N/A",
      commits: analysis.stats?.commits ?? "N/A",
      reviews: analysis.stats?.reviews ?? "N/A",
      risk_score: analysis.risk?.score ?? "N/A",
      risk_level: analysis.risk?.level ?? "N/A"
    })
  );

  if (analysis.risk?.reasons?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Risk Reasons"));
    const wrap = el("div", "file-chip-wrap");
    analysis.risk.reasons.forEach((reason) => {
      wrap.appendChild(el("div", "file-chip", reason));
    });
    block.appendChild(wrap);
    root.appendChild(block);
  }

  if (analysis.risk?.critical_paths?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Critical Paths Touched"));
    const wrap = el("div", "file-chip-wrap");
    analysis.risk.critical_paths.forEach((item) => {
      wrap.appendChild(el("div", "file-chip", item));
    });
    block.appendChild(wrap);
    root.appendChild(block);
  }

  if (analysis.top_files?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Changed Files"));
    const wrap = el("div", "file-chip-wrap");
    analysis.top_files.forEach((item) => {
      wrap.appendChild(el("div", "file-chip", item));
    });
    block.appendChild(wrap);
    root.appendChild(block);
  }

  root.appendChild(renderSummaryCard("AI PR Analysis", analysis.ai_summary || "No analysis returned"));

  if (analysis.html_url) {
    root.appendChild(renderSummaryCard("GitHub URL", analysis.html_url));
  }
}

function renderReleaseReadinessResponse(data) {
  const root = clearOutput();
  const readiness = data.release_readiness || {};

  root.appendChild(renderSummaryCard("Repository", readiness.repo || data.repo_url || "Unknown"));

  root.appendChild(
    renderMetadata({
      release_score: readiness.score ?? "N/A",
      release_level: readiness.level ?? "N/A",
      open_prs: readiness.signals?.open_prs ?? "N/A",
      draft_prs: readiness.signals?.draft_prs ?? "N/A",
      closed_without_merge: readiness.signals?.closed_without_merge ?? "N/A",
      average_merge_hours: readiness.signals?.average_merge_hours ?? "N/A",
      recent_open_issues_sampled: readiness.signals?.recent_open_issues_sampled ?? "N/A",
      repo_open_issues_count: readiness.signals?.repo_open_issues_count ?? "N/A",
      primary_language: readiness.signals?.primary_language ?? "N/A",
      default_branch: readiness.signals?.default_branch ?? "N/A"
    })
  );

  if (readiness.reasons?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Why This Score"));
    const wrap = el("div", "file-chip-wrap");
    readiness.reasons.forEach((reason) => {
      wrap.appendChild(el("div", "file-chip", reason));
    });
    block.appendChild(wrap);
    root.appendChild(block);
  }

  if (readiness.recommended_actions?.length) {
    root.appendChild(
      renderSummaryCard("Recommended Actions", readiness.recommended_actions.join("\n"))
    );
  }

  if (readiness.top_recent_issue_titles?.length) {
    root.appendChild(
      renderSummaryCard("Recent Open Issues", readiness.top_recent_issue_titles.join("\n"))
    );
  }
}

const _originalRenderResponse = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.pr_dashboard) {
    renderPRDashboardResponse(data);
    return;
  }

  if (data && data.pr_analysis) {
    renderPRAnalysisResponse(data);
    return;
  }

  if (data && data.release_readiness) {
    renderReleaseReadinessResponse(data);
    return;
  }

  _originalRenderResponse(data);
};

function getPRNumber() {
  return Number(document.getElementById("prNumber").value);
}

async function loadGithubPRDashboard() {
  const repoUrl = getRepoUrl();
  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  await postData("/github/prs/dashboard", { repo_url: repoUrl });
}

async function analyzeGithubPR() {
  const repoUrl = getRepoUrl();
  const pullNumber = getPRNumber();

  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  if (!pullNumber || Number.isNaN(pullNumber)) {
    renderError({ error: true, detail: "Enter a valid pull request number." });
    return;
  }

  await postData("/github/prs/analyze", {
    repo_url: repoUrl,
    pull_number: pullNumber
  });
}

async function loadReleaseReadiness() {
  const repoUrl = getRepoUrl();

  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  await postData("/github/release/readiness", {
    repo_url: repoUrl
  });
}
