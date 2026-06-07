let activeRepoPath = "";

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

function clearOutput() {
  const root = document.getElementById("renderedOutput");
  root.innerHTML = "";
  return root;
}

function renderLoading() {
  const root = clearOutput();
  root.appendChild(el("div", "loading", "Loading..."));
}

function renderError(data) {
  const root = clearOutput();
  const box = el("div", "error-box");
  box.textContent = JSON.stringify(data, null, 2);
  root.appendChild(box);
}

function setActiveRepoPath(path) {
  if (path) activeRepoPath = path;
}

function appendIfNode(root, node) {
  if (node instanceof Node) {
    root.appendChild(node);
  }
}

function normalizeRepoPath(value) {
  const path = (value || "").trim();
  if (!path) return "";
  if (path.startsWith("/")) return path;
  if (path.startsWith("Users/")) return "/" + path;
  return path;
}

function renderMetadata(metadata) {
  if (!metadata) return null;

  const block = el("div", "block");
  block.appendChild(el("div", "block-title", "Metadata"));

  const grid = el("div", "kv-grid");

  Object.entries(metadata).forEach(([key, value]) => {
    const card = el("div", "kv-card");
    card.appendChild(el("div", "kv-title", key));
    const valueDiv = el("div", "kv-value");
    valueDiv.textContent =
      typeof value === "object" ? JSON.stringify(value, null, 2) : String(value);
    card.appendChild(valueDiv);
    grid.appendChild(card);
  });

  block.appendChild(grid);
  return block;
}

function renderSummaryCard(title, text) {
  const block = el("div", "block");
  block.appendChild(el("div", "block-title", title));
  block.appendChild(el("div", "summary-text", text));
  return block;
}

function renderFileList(files) {
  if (!files || files.length === 0) return null;

  const block = el("div", "block");
  block.appendChild(el("div", "block-title", "Relevant Files"));

  const wrap = el("div", "file-chip-wrap");
  const uniqueFiles = [...new Set(files)];

  uniqueFiles.forEach((file) => {
    const chip = el("div", "file-chip", file);
    chip.onclick = () => loadFileContent(file);
    wrap.appendChild(chip);
  });

  block.appendChild(wrap);
  return block;
}

function renderContexts(contexts) {
  if (!contexts || contexts.length === 0) return null;

  const block = el("div", "block");
  block.appendChild(el("div", "block-title", "Retrieved Context"));

  contexts.forEach((ctx) => {
    const card = el("div", "context-card");

    const header = el("div", "context-header");
    header.appendChild(el("div", "", ctx.file_path || "unknown file"));
    header.appendChild(el("div", "", `chunk ${ctx.chunk_index ?? "-"}`));

    const body = el("div", "context-text", ctx.content || "");
    card.appendChild(header);
    card.appendChild(body);

    card.onclick = () => loadFileContent(ctx.file_path);

    block.appendChild(card);
  });

  return block;
}

function renderArchitectureSection(title, items) {
  if (!items || items.length === 0) return null;

  const block = el("div", "block");
  block.appendChild(el("div", "block-title", title));

  const wrap = el("div", "file-chip-wrap");
  items.forEach((item) => {
    const text = typeof item === "string" ? item : `${item.module} • ${item.files}`;
    const chip = el("div", "file-chip", text);

    if (typeof item === "string" && !text.includes(" • ")) {
      chip.onclick = () => loadFileContent(item);
    }

    wrap.appendChild(chip);
  });

  block.appendChild(wrap);
  return block;
}

function renderAnalyzeResponse(data) {
  const root = clearOutput();
  setActiveRepoPath(data.data.repo_path);

  root.appendChild(renderSummaryCard("Repository", data.data.repo_name || "Unknown"));
  appendIfNode(root, renderMetadata({
    repo_path: data.data.repo_path,
    total_files: data.data.total_files,
    languages: data.data.languages,
    frameworks: data.data.frameworks
  }));

  if (data.data.top_level_structure) {
    root.appendChild(renderSummaryCard("Top Level Structure", data.data.top_level_structure.join("\n")));
  }

  if (data.data.important_files) {
    appendIfNode(root, renderFileList(data.data.important_files.map((f) => f.path)));
  }
}

function renderSummaryResponse(data) {
  const root = clearOutput();
  setActiveRepoPath(data.local_repo_path || data.repo_path);

  root.appendChild(renderSummaryCard("Repository", data.repo_name || data.repo_url || "Repository"));
  appendIfNode(root, renderMetadata(data.metadata));

  if (data.local_repo_path) {
    root.appendChild(renderSummaryCard("Local Cache Path", data.local_repo_path));
  }

  root.appendChild(renderSummaryCard("AI Summary", data.summary || "No summary returned"));
}

function renderIndexResponse(data) {
  const root = clearOutput();
  setActiveRepoPath(data.local_repo_path || data.repo_path);

  root.appendChild(renderSummaryCard("Index Status", "Repository indexed successfully"));
  appendIfNode(root, renderMetadata(data.data || {}));

  if (data.local_repo_path) {
    root.appendChild(renderSummaryCard("Local Cache Path", data.local_repo_path));
  }
}

function renderAskResponse(data) {
  const root = clearOutput();
  setActiveRepoPath(data.local_repo_path || data.repo_path);

  root.appendChild(renderSummaryCard("Question", data.question || "No question"));
  root.appendChild(renderSummaryCard("Answer", data.answer || "No answer"));

  appendIfNode(root, renderFileList((data.contexts || []).map((c) => c.file_path)));
  appendIfNode(root, renderContexts(data.contexts));
}

function renderArchitectureMapResponse(data) {
  const root = clearOutput();
  const map = data.architecture_map || {};
  setActiveRepoPath(data.local_repo_path || data.repo_path || map.repo_path);

  root.appendChild(renderSummaryCard("Architecture Map", map.repo_name || data.repo_url || "Repository"));

  appendIfNode(root, renderMetadata({
    repo_path: map.repo_path,
    total_scanned_files: map.total_scanned_files
  }));

  appendIfNode(root, renderArchitectureSection("Top Modules", map.top_modules));
  appendIfNode(root, renderArchitectureSection("Entry Points", map.entry_points));
  appendIfNode(root, renderArchitectureSection("API Routes", map.api_routes));
  appendIfNode(root, renderArchitectureSection("Services", map.services));
  appendIfNode(root, renderArchitectureSection("Data Models", map.data_models));
  appendIfNode(root, renderArchitectureSection("Data Access", map.data_access));
  appendIfNode(root, renderArchitectureSection("Frontend", map.frontend));
  appendIfNode(root, renderArchitectureSection("Config / Infra", map.config_infra));
  appendIfNode(root, renderArchitectureSection("Tests", map.tests));
  appendIfNode(root, renderArchitectureSection("Docs", map.docs));

  if (map.likely_request_flow?.length) {
    root.appendChild(renderSummaryCard("Likely Request Flow", map.likely_request_flow.join("\n")));
  }
}

function renderOnboardingGuideResponse(data) {
  const root = clearOutput();
  const guide = data.onboarding_guide || {};
  setActiveRepoPath(data.local_repo_path || data.repo_path || guide.repo_path);

  root.appendChild(renderSummaryCard("Onboarding Guide", guide.repo_name || data.repo_url || "Repository"));
  appendIfNode(root, renderMetadata(guide.metadata));
  appendIfNode(root, renderArchitectureSection("First Files To Read", guide.first_files_to_read));

  if (guide.learning_path?.length) {
    root.appendChild(renderSummaryCard("Recommended Learning Path", guide.learning_path.join("\n")));
  }

  if (guide.focus_areas?.length) {
    root.appendChild(renderSummaryCard("Focus Areas", guide.focus_areas.join("\n")));
  }

  if (guide.likely_workflows?.length) {
    root.appendChild(renderSummaryCard("Likely Workflows", guide.likely_workflows.join("\n")));
  }
}

function renderReportExportResponse(data) {
  const root = clearOutput();
  const report = data.report_export || {};
  setActiveRepoPath(data.local_repo_path || data.repo_path || report.repo_path);

  root.appendChild(renderSummaryCard("Report Export", report.repo_name || data.repo_url || "Repository"));

  appendIfNode(root, renderMetadata({
    repo_path: report.repo_path,
    report_path: report.report_path
  }));

  if (report.report_path) {
    root.appendChild(renderSummaryCard("Saved Report Path", report.report_path));
  }

  if (report.markdown_preview) {
    root.appendChild(renderSummaryCard("Markdown Preview", report.markdown_preview));
  }
}

function renderRepoCompareResponse(data) {
  const root = clearOutput();
  const cmp = data.repo_compare || {};

  root.appendChild(renderSummaryCard("Repo Comparison", `${cmp.repo_a?.label || "Repo A"} vs ${cmp.repo_b?.label || "Repo B"}`));

  appendIfNode(root, renderMetadata({
    repo_a_path: cmp.repo_a?.repo_path,
    repo_b_path: cmp.repo_b?.repo_path,
    repo_a_total_files: cmp.repo_a?.total_files,
    repo_b_total_files: cmp.repo_b?.total_files
  }));

  appendIfNode(root, renderSummaryCard("Shared Frameworks", (cmp.comparison?.shared_frameworks || []).join("\n") || "None"));
  appendIfNode(root, renderSummaryCard("Frameworks Only In Repo A", (cmp.comparison?.frameworks_only_in_a || []).join("\n") || "None"));
  appendIfNode(root, renderSummaryCard("Frameworks Only In Repo B", (cmp.comparison?.frameworks_only_in_b || []).join("\n") || "None"));

  appendIfNode(root, renderSummaryCard("Shared Languages", (cmp.comparison?.shared_languages || []).join("\n") || "None"));
  appendIfNode(root, renderSummaryCard("Languages Only In Repo A", (cmp.comparison?.languages_only_in_a || []).join("\n") || "None"));
  appendIfNode(root, renderSummaryCard("Languages Only In Repo B", (cmp.comparison?.languages_only_in_b || []).join("\n") || "None"));

  appendIfNode(root, renderArchitectureSection("Repo A Top Modules", cmp.repo_a?.top_modules));
  appendIfNode(root, renderArchitectureSection("Repo B Top Modules", cmp.repo_b?.top_modules));

  if (cmp.comparison?.difference_notes?.length) {
    root.appendChild(renderSummaryCard("Architecture Differences", cmp.comparison.difference_notes.join("\n")));
  }
}

function renderGeneric(data) {
  const root = clearOutput();
  const block = el("div", "block");
  block.appendChild(el("div", "block-title", "Raw Response"));
  block.appendChild(el("div", "code-text", JSON.stringify(data, null, 2)));
  root.appendChild(block);
}

function renderResponse(data) {
  if (!data || data.error) {
    renderError(data || { error: true, detail: "Unknown error" });
    return;
  }

  if (data.repo_compare) {
    renderRepoCompareResponse(data);
    return;
  }

  if (data.report_export) {
    renderReportExportResponse(data);
    return;
  }

  if (data.onboarding_guide) {
    renderOnboardingGuideResponse(data);
    return;
  }

  if (data.architecture_map) {
    renderArchitectureMapResponse(data);
    return;
  }

  if (data.summary) {
    renderSummaryResponse(data);
    return;
  }

  if (data.question && data.answer) {
    renderAskResponse(data);
    return;
  }

  if (data.data && (data.data.collection_name || data.data.status)) {
    renderIndexResponse(data);
    return;
  }

  if (data.data && data.data.repo_name) {
    renderAnalyzeResponse(data);
    return;
  }

  renderGeneric(data);
}

async function postData(url, payload) {
  renderLoading();

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      renderError({
        error: true,
        status: response.status,
        detail: data
      });
      return null;
    }

    renderResponse(data);
    return data;
  } catch (error) {
    renderError({
      error: true,
      message: error.message
    });
    return null;
  }
}

function renderFileTree(items) {
  const root = document.getElementById("fileTree");
  root.innerHTML = "";

  if (!items || items.length === 0) {
    root.textContent = "No files found.";
    return;
  }

  const list = el("div", "file-tree-list");

  items.forEach((item) => {
    const row = el(
      "div",
      `file-row ${item.type}`,
      `${"  ".repeat(item.depth)}${item.type === "dir" ? "📁" : "📄"} ${item.path}`
    );
    if (item.type === "file") {
      row.onclick = () => loadFileContent(item.path);
    }
    list.appendChild(row);
  });

  root.appendChild(list);
}

function detectLanguage(filePath) {
  const path = (filePath || "").toLowerCase();

  if (path.endsWith(".py")) return "python";
  if (path.endsWith(".js")) return "javascript";
  if (path.endsWith(".ts")) return "typescript";
  if (path.endsWith(".tsx")) return "tsx";
  if (path.endsWith(".jsx")) return "jsx";
  if (path.endsWith(".java")) return "java";
  if (path.endsWith(".go")) return "go";
  if (path.endsWith(".json")) return "json";
  if (path.endsWith(".html")) return "xml";
  if (path.endsWith(".css")) return "css";
  if (path.endsWith(".scss")) return "scss";
  if (path.endsWith(".md")) return "markdown";
  if (path.endsWith(".sh")) return "bash";
  if (path.endsWith(".yml") || path.endsWith(".yaml")) return "yaml";
  if (path.endsWith(".sql")) return "sql";
  if (path.endsWith(".xml")) return "xml";
  if (path.endsWith("dockerfile")) return "dockerfile";
  return "plaintext";
}

function renderFileViewer(data) {
  const root = document.getElementById("fileViewer");
  root.innerHTML = "";

  const language = detectLanguage(data.file_path);

  const header = el("div", "file-viewer-header", data.file_path + (data.truncated ? " (truncated)" : ""));
  const meta = el("div", "file-viewer-meta", `Language: ${language}`);

  const wrapper = el("div", "file-viewer-content");
  const pre = document.createElement("pre");
  const code = document.createElement("code");

  code.className = `language-${language}`;
  code.textContent = data.content || "";

  pre.appendChild(code);
  wrapper.appendChild(pre);

  root.appendChild(header);
  root.appendChild(meta);
  root.appendChild(wrapper);

  if (window.hljs) {
    window.hljs.highlightElement(code);
  }
}

async function loadFileTree(repoPath) {
  const treeRoot = document.getElementById("fileTree");
  treeRoot.textContent = "Loading files...";

  try {
    const response = await fetch("/files/tree", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_path: repoPath })
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      treeRoot.textContent = JSON.stringify(data, null, 2);
      return;
    }

    setActiveRepoPath(repoPath);
    renderFileTree(data.items);
  } catch (error) {
    treeRoot.textContent = `File tree error: ${error.message}`;
  }
}

async function loadFileContent(filePath) {
  const viewerRoot = document.getElementById("fileViewer");

  if (!activeRepoPath) {
    viewerRoot.textContent = "Load a repo first.";
    return;
  }

  viewerRoot.textContent = "Loading file...";

  try {
    const response = await fetch("/files/content", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        repo_path: activeRepoPath,
        file_path: filePath
      })
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      viewerRoot.textContent = JSON.stringify(data, null, 2);
      return;
    }

    renderFileViewer(data);
  } catch (error) {
    viewerRoot.textContent = `File viewer error: ${error.message}`;
  }
}

async function loadSavedRepos() {
  const select = document.getElementById("savedRepos");
  if (!select) return;

  select.innerHTML = '<option value="">Loading...</option>';

  try {
    const response = await fetch("/repos");
    const data = await response.json().catch(() => null);

    if (!response.ok || !data || !data.repos) {
      select.innerHTML = '<option value="">Failed to load repos</option>';
      return;
    }

    select.innerHTML = "";

    if (data.repos.length === 0) {
      select.innerHTML = '<option value="">No saved repos yet</option>';
      return;
    }

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Select a saved repo";
    select.appendChild(defaultOption);

    data.repos.forEach((repo) => {
      const option = document.createElement("option");
      option.value = repo.repo_url;
      option.textContent = `${repo.repo_url} ${repo.indexed ? "• indexed" : "• not indexed"}`;
      option.dataset.localRepoPath = repo.local_repo_path || "";
      select.appendChild(option);
    });
  } catch (error) {
    select.innerHTML = '<option value="">Error loading repos</option>';
  }
}

function useSelectedRepo() {
  const select = document.getElementById("savedRepos");
  if (!select) return;
  const repoUrl = select.value;
  if (!repoUrl) return;
  document.getElementById("repoUrl").value = repoUrl;
}

async function refreshSelectedRepo() {
  const repoUrl = document.getElementById("repoUrl").value.trim();
  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  const data = await postData("/github/index", {
    repo_url: repoUrl,
    force_refresh: true
  });

  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}

function getRepoPath() {
  return normalizeRepoPath(document.getElementById("repoPath").value);
}

function getRepoUrl() {
  return document.getElementById("repoUrl").value.trim();
}

function getQuestion() {
  return document.getElementById("question").value.trim();
}

function getCompareRepoPathA() {
  return normalizeRepoPath(document.getElementById("compareRepoPathA").value);
}

function getCompareRepoPathB() {
  return normalizeRepoPath(document.getElementById("compareRepoPathB").value);
}

function getCompareRepoUrlA() {
  return document.getElementById("compareRepoUrlA").value.trim();
}

function getCompareRepoUrlB() {
  return document.getElementById("compareRepoUrlB").value.trim();
}

function analyzeLocal() {
  postData("/analyze", { repo_path: getRepoPath() });
}

function summarizeLocal() {
  postData("/summarize", { repo_path: getRepoPath() });
}

function indexLocal() {
  postData("/index", { repo_path: getRepoPath() });
}

function askLocal() {
  postData("/ask", {
    repo_path: getRepoPath(),
    question: getQuestion()
  });
}

async function loadLocalTree() {
  const repoPath = getRepoPath();
  if (!repoPath) {
    document.getElementById("fileTree").textContent = "Enter a local repo path first.";
    return;
  }
  await loadFileTree(repoPath);
}

async function loadLocalArchitectureMap() {
  const repoPath = getRepoPath();
  if (!repoPath) {
    renderError({ error: true, detail: "Enter a local repo path first." });
    return;
  }
  await postData("/architecture/map", { repo_path: repoPath });
}

async function loadLocalOnboardingGuide() {
  const repoPath = getRepoPath();
  if (!repoPath) {
    renderError({ error: true, detail: "Enter a local repo path first." });
    return;
  }
  await postData("/onboarding/guide", { repo_path: repoPath });
}

async function exportLocalReport() {
  const repoPath = getRepoPath();
  if (!repoPath) {
    renderError({ error: true, detail: "Enter a local repo path first." });
    return;
  }
  await postData("/report/export", { repo_path: repoPath });
}

async function compareLocalRepos() {
  const repoPathA = getCompareRepoPathA();
  const repoPathB = getCompareRepoPathB();

  if (!repoPathA || !repoPathB) {
    renderError({ error: true, detail: "Enter both local repo paths first." });
    return;
  }

  await postData("/compare/repos", {
    repo_path_a: repoPathA,
    repo_path_b: repoPathB
  });
}

async function summarizeGithub() {
  const data = await postData("/github/summarize", { repo_url: getRepoUrl() });
  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}

async function indexGithub() {
  const data = await postData("/github/index", { repo_url: getRepoUrl() });
  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}

async function askGithub() {
  const data = await postData("/github/ask", {
    repo_url: getRepoUrl(),
    question: getQuestion()
  });
  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}

async function loadGithubTree() {
  const repoUrl = getRepoUrl();
  if (!repoUrl) {
    document.getElementById("fileTree").textContent = "Enter a GitHub URL first.";
    return;
  }

  const data = await postData("/github/index", { repo_url: repoUrl });
  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}

async function loadGithubArchitectureMap() {
  const repoUrl = getRepoUrl();
  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  const data = await postData("/github/architecture/map", { repo_url: repoUrl });
  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}

async function loadGithubOnboardingGuide() {
  const repoUrl = getRepoUrl();
  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  const data = await postData("/github/onboarding/guide", { repo_url: repoUrl });
  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}

async function exportGithubReport() {
  const repoUrl = getRepoUrl();
  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  const data = await postData("/github/report/export", { repo_url: repoUrl });
  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}

async function compareGithubRepos() {
  const repoUrlA = getCompareRepoUrlA();
  const repoUrlB = getCompareRepoUrlB();

  if (!repoUrlA || !repoUrlB) {
    renderError({ error: true, detail: "Enter both GitHub repo URLs first." });
    return;
  }

  const data = await postData("/github/compare/repos", {
    repo_url_a: repoUrlA,
    repo_url_b: repoUrlB
  });

  if (data && data.local_repo_a) {
    await loadFileTree(data.local_repo_a);
    await loadSavedRepos();
  }
}

window.addEventListener("DOMContentLoaded", () => {
  loadSavedRepos();
});
