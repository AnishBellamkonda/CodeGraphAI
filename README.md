# 🚀 CodeGraph AI

<div align="center">

### AI-Powered Repository Intelligence Platform

Transform repositories into searchable engineering knowledge with architecture analysis, repository intelligence, AI-powered code understanding, and engineering health insights.

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/ChromaDB-Vector%20Store-purple?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/GitHub-Repository%20Intelligence-black?style=for-the-badge&logo=github"/>
  <img src="https://img.shields.io/badge/AI-Engineering%20Copilot-blueviolet?style=for-the-badge"/>
</p>

**Analyze • Understand • Compare • Explore • Explain**

</div>

---

# Overview

Modern software systems often contain thousands of files, multiple services, distributed architectures, and years of accumulated engineering decisions. Understanding these systems is frequently one of the most time-consuming aspects of software development, technical due diligence, onboarding, architecture reviews, and repository maintenance.

CodeGraph AI was built to solve this problem.

CodeGraph AI is an AI-powered repository intelligence platform that enables developers and engineering teams to analyze repositories, understand architecture, explore dependencies, compare systems, evaluate engineering quality, and interact with codebases through a contextual AI Engineering Copilot.

Instead of manually exploring source code, engineers can quickly obtain architecture insights, repository summaries, dependency information, contributor ownership, pull request intelligence, testing insights, deployment readiness assessments, and AI-generated explanations through a unified workspace.

---

# Key Capabilities

## Repository Intelligence

Perform deep repository analysis across both local and GitHub-hosted projects.

### Features

* Local repository analysis
* GitHub repository analysis
* Repository indexing
* Source tree exploration
* Repository summarization
* Context-aware repository search
* Engineering knowledge extraction

---

## AI Engineering Copilot

Interact with repositories using natural language.

Developers can ask questions about architecture, workflows, implementation details, dependencies, ownership, and repository structure without manually navigating the entire codebase.

### Examples

```text
How does authentication work?

Where does request processing start?

Explain the repository architecture.

What services interact with the database?

Which files are responsible for deployment?
```

### Capabilities

* Architecture explanations
* Codebase Q&A
* Engineering onboarding assistance
* Workflow understanding
* Repository navigation assistance
* Context-aware engineering guidance

---

## Architecture Intelligence

CodeGraph AI automatically extracts repository structure and architectural information.

### Insights

* Repository architecture maps
* Service relationships
* Dependency analysis
* Layer identification
* System design understanding
* Architecture comparison

This helps engineering teams understand unfamiliar systems significantly faster than traditional manual exploration.

---

## Repository Comparison Engine

Compare repositories and architectural structures side-by-side.

### Supported Workflows

* Local repository comparison
* GitHub repository comparison
* Architecture diff analysis
* Structural change detection
* Engineering design comparison

Useful for:

* Migration projects
* Technical evaluations
* Architecture reviews
* Competitive analysis
* Platform modernization initiatives

---

## Engineering Health Platform

Evaluate repository quality using engineering-focused heuristics.

### Assessments

#### Deployment Readiness

Evaluate:

* Configuration quality
* Deployment structure
* Environment readiness
* Infrastructure indicators

#### Testing Health

Analyze:

* Test organization
* Coverage indicators
* Testing maturity
* Risk identification

#### Dependency Intelligence

Identify:

* Critical dependencies
* Dependency complexity
* Engineering risk areas
* Potential maintenance concerns

---

## GitHub Intelligence

Analyze repository activity and ownership.

### Features

#### Pull Request Dashboard

* Pull request analysis
* Change intelligence
* Engineering review assistance

#### Issue Dashboard

* Open issue analysis
* Engineering workload visibility
* Repository activity tracking

#### Contributor Analysis

* Ownership insights
* Contributor mapping
* Team visibility

#### Repository Health

* Repository quality indicators
* Activity monitoring
* Engineering metrics

---

## Team Operations

Monitor repositories at scale.

### Capabilities

* Watch Mode
* Repository monitoring
* Team Dashboard
* Historical tracking
* Portfolio sharing
* Workspace history

---

# Platform Architecture

```text
┌───────────────────────────────────────────────┐
│                 Frontend UI                   │
│              HTML • CSS • JS                  │
└──────────────────────┬────────────────────────┘
                       │
                       ▼

┌───────────────────────────────────────────────┐
│                  FastAPI API                  │
│              Application Layer                │
└──────────────────────┬────────────────────────┘
                       │

      ┌────────────────┼────────────────┐
      ▼                ▼                ▼

┌────────────┐  ┌────────────┐  ┌────────────┐
│ Repository │  │ GitHub     │  │ AI & RAG   │
│ Analysis   │  │ Services   │  │ Services   │
└────────────┘  └────────────┘  └────────────┘

      └────────────────┼────────────────┘
                       ▼

┌───────────────────────────────────────────────┐
│            ChromaDB Vector Store              │
│         Repository Knowledge Layer            │
└───────────────────────────────────────────────┘
```

---

# Technology Stack

## Backend

* Python
* FastAPI
* Uvicorn

## Repository Intelligence

* GitHub REST APIs
* Repository Parsing
* Repository Scanning
* Architecture Analysis

## AI Layer

* ChromaDB
* Retrieval-Augmented Generation (RAG)
* Semantic Repository Understanding

## Frontend

* HTML
* CSS
* JavaScript

---

# Getting Started

## Clone Repository

```bash
git clone https://github.com/AnishBellamkonda/CodeGraphAI.git
cd CodeGraphAI
```

## Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Launch Application

```bash
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

---

# Project Structure

```text
CodeGraphAI
│
├── app
│   ├── services
│   ├── static
│   ├── templates
│   ├── schemas.py
│   ├── repo_reader.py
│   └── main.py
│
├── chroma_db
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Use Cases

## Software Engineers

* Understand unfamiliar repositories
* Accelerate onboarding
* Explore architecture faster
* Analyze dependencies

## Technical Leads

* Conduct architecture reviews
* Compare implementations
* Evaluate engineering quality

## Engineering Managers

* Assess repository health
* Review engineering maturity
* Understand ownership structures

## Open Source Contributors

* Navigate large projects
* Discover ownership patterns
* Understand architecture efficiently

---

# Future Roadmap

* Repository Health Score
* Architecture Graph Visualization
* AI-Generated Architecture Diagrams
* Semantic Code Search
* Multi-Repository Workspaces
* Advanced Engineering Analytics
* Automated Documentation Generation
* Team Collaboration Features

---

# Author

## Anish Bellamkonda

Software Engineer specializing in:

* Distributed Systems
* Developer Platforms
* AI-Powered Engineering Tools
* Cloud Infrastructure
* Backend Systems

GitHub: https://github.com/AnishBellamkonda

---

<div align="center">

### ⭐ If you find this project useful, consider giving it a star.

Built to make repository understanding faster, smarter, and more accessible for engineering teams.

</div>
