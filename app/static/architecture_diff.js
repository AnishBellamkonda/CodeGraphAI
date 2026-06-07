function renderArchitectureDiffResponse(data) {
  const root = clearOutput();
  const diff = data.architecture_diff || {};

  root.appendChild(
    renderSummaryCard(
      "Architecture Diff",
      `${diff.repo_a?.label || "Repo A"} vs ${diff.repo_b?.label || "Repo B"}`
    )
  );

  appendIfNode(root, renderMetadata({
    repo_a_path: diff.repo_a?.repo_path,
    repo_b_path: diff.repo_b?.repo_path,
    repo_a_total_scanned_files: diff.repo_a?.total_scanned_files,
    repo_b_total_scanned_files: diff.repo_b?.total_scanned_files
  }));

  if (diff.module_diff) {
    root.appendChild(
      renderSummaryCard(
        "Unique Modules In Repo A",
        (diff.module_diff.only_in_a || []).join("\n") || "None"
      )
    );
    root.appendChild(
      renderSummaryCard(
        "Unique Modules In Repo B",
        (diff.module_diff.only_in_b || []).join("\n") || "None"
      )
    );

    if (diff.module_diff.shared_modules_with_size_delta?.length) {
      const block = el("div", "block");
      block.appendChild(el("div", "block-title", "Shared Modules With Size Delta"));

      diff.module_diff.shared_modules_with_size_delta.forEach((item) => {
        const card = el("div", "context-card");

        const header = el("div", "context-header");
        header.appendChild(el("div", "", item.module || "module"));
        header.appendChild(el("div", "", `Δ ${item.delta}`));

        const body = el(
          "div",
          "context-text",
          [
            `Files in Repo A: ${item.files_in_a}`,
            `Files in Repo B: ${item.files_in_b}`
          ].join("\n")
        );

        card.appendChild(header);
        card.appendChild(body);
        block.appendChild(card);
      });

      root.appendChild(block);
    }
  }

  const sections = diff.section_diffs || {};
  Object.entries(sections).forEach(([key, value]) => {
    root.appendChild(
      renderSummaryCard(
        `${key} — Only In Repo A`,
        (value.only_in_a || []).join("\n") || "None"
      )
    );
    root.appendChild(
      renderSummaryCard(
        `${key} — Only In Repo B`,
        (value.only_in_b || []).join("\n") || "None"
      )
    );
  });

  if (diff.summary_notes?.length) {
    root.appendChild(renderSummaryCard("Summary Notes", diff.summary_notes.join("\n")));
  }
}

const __originalRenderResponseArchDiff = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.architecture_diff) {
    renderArchitectureDiffResponse(data);
    return;
  }
  __originalRenderResponseArchDiff(data);
};

async function diffLocalArchitectures() {
  const repoPathA = getCompareRepoPathA();
  const repoPathB = getCompareRepoPathB();

  if (!repoPathA || !repoPathB) {
    renderError({ error: true, detail: "Enter both local repo paths first." });
    return;
  }

  await postData("/architecture/diff", {
    repo_path_a: repoPathA,
    repo_path_b: repoPathB
  });
}

async function diffGithubArchitectures() {
  const repoUrlA = getCompareRepoUrlA();
  const repoUrlB = getCompareRepoUrlB();

  if (!repoUrlA || !repoUrlB) {
    renderError({ error: true, detail: "Enter both GitHub repo URLs first." });
    return;
  }

  const data = await postData("/github/architecture/diff", {
    repo_url_a: repoUrlA,
    repo_url_b: repoUrlB
  });

  if (data && data.local_repo_a) {
    await loadFileTree(data.local_repo_a);
    await loadSavedRepos();
  }
}
