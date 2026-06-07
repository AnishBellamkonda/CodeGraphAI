function renderIssueDashboardResponse(data) {
  const root = clearOutput();
  const dashboard = data.issue_dashboard || {};

  root.appendChild(renderSummaryCard("Issue Dashboard", dashboard.repo || data.repo_url || "Repository"));

  appendIfNode(root, renderMetadata({
    open_issues_sampled: dashboard.counts?.open_issues_sampled ?? 0,
    stale_issues: dashboard.counts?.stale_issues ?? 0,
    unlabeled_issues: dashboard.counts?.unlabeled_issues ?? 0,
    unassigned_issues: dashboard.counts?.unassigned_issues ?? 0
  }));

  if (dashboard.top_labels?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Top Labels"));
    const wrap = el("div", "file-chip-wrap");
    dashboard.top_labels.forEach((item) => {
      wrap.appendChild(el("div", "file-chip", `${item.label} • ${item.count}`));
    });
    block.appendChild(wrap);
    root.appendChild(block);
  }

  if (dashboard.top_assignees?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Top Assignees"));
    const wrap = el("div", "file-chip-wrap");
    dashboard.top_assignees.forEach((item) => {
      wrap.appendChild(el("div", "file-chip", `${item.assignee} • ${item.count}`));
    });
    block.appendChild(wrap);
    root.appendChild(block);
  }

  if (dashboard.recent_issues?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Recent Issues"));

    dashboard.recent_issues.forEach((issue) => {
      const card = el("div", "context-card");

      const header = el("div", "context-header");
      header.appendChild(el("div", "", `#${issue.number} • ${issue.title}`));
      header.appendChild(el("div", "", issue.updated_at || ""));

      const body = el(
        "div",
        "context-text",
        [
          `Created: ${issue.created_at || "N/A"}`,
          `Comments: ${issue.comments ?? "N/A"}`,
          `Labels: ${(issue.labels || []).join(", ") || "None"}`,
          `Assignees: ${(issue.assignees || []).join(", ") || "None"}`,
          issue.html_url ? `URL: ${issue.html_url}` : ""
        ].filter(Boolean).join("\n")
      );

      card.appendChild(header);
      card.appendChild(body);
      block.appendChild(card);
    });

    root.appendChild(block);
  }

  if (dashboard.stale_issue_titles?.length) {
    root.appendChild(renderSummaryCard("Stale Issue Titles", dashboard.stale_issue_titles.join("\n")));
  }

  if (dashboard.notes?.length) {
    root.appendChild(renderSummaryCard("Notes", dashboard.notes.join("\n")));
  }
}

const __originalRenderResponseIssue = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.issue_dashboard) {
    renderIssueDashboardResponse(data);
    return;
  }
  __originalRenderResponseIssue(data);
};

async function loadIssueDashboard() {
  const repoUrl = getRepoUrl();

  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  await postData("/github/issues/dashboard", {
    repo_url: repoUrl
  });
}
