const headingIcons = {
  "Ask / Search Input": "⌕",
  "Local Repository": "💻",
  "GitHub Repository": "🌐",
  "Compare Two Repos": "⇄",
  "Watch Mode": "🔔",
  "History": "🕘",
  "Results Workspace": "📊",
  "File Tree": "🗂",
  "Code Viewer": "🧾"
};

const navIcons = {
  "Local": "💻",
  "GitHub": "🌐",
  "Compare": "⇄",
  "Watch": "🔔",
  "History": "🕘",
  "Results": "📊",
  "Files": "🗂",
  "Viewer": "🧾"
};

const buttonIcons = {
  "Analyze": "🔎",
  "Summarize": "✨",
  "Index": "🧠",
  "Ask Local": "💬",
  "Ask GitHub": "💬",
  "Copilot Local": "🤖",
  "Copilot GitHub": "🤖",
  "Load Files": "🗂",
  "Architecture": "🧭",
  "Onboarding": "🪜",
  "Export Report": "📝",
  "Portfolio Share": "🌟",
  "Dependencies": "📦",
  "System Design": "🏗",
  "Test Heuristics": "🧪",
  "Deployment": "🚀",
  "Refresh Repo": "↻",
  "PR Dashboard": "🔀",
  "Analyze PR": "🧾",
  "Release Health": "🛡",
  "Issue Dashboard": "🐞",
  "Ownership Map": "👥",
  "Compare Local": "⇄",
  "Compare GitHub": "⇄",
  "Architecture Diff": "🧬",
  "Create Local Watch": "🔔",
  "Create GitHub Watch": "🔔",
  "Check Watches": "✅",
  "Reload Watches": "↻",
  "Clear All Watches": "🧹",
  "Reload History": "↻",
  "Team Dashboard": "🏢",
  "Clear History": "🧹",
  "Use": "➜",
  "Collapse": "–",
  "Expand": "+"
};

function addIconPrefix(el, icon, className, iconClassName) {
  if (!el || !icon) return;
  if (el.dataset.iconApplied === "true") return;

  const wrapper = document.createElement("span");
  wrapper.className = className;

  const iconNode = document.createElement("span");
  iconNode.className = iconClassName;
  iconNode.textContent = icon;

  const content = document.createElement("span");
  content.textContent = el.textContent;

  wrapper.appendChild(iconNode);
  wrapper.appendChild(content);

  el.textContent = "";
  el.appendChild(wrapper);
  el.dataset.iconApplied = "true";
}

function decorateHeadings(root = document) {
  root.querySelectorAll(".surface h2, .workspace-panel h2").forEach((el) => {
    const text = el.textContent.trim();
    addIconPrefix(el, headingIcons[text], "title-with-icon", "title-icon");
  });
}

function decorateNav(root = document) {
  root.querySelectorAll(".nav-chip").forEach((el) => {
    const text = el.textContent.trim();
    addIconPrefix(el, navIcons[text], "nav-chip-with-icon", "nav-chip-icon");
  });
}

function decorateButtons(root = document) {
  root.querySelectorAll("button").forEach((el) => {
    const text = el.textContent.trim();
    addIconPrefix(el, buttonIcons[text], "btn-with-icon", "btn-icon");
  });
}

function scoreTone(value) {
  const num = Number(value);
  if (Number.isNaN(num)) return "info";
  if (num >= 80) return "success";
  if (num >= 50) return "warn";
  return "danger";
}

function chipForValue(title, rawValue) {
  const value = (rawValue || "").trim();
  if (!value) return null;
  if (value.includes("{") || value.includes("[") || value.includes("\n")) return null;
  if (value.length > 60) return null;

  const lowerTitle = title.toLowerCase();
  const lowerValue = value.toLowerCase();

  let tone = "info";
  let shouldChip = false;

  if (lowerTitle.includes("score")) {
    tone = scoreTone(value);
    shouldChip = true;
  } else if (lowerTitle.includes("coverage")) {
    const num = parseFloat(value);
    tone = Number.isNaN(num) ? "info" : scoreTone(num);
    shouldChip = true;
  } else if (lowerTitle.includes("level")) {
    if (lowerValue.includes("strong")) tone = "success";
    else if (lowerValue.includes("moderate")) tone = "warn";
    else if (lowerValue.includes("weak")) tone = "danger";
    shouldChip = true;
  } else if (lowerTitle.includes("status")) {
    if (["ok", "healthy", "indexed"].some(x => lowerValue.includes(x))) tone = "success";
    else if (["error", "failed", "alert"].some(x => lowerValue.includes(x))) tone = "danger";
    else tone = "warn";
    shouldChip = true;
  } else if (
    lowerTitle.includes("alerts") ||
    lowerTitle.includes("warning") ||
    lowerTitle.includes("risky") ||
    lowerTitle.includes("stale")
  ) {
    tone = "warn";
    shouldChip = true;
  }

  if (!shouldChip) return null;

  const chip = document.createElement("span");
  chip.className = `status-chip ${tone}`;
  chip.textContent = value;
  return chip;
}

function decorateMetadata(root = document) {
  root.querySelectorAll(".kv-card").forEach((card) => {
    const titleEl = card.querySelector(".kv-title");
    const valueEl = card.querySelector(".kv-value");
    if (!titleEl || !valueEl) return;
    if (valueEl.dataset.chipApplied === "true") return;

    const title = titleEl.textContent.trim();
    const raw = valueEl.textContent;
    const chip = chipForValue(title, raw);

    if (chip) {
      valueEl.textContent = "";
      valueEl.appendChild(chip);
      valueEl.dataset.chipApplied = "true";
    }

    const lowerTitle = title.toLowerCase();
    const text = raw.trim();
    if (lowerTitle.includes("score") || lowerTitle.includes("coverage")) {
      const num = parseFloat(text);
      if (!Number.isNaN(num)) {
        card.classList.remove("score-strong", "score-mid", "score-weak");
        if (num >= 80) card.classList.add("score-strong");
        else if (num >= 50) card.classList.add("score-mid");
        else card.classList.add("score-weak");
      }
    }
  });
}

function iconForBlockTitle(title) {
  const value = title.toLowerCase();
  if (value.includes("architecture")) return { icon: "🧭", tone: "info" };
  if (value.includes("deployment")) return { icon: "🚀", tone: "warn" };
  if (value.includes("test")) return { icon: "🧪", tone: "success" };
  if (value.includes("issue")) return { icon: "🐞", tone: "warn" };
  if (value.includes("contributor") || value.includes("ownership")) return { icon: "👥", tone: "info" };
  if (value.includes("report") || value.includes("portfolio")) return { icon: "📝", tone: "success" };
  if (value.includes("error") || value.includes("risk") || value.includes("alert")) return { icon: "⚠", tone: "danger" };
  if (value.includes("history")) return { icon: "🕘", tone: "info" };
  if (value.includes("summary")) return { icon: "✨", tone: "success" };
  if (value.includes("dependencies")) return { icon: "📦", tone: "info" };
  if (value.includes("copilot")) return { icon: "🤖", tone: "info" };
  if (value.includes("watch")) return { icon: "🔔", tone: "warn" };
  if (value.includes("file")) return { icon: "🗂", tone: "info" };
  return { icon: "•", tone: "info" };
}

function decorateBlocks(root = document) {
  root.querySelectorAll(".block").forEach((block) => {
    const titleEl = block.querySelector(".block-title");
    if (!titleEl) return;

    const text = titleEl.textContent.trim();
    const { icon, tone } = iconForBlockTitle(text);

    if (titleEl.dataset.iconApplied !== "true") {
      addIconPrefix(titleEl, icon, "block-title-with-icon", "block-title-icon");
    }

    block.classList.remove("tone-info", "tone-success", "tone-warn", "tone-danger");
    block.classList.add(`tone-${tone}`);
  });
}

function decorateStatusCards(root = document) {
  root.querySelectorAll(".context-card").forEach((card) => {
    const text = card.textContent.toLowerCase();
    card.classList.remove("status-alert", "status-ok");

    if (text.includes("status: alert") || text.includes("[high]") || text.includes("[medium]")) {
      card.classList.add("status-alert");
    } else if (text.includes("status: ok")) {
      card.classList.add("status-ok");
    }
  });
}

function applyPhase3(root = document) {
  decorateHeadings(root);
  decorateNav(root);
  decorateButtons(root);
  decorateMetadata(root);
  decorateBlocks(root);
  decorateStatusCards(root);
}

window.addEventListener("DOMContentLoaded", () => {
  applyPhase3(document);

  const observer = new MutationObserver(() => {
    applyPhase3(document);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
});
