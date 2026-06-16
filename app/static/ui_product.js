const UI_RELEASE = "1001";

const PAGE_TITLES = {
  overview: "Dashboard",
  local: "Local repositories",
  github: "GitHub intelligence",
  compare: "Repository comparison",
  workspace: "AI workspace",
  ops: "Monitoring"
};

const FALLBACK_ICON_PATHS = {
  dashboard: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  folder: '<path d="M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/>',
  git: '<circle cx="6" cy="5" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="8" cy="19" r="2"/><path d="M6 7v4a4 4 0 0 0 4 4h2a6 6 0 0 0 6-6V8M8 17v-2"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  sparkle: '<path d="m12 3 1.4 4.1L17.5 8.5l-4.1 1.4L12 14l-1.4-4.1-4.1-1.4 4.1-1.4Z"/><path d="m18 14 .8 2.2L21 17l-2.2.8L18 20l-.8-2.2L15 17l2.2-.8Z"/>',
  activity: '<path d="M3 12h4l2.2-6 4.2 12 2.2-6H21"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  compare: '<path d="M7 7h12l-3-3M19 7l-3 3M17 17H5l3 3M5 17l3-3"/>',
  file: '<path d="M6 3h8l4 4v14H6Z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
  database: '<ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v6c0 1.7 3.1 3 7 3s7-1.3 7-3V5M5 11v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>',
  network: '<circle cx="12" cy="5" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><path d="m10.8 6.7-4.6 9.5M13.2 6.7l4.6 9.5M7 18h10"/>',
  check: '<circle cx="12" cy="12" r="9"/><path d="m8 12 2.5 2.5L16 9"/>',
  rocket: '<path d="M14 4c3-1 5-1 6-1 0 1 0 3-1 6l-6 6-4-4Z"/><path d="m9 11-4 1-2 2 5 1M13 15l-1 4-2 2-1-5M15 7l2 2"/>',
  users: '<circle cx="9" cy="8" r="3"/><path d="M3 20c.5-4 2.5-6 6-6s5.5 2 6 6M16 7a3 3 0 0 1 0 6M17 14c2.5.5 3.8 2.5 4 5"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  bell: '<path d="M6 9a6 6 0 0 1 12 0c0 7 3 7 3 7H3s3 0 3-7M10 20h4"/>',
  play: '<circle cx="12" cy="12" r="9"/><path d="m10 8 6 4-6 4Z"/>',
  trash: '<path d="M4 7h16M9 7V4h6v3M7 7l1 14h8l1-14M10 11v6M14 11v6"/>',
  refresh: '<path d="M20 7v5h-5M4 17v-5h5M6.5 8a7 7 0 0 1 11-2l2.5 3M17.5 16a7 7 0 0 1-11 2L4 15"/>',
  share: '<circle cx="18" cy="5" r="2"/><circle cx="6" cy="12" r="2"/><circle cx="18" cy="19" r="2"/><path d="m8 11 8-5M8 13l8 5"/>',
  link: '<path d="M10 13a5 5 0 0 0 7 0l2-2a5 5 0 0 0-7-7l-1 1M14 11a5 5 0 0 0-7 0l-2 2a5 5 0 0 0 7 7l1-1"/>',
  message: '<path d="M4 5h16v11H8l-4 4Z"/><path d="M8 9h8M8 12h5"/>',
  device: '<rect x="3" y="5" width="18" height="12" rx="2"/><path d="M8 21h8M12 17v4"/>',
  bookmark: '<path d="M6 3h12v18l-6-4-6 4Z"/>',
  package: '<path d="m12 3 8 4-8 4-8-4Z"/><path d="m4 7 8 4 8-4v10l-8 4-8-4ZM12 11v10"/>',
  arrow: '<path d="M7 17 17 7M8 7h9v9"/>',
  generic: '<circle cx="12" cy="12" r="8"/><path d="M9 12h6M12 9v6"/>'
};

function iconKind(name) {
  if (/layout-dashboard/.test(name)) return "dashboard";
  if (/folder/.test(name)) return "folder";
  if (/github|git-|git$/.test(name)) return "git";
  if (/search|scan/.test(name)) return "search";
  if (/spark|wand|bot/.test(name)) return "sparkle";
  if (/activity|radar/.test(name)) return "activity";
  if (/history/.test(name)) return "clock";
  if (/compare|columns/.test(name)) return "compare";
  if (/file|code-2/.test(name)) return "file";
  if (/database|server/.test(name)) return "database";
  if (/network|route|blocks|boxes|milestone/.test(name)) return "network";
  if (/shield|test-tube/.test(name)) return "check";
  if (/rocket/.test(name)) return "rocket";
  if (/users/.test(name)) return "users";
  if (/menu|panel-left/.test(name)) return "menu";
  if (/bell/.test(name)) return "bell";
  if (/play/.test(name)) return "play";
  if (/trash/.test(name)) return "trash";
  if (/refresh/.test(name)) return "refresh";
  if (/share/.test(name)) return "share";
  if (/link/.test(name)) return "link";
  if (/message/.test(name)) return "message";
  if (/laptop|hard-drive/.test(name)) return "device";
  if (/bookmark/.test(name)) return "bookmark";
  if (/package/.test(name)) return "package";
  if (/arrow/.test(name)) return "arrow";
  return "generic";
}

function refreshIcons() {
  if (window.lucide?.createIcons) {
    window.lucide.createIcons({ attrs: { "aria-hidden": "true" } });
    return;
  }

  document.querySelectorAll("i[data-lucide]").forEach((node) => {
    const name = node.dataset.lucide || "generic";
    const kind = iconKind(name);
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "1.8");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    svg.setAttribute("aria-hidden", "true");
    svg.innerHTML = FALLBACK_ICON_PATHS[kind] || FALLBACK_ICON_PATHS.generic;
    node.replaceWith(svg);
  });
}

function setPageTitle(pageName) {
  const title = PAGE_TITLES[pageName] || "CodeGraph AI";
  const titleNode = document.getElementById("currentPageTitle");
  if (titleNode) titleNode.textContent = title;
  document.title = `${title} · CodeGraph AI`;
}

function closeMobileSidebar() {
  document.body.classList.remove("sidebar-open");
}

function showAllRevealContent() {
  document.querySelectorAll(".reveal").forEach((node) => {
    node.classList.remove("reveal-pending");
    node.classList.add("is-visible");
  });
}

function revealCurrentPage() {
  const activePage = document.querySelector(".page.active");
  if (!activePage) return;

  activePage.querySelectorAll(".reveal").forEach((node, index) => {
    node.classList.add("reveal-pending");
    node.classList.remove("is-visible");
    window.setTimeout(() => node.classList.add("is-visible"), Math.min(index * 65, 320));
  });
}

function openPage(pageName) {
  const pages = document.querySelectorAll(".page");
  const links = document.querySelectorAll("[data-page-link]");

  pages.forEach((page) => {
    page.classList.toggle("active", page.dataset.page === pageName);
  });

  links.forEach((link) => {
    link.classList.toggle("active", link.dataset.pageLink === pageName);
  });

  localStorage.setItem("codegraph-active-page", pageName);
  setPageTitle(pageName);
  closeMobileSidebar();
  window.scrollTo({ top: 0, behavior: "smooth" });

  window.requestAnimationFrame(() => {
    revealCurrentPage();
    refreshIcons();
  });
}

function setupNavigation() {
  document.querySelectorAll("[data-page-link]").forEach((button) => {
    button.addEventListener("click", () => openPage(button.dataset.pageLink));
  });

  document.querySelectorAll("[data-open-page]").forEach((button) => {
    button.addEventListener("click", () => openPage(button.dataset.openPage));
  });

  const savedPage = localStorage.getItem("codegraph-active-page");
  const initialPage = savedPage && document.querySelector(`.page[data-page="${savedPage}"]`)
    ? savedPage
    : "overview";

  openPage(initialPage);
}

function setupSidebar() {
  const collapseButton = document.getElementById("sidebarCollapse");
  const mobileMenu = document.getElementById("mobileMenu");
  const mobileBackdrop = document.getElementById("mobileBackdrop");
  const collapsed = localStorage.getItem("codegraph-sidebar-collapsed") === "true";

  document.body.classList.toggle("sidebar-collapsed", collapsed);

  collapseButton?.addEventListener("click", () => {
    const nextCollapsed = !document.body.classList.contains("sidebar-collapsed");
    document.body.classList.toggle("sidebar-collapsed", nextCollapsed);
    localStorage.setItem("codegraph-sidebar-collapsed", String(nextCollapsed));
  });

  mobileMenu?.addEventListener("click", () => document.body.classList.add("sidebar-open"));
  mobileBackdrop?.addEventListener("click", closeMobileSidebar);
}

function setupKeyboardShortcuts() {
  const focusPrompt = () => {
    const prompt = document.getElementById("question");
    prompt?.focus();
    prompt?.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  document.getElementById("focusPromptButton")?.addEventListener("click", focusPrompt);

  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      focusPrompt();
    }
    if (event.key === "Escape") closeMobileSidebar();
  });
}

function formatActivityName(value) {
  return String(value || "analysis")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function renderDashboardHistory(items) {
  const root = document.getElementById("dashboardRecentActivity");
  if (!root) return;

  if (!Array.isArray(items) || !items.length) {
    root.innerHTML = `
      <div class="dashboard-empty">
        <i data-lucide="history"></i>
        <span>No recent analysis yet. Start by analyzing a local or GitHub repository.</span>
      </div>
    `;
    refreshIcons();
    return;
  }

  root.innerHTML = "";
  items.slice(0, 5).forEach((item) => {
    const row = document.createElement("div");
    row.className = "dashboard-activity-item";

    const icon = document.createElement("div");
    icon.className = "activity-icon";
    icon.innerHTML = '<i data-lucide="activity"></i>';

    const copy = document.createElement("div");
    copy.className = "activity-copy";

    const title = document.createElement("strong");
    title.textContent = item.label || formatActivityName(item.event_type);

    const meta = document.createElement("small");
    meta.textContent = `${formatActivityName(item.event_type)} · ${item.timestamp || "Recent"}`;

    copy.append(title, meta);
    row.append(icon, copy);
    root.appendChild(row);
  });

  refreshIcons();
}

async function fetchJsonWithTimeout(url, timeoutMs = 2500) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: { Accept: "application/json" }
    });
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

async function loadDashboardMetrics() {
  const repoCount = document.getElementById("dashboardRepoCount");
  const historyCount = document.getElementById("dashboardHistoryCount");
  const watchCount = document.getElementById("dashboardWatchCount");

  if (repoCount) repoCount.textContent = "0";
  if (historyCount) historyCount.textContent = "0";
  if (watchCount) watchCount.textContent = "0";
  renderDashboardHistory([]);

  const results = await Promise.allSettled([
    fetchJsonWithTimeout("/repos"),
    fetchJsonWithTimeout("/history"),
    fetchJsonWithTimeout("/watch/list")
  ]);

  const reposData = results[0].status === "fulfilled" ? results[0].value : null;
  const historyData = results[1].status === "fulfilled" ? results[1].value : null;
  const watchData = results[2].status === "fulfilled" ? results[2].value : null;

  const repos = Array.isArray(reposData?.repos) ? reposData.repos : [];
  const history = Array.isArray(historyData?.history) ? historyData.history : [];
  const watches = Array.isArray(watchData?.watches) ? watchData.watches : [];

  if (repoCount) repoCount.textContent = String(repos.length);
  if (historyCount) historyCount.textContent = String(history.length);
  if (watchCount) watchCount.textContent = String(watches.length);
  renderDashboardHistory(history);
}

function shouldRouteToWorkspace(node) {
  if (!node) return false;
  const text = (node.textContent || "").trim().toLowerCase();
  if (!text) return false;

  const placeholders = [
    "run any analysis",
    "no analysis selected",
    "no repository loaded",
    "no file selected",
    "load files from",
    "select a file",
    "loading"
  ];

  return !placeholders.some((placeholder) => text.includes(placeholder));
}

function setupWorkspaceRouting() {
  [document.getElementById("renderedOutput"), document.getElementById("fileViewer")].forEach((node) => {
    if (!node) return;

    const observer = new MutationObserver(() => {
      if (shouldRouteToWorkspace(node)) openPage("workspace");
      refreshIcons();
    });

    observer.observe(node, { childList: true, subtree: true, characterData: true });
  });
}

function setupRevealObserver() {
  const nodes = [...document.querySelectorAll(".reveal")];
  if (!("IntersectionObserver" in window)) {
    showAllRevealContent();
    return;
  }

  nodes.forEach((node) => node.classList.add("reveal-pending"));

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.06, rootMargin: "0px 0px -20px" }
  );

  nodes.forEach((node) => observer.observe(node));
  window.setTimeout(showAllRevealContent, 1400);
}

function initializeCodeGraphUI() {
  try {
    if (localStorage.getItem("codegraph-ui-release") !== UI_RELEASE) {
      localStorage.setItem("codegraph-ui-release", UI_RELEASE);
      localStorage.removeItem("codegraph-active-page");
    }
  } catch (error) {
    console.warn("Local UI preferences are unavailable", error);
  }

  try { refreshIcons(); } catch (error) { console.warn("Icon setup skipped", error); }
  try { setupNavigation(); } catch (error) { console.error("Navigation setup failed", error); }
  try { setupSidebar(); } catch (error) { console.error("Sidebar setup failed", error); }
  try { setupKeyboardShortcuts(); } catch (error) { console.error("Shortcut setup failed", error); }
  try { setupWorkspaceRouting(); } catch (error) { console.error("Workspace routing setup failed", error); }
  try { setupRevealObserver(); } catch (error) { console.error("Reveal setup failed", error); showAllRevealContent(); }

  loadDashboardMetrics().catch((error) => {
    console.warn("Dashboard metrics unavailable", error);
    renderDashboardHistory([]);
  });
}

window.codeGraphRefreshIcons = refreshIcons;
window.addEventListener("error", () => showAllRevealContent());
window.addEventListener("unhandledrejection", () => showAllRevealContent());

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeCodeGraphUI, { once: true });
} else {
  initializeCodeGraphUI();
}

