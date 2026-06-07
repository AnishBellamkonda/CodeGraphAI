from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

from app.services.architecture_map import build_architecture_map
from app.services.onboarding_assistant import build_onboarding_guide
from app.services.rag_service import index_repository, search_repository
from app.services.repo_scanner import scan_repository

load_dotenv()


def _openai_chat(prompt: str) -> str:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing in .env")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a senior software engineer acting as an engineering copilot."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or "No response generated."


def _gemini_chat(prompt: str) -> str:
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing in .env")

    genai.configure(api_key=api_key)
    llm = genai.GenerativeModel(model)
    response = llm.generate_content(prompt)

    if hasattr(response, "text") and response.text:
        return response.text

    return "No response generated."


def _build_copilot_prompt(
    question: str,
    scan_result: dict[str, Any],
    architecture_map: dict[str, Any],
    onboarding_guide: dict[str, Any],
    contexts: list[dict[str, Any]],
) -> str:
    top_modules = ", ".join(
        f"{item['module']} ({item['files']})"
        for item in architecture_map.get("top_modules", [])[:8]
    ) or "None"

    context_text = "\n\n".join(
        f"FILE: {item['file_path']}\nCHUNK: {item['chunk_index']}\nCONTENT:\n{item['content']}"
        for item in contexts[:8]
    ) or "No retrieved context found."

    return f"""
You are a senior software engineer acting as an engineering copilot for a codebase.

Question:
{question}

Repository:
- Name: {scan_result.get("repo_name")}
- Total files: {scan_result.get("total_files")}
- Languages: {scan_result.get("languages")}
- Frameworks: {scan_result.get("frameworks")}

Architecture Signals:
- Top modules: {top_modules}
- Entry points: {architecture_map.get("entry_points")}
- API routes: {architecture_map.get("api_routes")}
- Services: {architecture_map.get("services")}
- Data models: {architecture_map.get("data_models")}
- Data access: {architecture_map.get("data_access")}
- Frontend: {architecture_map.get("frontend")}
- Config/Infra: {architecture_map.get("config_infra")}
- Tests: {architecture_map.get("tests")}
- Likely request flow: {architecture_map.get("likely_request_flow")}

Onboarding Guide:
- First files to read: {onboarding_guide.get("first_files_to_read")}
- Learning path: {onboarding_guide.get("learning_path")}
- Focus areas: {onboarding_guide.get("focus_areas")}
- Likely workflows: {onboarding_guide.get("likely_workflows")}

Retrieved code context:
{context_text}

Instructions:
- Answer the engineering question directly.
- Ground your answer in the provided repo structure and retrieved code context.
- Mention the most relevant files.
- If context is incomplete, say that clearly.
- Keep it practical and implementation-oriented.

Return exactly these sections:

1. Direct Answer
2. Why
3. Relevant Files
4. Suggested Next Steps
5. Confidence / Gaps
""".strip()


def _mock_copilot_answer(
    question: str,
    architecture_map: dict[str, Any],
    onboarding_guide: dict[str, Any],
    contexts: list[dict[str, Any]],
) -> str:
    relevant_files = []
    relevant_files.extend(item["file_path"] for item in contexts[:6] if item.get("file_path"))
    if not relevant_files:
        relevant_files.extend(onboarding_guide.get("first_files_to_read", [])[:6])

    relevant_files = list(dict.fromkeys(relevant_files))[:8]

    flows = onboarding_guide.get("likely_workflows", [])
    focus = onboarding_guide.get("focus_areas", [])

    return f"""
1. Direct Answer
This is a grounded mock copilot response for the question: "{question}". Based on the repo structure and retrieved context, the most likely implementation path is through the relevant files and workflows listed below.

2. Why
The answer is based on a combination of architecture signals, onboarding hints, and retrieved code chunks. The repo appears to be organized around the detected modules and flows below:
{chr(10).join(f"- {item}" for item in (flows[:4] or focus[:4] or ['No strong workflow detected']))}

3. Relevant Files
{chr(10).join(f"- {item}" for item in relevant_files) if relevant_files else "- No strong file matches were found."}

4. Suggested Next Steps
- Start with the files listed above
- Trace from entry points or routes into the service layer
- Verify supporting config and test files around the same workflow
- Use Architecture Map and Onboarding Guide together to narrow down the implementation area

5. Confidence / Gaps
This response uses mock-mode reasoning. The repo analysis and retrieval are real, but the final AI explanation is heuristic unless OpenAI or Gemini is enabled.
""".strip()


def ask_engineering_copilot(repo_path: str, question: str) -> dict[str, Any]:
    scan_result = scan_repository(repo_path)
    architecture_map = build_architecture_map(repo_path)
    onboarding_guide = build_onboarding_guide(repo_path)

    # Ensure the repo is indexed before retrieval
    index_repository(repo_path)
    contexts = search_repository(repo_path, question, n_results=6)

    provider = os.getenv("AI_PROVIDER", "mock").lower()

    if provider == "mock":
        answer = _mock_copilot_answer(question, architecture_map, onboarding_guide, contexts)
    elif provider == "openai":
        prompt = _build_copilot_prompt(question, scan_result, architecture_map, onboarding_guide, contexts)
        answer = _openai_chat(prompt)
    elif provider == "gemini":
        prompt = _build_copilot_prompt(question, scan_result, architecture_map, onboarding_guide, contexts)
        answer = _gemini_chat(prompt)
    else:
        raise ValueError("Unsupported AI_PROVIDER. Use mock, openai, or gemini.")

    return {
        "repo_name": scan_result["repo_name"],
        "repo_path": scan_result["repo_path"],
        "question": question,
        "answer": answer,
        "relevant_files": [item["file_path"] for item in contexts[:8] if item.get("file_path")],
        "contexts": contexts,
        "metadata": {
            "languages": scan_result.get("languages", {}),
            "frameworks": scan_result.get("frameworks", []),
            "top_modules": architecture_map.get("top_modules", []),
        },
    }
