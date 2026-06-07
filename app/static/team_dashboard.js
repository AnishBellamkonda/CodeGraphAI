function renderTeamDashboardResponse(data) {
  const root = clearOutput();
  const td = data.team_dashboard || {};

  root.appendChild(renderSummaryCard("Multi-Repo Team Dashboard", "Workspace overview across saved repositories"));

  appendIfNode(root, renderMetadata(td.summary || {}));

  if (td.repos?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Repo Health Cards"));

    td.repos.forEach((repo) => {
      const card = el("div", "context-card");

      const header = el("div", "context-header");
      header.appendChild(el("div", "", repo.label || "repo"));
      header.appendChild(el("div", "", `${repo.deployment_score} / ${repo.test_coverage_percent}%`));

      const body = el(
        "div",
        "context-text",
        [
          repo.repo_url ? `Repo URL: ${repo.repo_url}` : "",
          repo.local_repo_path ? `Local Path: ${repo.local_repo_path}` : "",
          `Indexed: ${repo.indexed}`,
          `Total Files: ${repo.total_files}`,
          `Frameworks: ${(repo.frameworks || []).join(", ") || "None"}`,
          `Languages: ${JSON.stringify(repo.languages || {}, null, 2)}`,
          `Package Managers: ${(repo.package_managers || []).join(", ") || "None"}`,
          `Deployment Level: ${repo.deployment_level}`,
          `Risky Untested Files: ${repo.risky_untested_count}`,
          `Attached Watches: ${repo.watch_count}`
        ].filter(Boolean).join("\n")
      );

      card.appendChild(header);
      card.appendChild(body);
      block.appendChild(card);
    });

    root.appendChild(block);
  }

  if (td.watches?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Saved Watches"));

    td.watches.forEach((watch) => {
      const card = el(
        "div",
        "context-card",
        [
          `Name: ${watch.name || "watch"}`,
          `Source: ${watch.source_type}`,
          watch.repo_url ? `Repo URL: ${watch.repo_url}` : "",
          watch.repo_path ? `Repo Path: ${watch.repo_path}` : "",
          `Thresholds: ${JSON.stringify(watch.thresholds || {}, null, 2)}`
        ].filter(Boolean).join("\n")
      );
      block.appendChild(card);
    });

    root.appendChild(block);
  }

  if (td.recent_history?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Recent History"));

    td.recent_history.forEach((item) => {
      const card = el(
        "div",
        "context-card",
        [
          `${item.event_type} • ${item.source_type}`,
          `Label: ${item.label || "N/A"}`,
          item.timestamp || "",
          item.repo_url ? `Repo URL: ${item.repo_url}` : "",
          item.repo_path ? `Repo Path: ${item.repo_path}` : ""
        ].filter(Boolean).join("\n")
      );
      block.appendChild(card);
    });

    root.appendChild(block);
  }

  if (td.errors?.length) {
    root.appendChild(renderSummaryCard("Repo Errors", td.errors.map(e => `${e.repo}: ${e.error}`).join("\n")));
  }

  if (td.notes?.length) {
    root.appendChild(renderSummaryCard("Notes", td.notes.join("\n")));
  }
}

const __originalRenderResponseTeamDashboard = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.team_dashboard) {
    renderTeamDashboardResponse(data);
    return;
  }
  __originalRenderResponseTeamDashboard(data);
};

async function loadTeamDashboard() {
  renderLoading();

  try {
    const response = await fetch("/dashboard/team");
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      renderError({
        error: true,
        status: response.status,
        detail: data
      });
      return;
    }

    renderResponse(data);
  } catch (error) {
    renderError({
      error: true,
      message: error.message
    });
  }
}
