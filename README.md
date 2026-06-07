# 🚀 CodeGraph AI

**AI-powered Repository Intelligence Platform**

CodeGraph AI helps developers, engineering teams, and technical leaders understand large codebases faster through AI-driven analysis, architecture insights, repository health checks, and interactive code exploration.

Instead of manually navigating thousands of files, CodeGraph AI transforms repositories into searchable, explainable, and actionable engineering knowledge.

---

## ✨ Features

### 🔍 Repository Analysis

* Analyze local repositories
* Analyze GitHub repositories
* Repository summarization
* Intelligent codebase indexing
* Repository structure exploration

### 🤖 AI Engineering Copilot

* Ask questions about your codebase
* Understand architecture and workflows
* Explain implementation details
* Discover entry points and dependencies
* Accelerate developer onboarding

### 🏗️ Architecture Intelligence

* Architecture mapping
* System design insights
* Dependency analysis
* Architecture comparison
* Engineering documentation generation

### 📊 Engineering Health & Quality

* Deployment readiness analysis
* Test coverage heuristics
* Dependency insights
* Repository health metrics
* Technical risk identification

### 🔄 Repository Comparison

* Compare local repositories
* Compare GitHub repositories
* Architecture diff analysis
* Structural change detection

### 🛠️ GitHub Intelligence

* Pull Request Dashboard
* Contributor Analysis
* Issue Dashboard
* Release Readiness Insights
* Repository Activity Tracking

### 👥 Team & Operations

* Watch Mode
* Team Dashboard
* Historical Analysis
* Portfolio Reports
* Repository Monitoring

---

## 🏛️ High-Level Architecture

```text
                    ┌───────────────────┐
                    │      Frontend     │
                    │  HTML / CSS / JS  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      FastAPI      │
                    │    Backend API    │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼

 ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
 │ Repo Parser │      │ GitHub APIs │      │ AI Services │
 └─────────────┘      └─────────────┘      └─────────────┘
        │                     │                     │
        └─────────────┬───────┴─────────────┬───────┘
                      ▼                     ▼

              ┌─────────────────────┐
              │   ChromaDB (RAG)    │
              │  Repository Memory  │
              └─────────────────────┘
```

---

## 🧰 Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn

### AI & Search

* ChromaDB
* Retrieval-Augmented Generation (RAG)

### Repository Intelligence

* GitHub REST APIs
* Repository Parsing
* Architecture Analysis

### Frontend

* HTML
* CSS
* JavaScript

### Storage

* ChromaDB
* Local Repository Metadata

---

## 📸 Core Workflows

### Local Repository Analysis

```text
Repository Path
      │
      ▼
Analyze Repository
      │
      ▼
Index + Summarize
      │
      ▼
Architecture Insights
      │
      ▼
AI Copilot Q&A
```

### GitHub Repository Analysis

```text
GitHub URL
      │
      ▼
Repository Fetch
      │
      ▼
Index Repository
      │
      ▼
PR / Issues / Contributors
      │
      ▼
Engineering Insights
```

---

## 🚀 Getting Started

### Clone Repository

```bash
git clone https://github.com/AnishBellamkonda/CodeGraphAI.git
cd CodeGraphAI
```

### Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python -m uvicorn app.main:app --reload
```

Application will be available at:

```text
http://127.0.0.1:8000
```

---

## 📁 Project Structure

```text
CodeGraphAI
│
├── app
│   ├── services
│   ├── static
│   ├── templates
│   ├── models
│   └── main.py
│
├── chroma_db
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🎯 Use Cases

### Developers

* Understand unfamiliar repositories
* Accelerate onboarding
* Explore architecture faster

### Engineering Managers

* Evaluate repository health
* Review engineering quality
* Identify technical debt

### Technical Leads

* Analyze architecture decisions
* Compare implementations
* Assess deployment readiness

### Open Source Contributors

* Understand project structure
* Find relevant code paths
* Discover ownership patterns

---

## 🔮 Future Roadmap

* Repository Health Score
* Architecture Graph Visualization
* AI-Generated System Design Diagrams
* Semantic Code Search
* Multi-Repository Workspaces
* Team Collaboration Features
* Automated Documentation Generation
* Engineering Trend Analytics

---

## 👨‍💻 Author

**Anish Bellamkonda**

Software Engineer focused on distributed systems, developer tooling, AI-powered engineering workflows, and scalable backend platforms.

GitHub: https://github.com/AnishBellamkonda

---

## ⭐ Support

If you find this project useful, consider giving it a star on GitHub.

It helps the project reach more developers and engineering teams.
