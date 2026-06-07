function renderContributorMapResponse(data) {
  const root = clearOutput();
  const dashboard = data.contributor_map || {};

  root.appendChild(renderSummaryCard("Contributor / Ownership Map", dashboard.repo || data.repo_url || "Repository"));

  appendIfNode(root, renderMetadata({
    ownership_signal: dashboard.ownership_signal || "N/A",
    top_contributor_share_percent: dashboard.top_contributor_share_percent ?? "N/A",
    anonymous_contributors: dashboard.anonymous_contributors ?? 0
  }));

  if (dashboard.top_contributors?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Top Contributors"));
    const wrap = el("div", "file-chip-wrap");
    dashboard.top_contributors.forEach((item) => {
      wrap.appendChild(el("div", "file-chip", `${item.login} • ${item.contributions}`));
    });
    block.appendChild(wrap);
    root.appendChild(block);
  }

  if (dashboard.ownership_summary?.length) {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", "Likely Module Ownership"));

    dashboard.ownership_summary.forEach((item) => {
      const card = el("div", "context-card");

      const header = el("div", "context-header");
      header.appendChild(el("div", "", `${item.module}`));
      header.appendChild(el("div", "", `${item.top_owner} • ${item.changed_files_or_pr_touches}`));

      const others = (item.other_owners || [])
        .map((owner) => `${owner.login} (${owner.count})`)
        .join(", ");

      const body = el(
        "div",
        "context-text",
        [
          `Top owner: ${item.top_owner}`,
          `Touches: ${item.changed_files_or_pr_touches}`,
          `Other owners: ${others || "None"}`
        ].join("\n")
      );

      card.appendChild(header);
      card.appendChild(body);
      block.appendChild(card);
    });

    root.appendChild(block);
  }

  if (dashboard.notes?.length) {
    root.appendChild(renderSummaryCard("Notes", dashboard.notes.join("\n")));
  }
}

const __originalRenderResponseContributor = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.contributor_map) {
    renderContributorMapResponse(data);
    return;
  }
  __originalRenderResponseContributor(data);
};

async function loadContributorMap() {
  const repoUrl = getRepoUrl();

  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  await postData("/github/contributors/map", {
    repo_url: repoUrl
  });
}
