function getWatchName() {
  return document.getElementById("watchName").value.trim() || "Repo Watch";
}

function getWatchMinDeployment() {
  return Number(document.getElementById("watchMinDeployment").value || 60);
}

function getWatchMinCoverage() {
  return Number(document.getElementById("watchMinCoverage").value || 40);
}

function getWatchMaxRiskyUntested() {
  return Number(document.getElementById("watchMaxRiskyUntested").value || 10);
}

function renderWatchPanel(items) {
  const root = document.getElementById("watchPanel");
  if (!root) return;

  root.innerHTML = "";

  if (!items || items.length === 0) {
    root.textContent = "No saved watches yet.";
    return;
  }

  items.forEach((item) => {
    const card = el("div", "context-card");

    const header = el("div", "context-header");
    header.appendChild(el("div", "", `${item.name} • ${item.source_type}`));
    header.appendChild(el("div", "", item.created_at || item.checked_at || ""));

    const body = el(
      "div",
      "context-text",
      [
        item.repo_url ? `Repo URL: ${item.repo_url}` : "",
        item.repo_path ? `Repo Path: ${item.repo_path}` : "",
        item.thresholds ? `Thresholds: ${JSON.stringify(item.thresholds, null, 2)}` : "",
        item.status ? `Status: ${item.status}` : "",
        item.deployment_score !== undefined ? `Deployment Score: ${item.deployment_score}` : "",
        item.test_coverage_percent !== undefined ? `Test Coverage %: ${item.test_coverage_percent}` : "",
        item.risky_untested_count !== undefined ? `Risky Untested Files: ${item.risky_untested_count}` : "",
        item.alerts?.length ? `Alerts:\n${item.alerts.map(a => `[${a.severity}] ${a.message}`).join("\n")}` : ""
      ].filter(Boolean).join("\n")
    );

    card.appendChild(header);
    card.appendChild(body);

    if (item.id) {
      const row = el("div", "button-row");
      const btn = el("button", "", "Delete Watch");
      btn.onclick = () => deleteSingleWatch(item.id);
      row.appendChild(btn);
      card.appendChild(row);
    }

    root.appendChild(card);
  });
}

function renderWatchCheckResponse(data) {
  const root = clearOutput();
  const results = data.watch_check || [];

  root.appendChild(renderSummaryCard("Watch Check Results", `${results.length} watches checked`));

  const alertCount = results.filter(item => item.status === "alert").length;
  appendIfNode(root, renderMetadata({
    total_watches: results.length,
    watches_in_alert: alertCount,
    watches_ok: results.filter(item => item.status === "ok").length,
    watches_error: results.filter(item => item.status === "error").length
  }));

  results.forEach((item) => {
    const block = el("div", "block");
    block.appendChild(el("div", "block-title", `${item.name} • ${item.status}`));

    const text = [
      `Deployment Score: ${item.deployment_score ?? "N/A"}`,
      `Deployment Level: ${item.deployment_level ?? "N/A"}`,
      `Test Coverage %: ${item.test_coverage_percent ?? "N/A"}`,
      `Risky Untested Files: ${item.risky_untested_count ?? "N/A"}`,
      item.alerts?.length ? `Alerts:\n${item.alerts.map(a => `[${a.severity}] ${a.message}`).join("\n")}` : "Alerts:\nNone"
    ].join("\n");

    block.appendChild(el("div", "summary-text", text));
    root.appendChild(block);
  });

  renderWatchPanel(results);
}

const __originalRenderResponseWatch = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.watch_check) {
    renderWatchCheckResponse(data);
    return;
  }

  if (data && data.watch_create) {
    const root = clearOutput();
    root.appendChild(renderSummaryCard("Watch Created", JSON.stringify(data.watch_create, null, 2)));
    loadWatches();
    return;
  }

  if (data && data.watch_deleted !== undefined) {
    const root = clearOutput();
    root.appendChild(renderSummaryCard("Watch Delete", data.watch_deleted ? "Watch deleted" : "Watch not found"));
    loadWatches();
    return;
  }

  if (data && data.watch_cleared) {
    const root = clearOutput();
    root.appendChild(renderSummaryCard("Watch Mode", "All watches cleared"));
    loadWatches();
    return;
  }

  __originalRenderResponseWatch(data);
};

async function loadWatches() {
  const root = document.getElementById("watchPanel");
  if (!root) return;

  root.textContent = "Loading watches...";

  try {
    const response = await fetch("/watch/list");
    const data = await response.json().catch(() => null);

    if (!response.ok || !data) {
      root.textContent = JSON.stringify(data, null, 2);
      return;
    }

    renderWatchPanel(data.watches || []);
  } catch (error) {
    root.textContent = `Watch load error: ${error.message}`;
  }
}

async function createLocalWatch() {
  const repoPath = getRepoPath();
  if (!repoPath) {
    renderError({ error: true, detail: "Enter a local repo path first." });
    return;
  }

  await postData("/watch/create", {
    name: getWatchName(),
    source_type: "local",
    repo_path: repoPath,
    min_deployment_score: getWatchMinDeployment(),
    min_test_coverage: getWatchMinCoverage(),
    max_risky_untested: getWatchMaxRiskyUntested()
  });
}

async function createGithubWatch() {
  const repoUrl = getRepoUrl();
  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  await postData("/watch/create", {
    name: getWatchName(),
    source_type: "github",
    repo_url: repoUrl,
    min_deployment_score: getWatchMinDeployment(),
    min_test_coverage: getWatchMinCoverage(),
    max_risky_untested: getWatchMaxRiskyUntested()
  });
}

async function checkWatches() {
  await postData("/watch/check", {
    force_refresh_github: false
  });
}

async function deleteSingleWatch(watchId) {
  await postData("/watch/delete", {
    watch_id: watchId
  });
}

async function clearAllWatches() {
  await postData("/watch/clear", {});
}

window.addEventListener("DOMContentLoaded", () => {
  loadWatches();
});
