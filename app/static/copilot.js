function renderCopilotResponse(data) {
  const root = clearOutput();
  const copilot = data.copilot_answer || {};

  root.appendChild(renderSummaryCard("Engineering Copilot", copilot.repo_name || data.repo_url || "Repository"));

  appendIfNode(root, renderMetadata(copilot.metadata));

  if (copilot.question) {
    root.appendChild(renderSummaryCard("Question", copilot.question));
  }

  if (copilot.answer) {
    root.appendChild(renderSummaryCard("Copilot Answer", copilot.answer));
  }

  appendIfNode(root, renderFileList(copilot.relevant_files || []));

  if (copilot.contexts?.length) {
    appendIfNode(root, renderContexts(copilot.contexts));
  }

  if (data.local_repo_path) {
    root.appendChild(renderSummaryCard("Local Cache Path", data.local_repo_path));
  }
}

const __originalRenderResponseCopilot = window.renderResponse;

window.renderResponse = function(data) {
  if (data && data.copilot_answer) {
    renderCopilotResponse(data);
    return;
  }
  __originalRenderResponseCopilot(data);
};

async function askCopilotLocal() {
  const repoPath = getRepoPath();
  const question = getQuestion();

  if (!repoPath) {
    renderError({ error: true, detail: "Enter a local repo path first." });
    return;
  }

  if (!question) {
    renderError({ error: true, detail: "Enter a question first." });
    return;
  }

  await postData("/copilot/ask", {
    repo_path: repoPath,
    question: question
  });
}

async function askCopilotGithub() {
  const repoUrl = getRepoUrl();
  const question = getQuestion();

  if (!repoUrl) {
    renderError({ error: true, detail: "Enter or select a GitHub repo first." });
    return;
  }

  if (!question) {
    renderError({ error: true, detail: "Enter a question first." });
    return;
  }

  const data = await postData("/github/copilot/ask", {
    repo_url: repoUrl,
    question: question
  });

  if (data && data.local_repo_path) {
    await loadFileTree(data.local_repo_path);
    await loadSavedRepos();
  }
}
