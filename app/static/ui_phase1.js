window.addEventListener("DOMContentLoaded", () => {
  const animated = document.querySelectorAll(".hero-panel, .surface, .workspace-panel");
  animated.forEach((node, index) => {
    node.style.setProperty("--delay", `${index * 45}ms`);
  });

  const actionButtons = document.querySelectorAll("button");
  actionButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const output = document.getElementById("renderedOutput");
      if (!output) return;

      setTimeout(() => {
        output.scrollIntoView({
          behavior: "smooth",
          block: "start"
        });
      }, 120);
    });
  });
});
