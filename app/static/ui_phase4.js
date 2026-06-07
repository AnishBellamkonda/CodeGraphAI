function phase4Text(el) {
  return (el?.textContent || "").trim();
}

function createRibbonCard(label, value) {
  const card = document.createElement("div");
  card.className = "result-ribbon-card";

  const labelEl = document.createElement("div");
  labelEl.className = "result-ribbon-label";
  labelEl.textContent = label;

  const valueEl = document.createElement("div");
  valueEl.className = "result-ribbon-value";
  valueEl.textContent = value;

  card.appendChild(labelEl);
  card.appendChild(valueEl);
  return card;
}

function buildResultRibbon(root) {
  if (!root || root.querySelector(".result-ribbon")) return;

  const kvCards = Array.from(root.querySelectorAll(":scope > .block .kv-card")).slice(0, 6);
  if (!kvCards.length) return;

  const ribbon = document.createElement("div");
  ribbon.className = "result-ribbon";

  kvCards.forEach((card) => {
    const title = phase4Text(card.querySelector(".kv-title"));
    const valueNode = card.querySelector(".kv-value");
    const value = phase4Text(valueNode);
    if (!title || !value) return;
    ribbon.appendChild(createRibbonCard(title, value));
  });

  if (ribbon.children.length) {
    root.insertBefore(ribbon, root.firstChild);
  }
}

function markHeroBlocks(root) {
  const blocks = Array.from(root.querySelectorAll(":scope > .block"));
  if (!blocks.length) return;

  const first = blocks[0];
  const title = phase4Text(first.querySelector(".block-title")).toLowerCase();

  if (
    title.includes("repository") ||
    title.includes("architecture diff") ||
    title.includes("engineering copilot") ||
    title.includes("team dashboard") ||
    title.includes("portfolio") ||
    title.includes("system design")
  ) {
    first.classList.add("large-hero");
  }
}

function groupPairsByTitle(root) {
  const blocks = Array.from(root.querySelectorAll(":scope > .block"));
  if (blocks.length < 2) return;

  for (let i = 0; i < blocks.length - 1; i++) {
    const a = blocks[i];
    const b = blocks[i + 1];

    if (a.parentElement?.classList.contains("paired-blocks")) continue;
    if (b.parentElement?.classList.contains("paired-blocks")) continue;

    const titleA = phase4Text(a.querySelector(".block-title"));
    const titleB = phase4Text(b.querySelector(".block-title"));

    const pairable =
      (
        titleA.includes("Only In Repo A") &&
        titleB.includes("Only In Repo B") &&
        titleA.replace("Only In Repo A", "").trim() === titleB.replace("Only In Repo B", "").trim()
      ) ||
      (
        titleA.includes("Unique Modules In Repo A") &&
        titleB.includes("Unique Modules In Repo B")
      ) ||
      (
        titleA.includes("Frameworks Only In Repo A") &&
        titleB.includes("Frameworks Only In Repo B")
      ) ||
      (
        titleA.includes("Languages Only In Repo A") &&
        titleB.includes("Languages Only In Repo B")
      );

    if (!pairable) continue;

    const wrapper = document.createElement("div");
    wrapper.className = "paired-blocks";

    a.classList.add("compact-block", "compare-pair-left");
    b.classList.add("compact-block", "compare-pair-right");

    a.parentNode.insertBefore(wrapper, a);
    wrapper.appendChild(a);
    wrapper.appendChild(b);
    i++;
  }
}

function groupCards(root) {
  const cardBlocks = Array.from(root.querySelectorAll(":scope > .block")).filter((block) => {
    const count = block.querySelectorAll(".context-card").length;
    return count >= 3;
  });

  cardBlocks.forEach((block) => {
    if (block.querySelector(".stacked-grid")) return;

    const cards = Array.from(block.querySelectorAll(":scope > .context-card"));
    if (!cards.length) return;

    const grid = document.createElement("div");
    grid.className = "stacked-grid";

    cards.forEach((card) => grid.appendChild(card));
    block.appendChild(grid);
  });
}

function addMiniBadges(root) {
  const heroBlocks = root.querySelectorAll(":scope > .block.large-hero, :scope > .block.metric-block");
  heroBlocks.forEach((block) => {
    if (block.querySelector(".result-mini-badges")) return;

    const summaryText = phase4Text(block.querySelector(".summary-text"));
    const badges = [];

    const scoreMatch = summaryText.match(/(\d+(?:\.\d+)?)\s*%/);
    if (scoreMatch) badges.push({ tone: "info", text: `${scoreMatch[1]}%` });

    if (/strong/i.test(summaryText)) badges.push({ tone: "success", text: "Strong" });
    if (/moderate/i.test(summaryText)) badges.push({ tone: "warn", text: "Moderate" });
    if (/weak/i.test(summaryText)) badges.push({ tone: "danger", text: "Weak" });
    if (/alert/i.test(summaryText)) badges.push({ tone: "danger", text: "Alert" });

    if (!badges.length) return;

    const wrap = document.createElement("div");
    wrap.className = "result-mini-badges";

    badges.slice(0, 4).forEach((item) => {
      const chip = document.createElement("span");
      chip.className = `status-chip ${item.tone}`;
      chip.textContent = item.text;
      wrap.appendChild(chip);
    });

    block.appendChild(wrap);
  });
}

function insertDividers(root) {
  if (root.querySelector(".result-divider")) return;

  const directChildren = Array.from(root.children).filter((node) => {
    return node.classList?.contains("block") || node.classList?.contains("paired-blocks");
  });

  for (let i = 1; i < directChildren.length; i += 3) {
    const divider = document.createElement("hr");
    divider.className = "result-divider";
    root.insertBefore(divider, directChildren[i]);
  }
}

function enhanceResultsLayout() {
  const root = document.getElementById("renderedOutput");
  if (!root) return;

  root.classList.add("enhanced-layout");

  const hasContent =
    root.querySelector(".block") ||
    root.querySelector(".context-card") ||
    root.querySelector(".kv-card");

  if (!hasContent) return;

  buildResultRibbon(root);
  markHeroBlocks(root);
  groupPairsByTitle(root);
  groupCards(root);
  addMiniBadges(root);
  insertDividers(root);
}

window.addEventListener("DOMContentLoaded", () => {
  enhanceResultsLayout();

  const output = document.getElementById("renderedOutput");
  if (!output) return;

  const observer = new MutationObserver(() => {
    enhanceResultsLayout();
  });

  observer.observe(output, {
    childList: true,
    subtree: true
  });
});
