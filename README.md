# Developer Intelligence Platform 🚀

A comprehensive, full-stack developer productivity and code intelligence platform that unifies static analysis, performance profiling, security auditing, and deployment validation into an interconnected, actionable workflow.

---

## 🌟 Overview

Developers traditionally juggle disconnected tools for code quality, dead code detection, performance monitoring, database optimization, and deployment checks. These tools often deliver isolated warnings without highlighting cause-and-effect relationships.

**Developer Intelligence Platform** bridges this gap across your entire stack:
> **Scan → Detect → Explain → Recommend → Fix → Verify → Deploy**

---

## 🎯 Key Features

- **Multi-Engine Code Intelligence**:
  - **Code Engine**: Syntax validation, dead code detection, complexity scoring, and refactoring tips.
  - **Context Engine**: Multi-file cross-dependency tracing and architectural impact assessment.
  - **Database Engine**: Query performance analysis, schema indexing suggestions, and connection pool validation.
  - **Security Engine (Strix)**: Static vulnerability detection (SQL injection, XSS, insecure dependencies, hardcoded secrets).
  - **Deployment Engine**: Dockerfile, CI/CD, and cloud configuration sanity checks.
  - **Self-Correction & Fix Validation Engine**: Automatic test validation and remediation verify-before-commit workflows.
- **Modern Interactive Dashboard**:
  - Built with **React 18 + Vite + Tailwind CSS**.
  - Interactive workspace with project health scores, dependency maps, and real-time analysis reports.
  - Folder-drop analysis zone for rapid on-demand code audits.
- **VS Code Extension Integration**:
  - In-editor sidebar provider and Webview UI for frictionless developer feedback inside VS Code.
- **OpenRouter AI Integration**:
  - LLM-assisted code explanations, automated patch generation, and contextual remediation.

---

## 📁 Repository Structure

```
.
├── backend/                  # FastAPI backend and core intelligence engines
│   ├── app/
│   │   ├── api/v1/           # API routes (analysis, auth, database, deployment, etc.)
│   │   ├── core/             # Database, config, security, Turso, OpenRouter
│   │   ├── engines/          # Code, Context, Security, Strix, Fix Validation
│   │   ├── models/           # Database entities
│   │   └── schemas/          # Pydantic schemas
│   └── requirements.txt
├── frontend/                 # Vite + React + Tailwind CSS dashboard
│   ├── src/components/       # UI components, dashboard, folder analyzer, hero
│   └── package.json
├── extension/                # VS Code extension
│   ├── src/                  # Sidebar provider, extension logic, API client
│   └── package.json
├── webview-ui/               # Extension webview interface
├── demo-projects/            # Sample projects for testing & validation
├── tests/                    # End-to-end integration and engine test suites
└── docs/                     # Architecture & blueprint documentation
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**

---

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env`:
   ```env
   OPENROUTER_API_KEY=your_key_here
   TURSO_DATABASE_URL=your_turso_db_url
   TURSO_AUTH_TOKEN=your_turso_auth_token
   ```
5. Run the backend API server:
   ```bash
   python run.py
   ```
   Backend will be available at `http://localhost:8000`.

---

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start development server:
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:5173`.

---

### VS Code Extension

1. Navigate to the extension directory:
   ```bash
   cd extension
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Build or launch in VS Code debugging mode (`F5`).

---

## 🧪 Testing

Run test suites:
```bash
pytest tests/
```

Run demo end-to-end validation:
```bash
python tests/demo_e2e.py
```

---

## 📄 License

This project is licensed under the MIT License.
