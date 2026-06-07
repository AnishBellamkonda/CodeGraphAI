function renderHistoryPanel(items) {
  const root = document.getElementById("historyPanel");
  if (!root) return;

  root.innerHTML = "";

  if (!items || items.length === 0) {
    root.textContent = "No history yet.";
    return;
  }

  items.forEach((item) => {
    const card = el("div", "context-card");

    const header = el("div", "context-header");
    header.appendChild(el("div", "", `${item.event_type} • ${item.source_type}`));
    header.appendChild(el("div", "", item.timestamp || ""));

    const body = el(
      "div",
      "context-text",
      [
        `Label: ${item.label || "N/A"}`,
        item.repo_url ? `Repo URL: ${item.repo_url}` : "",
        item.repo_path ? `Repo Path: ${item.repo_path}` : "",
        item.payload_summary ? `Summary: ${JSON.stringify(item.payload_summary, null, 2)}` : ""
      ].filter(Boolean).join("\n")
    );

    card.appendChild(header);
    card.appendChild(body);
    root.appendChild(card);
  });
}

async function loadHistory() {
  const root = document.getElementById("historyPanel");
  if (!root) return;

  root.textContent = "Loading history...";

  try {
    const response = await fetch("/history");
    const data = await response.json().catch(() => null);

    if (!response.ok || !data) {
      root.textContent = JSON.stringify(data, null, 2);
      return;
    }

    renderHistoryPanel(data.history || []);
  } catch (error) {
    root.textContent = `History error: ${error.message}`;
  }
}

async function clearHistoryPanel() {
  const root = document.getElementById("historyPanel");
  if (!root) return;

  root.textContent = "Clearing history...";

  try {
    const response = await fetch("/history/clear", {
      method: "POST"
    });

    const data = await response.json().catch(() => null);

    if (!response.ok || !data) {
      root.textContent = JSON.stringify(data, null, 2);
      return;
    }

    await loadHistory();
  } catch (error) {
    root.textContent = `Clear history error: ${error.message}`;
  }
}

const __originalPostDataHistory = window.postData;

window.postData = async function(url, payload) {
  const data = await __originalPostDataHistory(url, payload);
  if (data && !url.startsWith("/history")) {
    loadHistory();
  }
  return data;
};

window.addEventListener("DOMContentLoaded", () => {
  loadHistory();
});
