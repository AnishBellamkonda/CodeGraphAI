window.addEventListener("DOMContentLoaded", () => {
  const chips = document.querySelectorAll("[data-jump-target]");
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const targetId = chip.getAttribute("data-jump-target");
      const target = document.getElementById(targetId);
      if (!target) return;

      target.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });

      target.classList.add("focus-flash");
      setTimeout(() => target.classList.remove("focus-flash"), 700);
    });
  });

  const collapsibles = document.querySelectorAll("[data-collapsible]");
  collapsibles.forEach((section) => {
    const button = section.querySelector(".section-toggle");
    if (!button) return;

    button.addEventListener("click", () => {
      const isCollapsed = section.classList.toggle("is-collapsed");
      button.textContent = isCollapsed ? "Expand" : "Collapse";
    });
  });
});

const phase2Style = document.createElement("style");
phase2Style.textContent = `
.focus-flash {
  box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.35), 0 0 0 8px rgba(96, 165, 250, 0.08), var(--shadow);
  transition: box-shadow 220ms ease;
}
`;
document.head.appendChild(phase2Style);
