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
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function setupProductNavigation() {
  document.querySelectorAll("[data-page-link]").forEach((btn) => {
    btn.addEventListener("click", () => openPage(btn.dataset.pageLink));
  });

  document.querySelectorAll("[data-open-page]").forEach((btn) => {
    btn.addEventListener("click", () => openPage(btn.dataset.openPage));
  });

  const saved = localStorage.getItem("codegraph-active-page");
  if (saved && document.querySelector(`.page[data-page="${saved}"]`)) {
    openPage(saved);
  } else {
    openPage("overview");
  }
}

function autoRouteToWorkspace() {
  const renderedOutput = document.getElementById("renderedOutput");
  const fileTree = document.getElementById("fileTree");
  const fileViewer = document.getElementById("fileViewer");

  const shouldSwitch = (node) => {
    if (!node) return false;
    const text = (node.textContent || "").trim().toLowerCase();
    if (!text) return false;
    if (text.includes("run any analysis")) return false;
    if (text.includes("load a repository to browse files")) return false;
    if (text.includes("choose a file to preview")) return false;
    return true;
  };

  const maybeSwitch = (node) => {
    if (shouldSwitch(node)) {
      openPage("workspace");
    }
  };

  [renderedOutput, fileTree, fileViewer].forEach((node) => {
    if (!node) return;

    const observer = new MutationObserver(() => {
      maybeSwitch(node);
    });

    observer.observe(node, {
      childList: true,
      subtree: true,
      characterData: true
    });
  });
}

window.addEventListener("DOMContentLoaded", () => {
  setupProductNavigation();
  autoRouteToWorkspace();
});
