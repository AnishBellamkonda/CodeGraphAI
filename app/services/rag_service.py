from __future__ import annotations

import os
import re
import hashlib
from pathlib import Path
from typing import Any

import chromadb
from dotenv import load_dotenv

from app.services.repo_scanner import IGNORE_DIRS, IGNORE_FILES

load_dotenv()

CHROMA_DIR = "./chroma_db"
COLLECTION_PREFIX = "codegraph_"


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts.intersection(IGNORE_DIRS):
        return True
    if path.name in IGNORE_FILES:
        return True
    return False


def is_text_file(path: Path) -> bool:
    allowed = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
        ".json", ".yaml", ".yml", ".md", ".sql", ".html", ".css", ".scss",
        ".sh", ".txt", ".xml"
    }
    return path.suffix.lower() in allowed or path.name in {
        "Dockerfile", "README.md", "requirements.txt", "pyproject.toml",
        "package.json", "pom.xml", "build.gradle", "go.mod"
    }


def read_file_content(path: Path, max_chars: int = 20000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except Exception:
        return ""


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    if not text.strip():
        return []

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        if end == length:
            break
        start = end - overlap

    return chunks


def repo_to_collection_name(repo_path: str) -> str:
    repo_name = Path(repo_path).name.lower()
    repo_name = re.sub(r"[^a-z0-9_-]", "-", repo_name)
    repo_name = re.sub(r"[-_]+", "-", repo_name).strip("-")

    if not repo_name:
        repo_name = "repo"

    digest = hashlib.md5(repo_path.encode("utf-8")).hexdigest()[:10]
    collection_name = f"{COLLECTION_PREFIX}{repo_name}-{digest}".lower()

    collection_name = re.sub(r"[^a-z0-9_-]", "-", collection_name)
    collection_name = re.sub(r"[-_]+", "-", collection_name).strip("-")

    if len(collection_name) > 63:
        collection_name = collection_name[:63].rstrip("-")

    if len(collection_name) < 3:
        collection_name = f"cg-{digest}"

    return collection_name


def get_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


def get_embedding_function():
    provider = os.getenv("AI_PROVIDER", "mock").lower()

    if provider == "openai":
        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing in .env")

        return OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-3-small",
        )

    return None


def collect_repo_documents(repo_path_str: str) -> list[dict[str, Any]]:
    repo_path = Path(repo_path_str).expanduser().resolve()

    if not repo_path.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")

    if not repo_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {repo_path}")

    docs: list[dict[str, Any]] = []

    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        if not is_text_file(path):
            continue

        relative_path = str(path.relative_to(repo_path))
        content = read_file_content(path)
        if not content.strip():
            continue

        chunks = chunk_text(content)
        for idx, chunk in enumerate(chunks):
            docs.append(
                {
                    "id": f"{relative_path}::chunk_{idx}",
                    "document": chunk,
                    "metadata": {
                        "file_path": relative_path,
                        "chunk_index": idx,
                    },
                }
            )

    return docs


def index_repository(repo_path: str) -> dict[str, Any]:
    docs = collect_repo_documents(repo_path)
    client = get_client()
    collection_name = repo_to_collection_name(repo_path)

    embedding_fn = get_embedding_function()

    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    if embedding_fn:
        collection = client.create_collection(name=collection_name, embedding_function=embedding_fn)
    else:
        collection = client.create_collection(name=collection_name)

    if not docs:
        return {
            "collection_name": collection_name,
            "files_indexed": 0,
            "chunks_indexed": 0,
        }

    ids = [doc["id"] for doc in docs]
    documents = [doc["document"] for doc in docs]
    metadatas = [doc["metadata"] for doc in docs]

    if embedding_fn:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
    else:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=[[0.0] * 8 for _ in docs],
        )

    unique_files = {doc["metadata"]["file_path"] for doc in docs}

    return {
        "collection_name": collection_name,
        "files_indexed": len(unique_files),
        "chunks_indexed": len(docs),
    }


def search_repository(repo_path: str, question: str, n_results: int = 5) -> list[dict[str, Any]]:
    client = get_client()
    collection_name = repo_to_collection_name(repo_path)
    embedding_fn = get_embedding_function()

    if embedding_fn:
        collection = client.get_collection(name=collection_name, embedding_function=embedding_fn)
        results = collection.query(query_texts=[question], n_results=n_results)
    else:
        collection = client.get_collection(name=collection_name)
        all_docs = collection.get()
        matches = []

        query_words = set(question.lower().split())
        for doc, meta in zip(all_docs.get("documents", []), all_docs.get("metadatas", [])):
            score = sum(1 for word in query_words if word in doc.lower())
            if score > 0:
                matches.append((score, doc, meta))

        matches.sort(key=lambda x: x[0], reverse=True)
        top = matches[:n_results]

        return [
            {
                "file_path": meta["file_path"],
                "chunk_index": meta["chunk_index"],
                "content": doc,
            }
            for _, doc, meta in top
        ]

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    output = []
    for doc, meta in zip(documents, metadatas):
        output.append(
            {
                "file_path": meta["file_path"],
                "chunk_index": meta["chunk_index"],
                "content": doc,
            }
        )

    return output
