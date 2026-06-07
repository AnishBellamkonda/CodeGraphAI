# CodeGraph AI - Starter Backend

This is the first backend for **CodeGraph AI**, an AI-powered codebase understanding engine.

## What this version does
- Starts a FastAPI server
- Accepts a local repository path
- Scans text-based source files
- Ignores noisy folders like `node_modules`, `.git`, `dist`, `build`, and `venv`
- Returns:
  - detected languages
  - top-level folders/files
  - basic framework guesses
  - previews of important files

## Project structure
```text
backend/
  app/
    main.py
    repo_reader.py
  requirements.txt
  .env.example
  README.md
```

## Setup
### 1. Create and activate a virtual environment
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the API
```bash
uvicorn app.main:app --reload
```

The server will start on:
```text
http://127.0.0.1:8000
```

## Test it
Open the Swagger UI:
```text
http://127.0.0.1:8000/docs
```

Use the `/analyze` endpoint with a JSON body like:
```json
{
  "repo_path": "/absolute/path/to/your/repo"
}
```

Example:
```json
{
  "repo_path": "/Users/anish/Desktop/sample-project"
}
```

## What to build next
1. Add LLM summary generation
2. Add chunking + embeddings
3. Add ChromaDB for RAG
4. Add `/ask` endpoint for codebase Q&A
5. Add frontend UI in React
```
# CodeGraphAI
