from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _build_prompt(scan_result: dict[str, Any]) -> str:
    important_sections = []

    for item in scan_result.get("important_files", [])[:10]:
        important_sections.append(
            f"FILE: {item['path']}\nCONTENT PREVIEW:\n{item['preview']}\n"
        )

    prompt = f"""
You are a senior software engineer helping explain a codebase to a new developer.

Analyze this repository and provide a clean structured summary.

Repository name: {scan_result.get("repo_name")}
Total files: {scan_result.get("total_files")}
Languages: {scan_result.get("languages")}
Frameworks: {scan_result.get("frameworks")}
Top level structure: {scan_result.get("top_level_structure")}

Important files:
{chr(10).join(important_sections)}

Return the answer in exactly this format:

1. Project Overview
2. Main Technologies
3. Likely Architecture
4. Important Modules or Files
5. How Data or Requests Probably Flow
6. Suggested Next Files to Read
7. Risks / Unknowns

Keep it grounded in the provided files.
Do not invent details if not visible.
""".strip()

    return prompt


def _build_qa_prompt(question: str, contexts: list[dict[str, Any]]) -> str:
    joined_context = "\n\n".join(
        [
            f"FILE: {item['file_path']}\nCHUNK: {item['chunk_index']}\nCONTENT:\n{item['content']}"
            for item in contexts
        ]
    )

    return f"""
You are an expert software engineer helping answer questions about a code repository.

Question:
{question}

Relevant code/context:
{joined_context}

Instructions:
- Answer only from the provided context.
- If the context is incomplete, say that clearly.
- Mention the relevant file paths.
- Keep the answer practical and grounded.

Return format:
1. Answer
2. Relevant Files
3. Confidence / Gaps
""".strip()


def _mock_summary(scan_result: dict[str, Any]) -> str:
    repo_name = scan_result.get("repo_name", "unknown-repo")
    languages = ", ".join(scan_result.get("languages", {}).keys()) or "Unknown"
    frameworks = ", ".join(scan_result.get("frameworks", [])) or "Unknown"

    important_files = "\n".join(
        f"- {item['path']}" for item in scan_result.get("important_files", [])[:8]
    )

    return f"""
1. Project Overview
This repository appears to be a project named {repo_name}. Based on the scanned files, it looks like a software application with source code, configuration files, and supporting project metadata.

2. Main Technologies
The main detected languages are: {languages}.
The likely frameworks or runtime ecosystem are: {frameworks}.

3. Likely Architecture
From the folder layout and file patterns, this project appears to follow a modular repository structure with application code, configuration, and dependency files separated across directories.

4. Important Modules or Files
{important_files if important_files else "- No major files detected yet."}

5. How Data or Requests Probably Flow
A likely flow is that entry-point files define routes, handlers, or startup logic, which then call service or utility layers and possibly interact with a database or external APIs.

6. Suggested Next Files to Read
Start with the README, dependency manifest files, entry-point application files, and main route or service files.

7. Risks / Unknowns
This summary is based only on file scanning and previews. Exact request flow, business logic, and runtime behavior still need deeper code analysis.
""".strip()


def _mock_answer(question: str, contexts: list[dict[str, Any]]) -> str:
    files = "\n".join(f"- {item['file_path']}" for item in contexts[:5]) or "- No matches found"

    return f"""
1. Answer
This is a mock answer for the question: "{question}". Based on the retrieved chunks, the likely implementation details are present in the files listed below. Once you switch to OpenAI or Gemini, this will return a real grounded answer.

2. Relevant Files
{files}

3. Confidence / Gaps
This answer is based on mock mode. Retrieval worked, but the final reasoning is placeholder text.
""".strip()


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
            {"role": "system", "content": "You are an expert software architect and code reviewer."},
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


def summarize_repository(scan_result: dict[str, Any]) -> str:
    provider = os.getenv("AI_PROVIDER", "mock").lower()
    prompt = _build_prompt(scan_result)

    if provider == "mock":
        return _mock_summary(scan_result)

    if provider == "openai":
        return _openai_chat(prompt)

    if provider == "gemini":
        return _gemini_chat(prompt)

    raise ValueError("Unsupported AI_PROVIDER. Use mock, openai, or gemini.")


def answer_repository_question(question: str, contexts: list[dict[str, Any]]) -> str:
    provider = os.getenv("AI_PROVIDER", "mock").lower()
    prompt = _build_qa_prompt(question, contexts)

    if provider == "mock":
        return _mock_answer(question, contexts)

    if provider == "openai":
        return _openai_chat(prompt)

    if provider == "gemini":
        return _gemini_chat(prompt)

    raise ValueError("Unsupported AI_PROVIDER. Use mock, openai, or gemini.")
