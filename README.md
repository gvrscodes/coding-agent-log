# Agent Log

Agent Log is a lightweight, local web application designed to browse and inspect agent-generated code reviews and technical explanations across development projects.

It reads markdown documents from `/docs/code-reviews` and `/docs/explanations` folders of any local project root, presenting them in a responsive, two-column interface.

---

## Features

- **Project Folder Picker**: In-app folder browser supporting Windows drive enumeration, directory traversal, and automatic detection/highlighting of projects containing agent documentation.
- **Root Persistence**: Retains selected project root across restarts with quick switching among recent project roots.
- **Two-Column Dashboard**: Categorized document lists (Code Reviews and Explanations) sorted with newest modifications first.
- **Real-Time Polling**: Browser automatically polls the local backend every 3 seconds to reflect newly created or updated files without full page reload.
- **Search and Filter**: Instant client-side filtering by document filename.
- **Secure Markdown Rendering**: Offline-first client rendering via `marked` with syntax highlighting (`highlight.js`) and sanitization (`DOMPurify`) to prevent malicious script injection.
- **Directory Traversal Protection**: Centralized path validator ensuring only authorized markdown files within target documentation folders are read.
- **Strict Localhost Binding**: Server binds exclusively to `127.0.0.1:5000`.

---

## Tech Stack

- **Backend**: Python 3.11+ with Flask (read-only GET endpoints).
- **Package Management**: `uv` with `pyproject.toml` and `uv.lock`.
- **Frontend**: Plain HTML5, CSS3, and vanilla ES modules (no frameworks, no bundler, no build step).
- **Libraries (Vendored Offline)**:
  - `marked.min.js`: Markdown parser
  - `purify.min.js`: DOMPurify HTML sanitizer
  - `highlight.min.js` & `highlight-dark.css`: Code syntax highlighter
- **Testing and Code Quality**: `pytest` and `ruff`.

---

## Project Structure

```
.
├── app.py                     # Application entry point (127.0.0.1:5000)
├── pyproject.toml             # Project dependencies and tool configurations
├── uv.lock                    # Locked dependency versions
├── settings.json              # Local persistence for active and recent roots
├── AGENTS.md                  # System prompt and core application requirements
├── GUIDELINES.md              # Writing standards for agent reviews and explanations
├── PLAN.md                    # Implementation roadmap and phase checklist
├── agent_log/                 # Python backend modules
│   ├── browse.py              # Directory and Windows drive browsing engine
│   ├── paths.py               # Security chokepoint and path traversal validation
│   ├── routes.py              # Flask Blueprint with read-only GET endpoints
│   └── settings.py            # User settings management
├── docs/                      # Agent documentation folders
│   ├── code-reviews/          # Agent-generated code review markdown files
│   └── explanations/          # Agent-generated architectural explanation files
├── static/                    # Frontend assets
│   ├── index.html             # Semantic single-page application layout
│   ├── css/
│   │   └── styles.css         # Theme palette and responsive styling
│   ├── js/
│   │   ├── api.js             # Backend HTTP client
│   │   ├── app.js             # Application coordinator
│   │   ├── list.js            # Document list, search filter, and polling
│   │   ├── picker.js          # Modal folder browser logic
│   │   └── viewer.js          # Markdown renderer and sanitization
│   └── vendor/                # Vendored offline JavaScript and CSS libraries
└── tests/                     # Automated pytest test suite
    ├── conftest.py            # Fixtures for isolated test environments
    ├── test_api.py            # API endpoint and security tests
    ├── test_paths.py          # Path validation and traversal attack tests
    └── test_settings.py       # Settings loading and persistence tests
```

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- `uv` (recommended) or standard `pip`

### Installation

Clone the repository:

```bash
git clone https://github.com/gvrscodes/coding-agent-log.git
cd coding-agent-log
```

Sync dependencies using `uv`:

```bash
uv sync
```

Alternatively, create a virtual environment manually:

```bash
python -m venv .venv
source .venv/bin/activate       # On Linux/macOS or Git Bash
# or
.venv\Scripts\Activate.ps1     # On Windows PowerShell
pip install -e .
```

---

## Running the Application

Start the local server using `uv`:

```bash
uv run python app.py
```

Or from an active virtual environment:

```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## Running Tests and Linting

Run automated unit and integration tests:

```bash
uv run pytest
```

Run linting and formatting checks:

```bash
uv run ruff check .
uv run ruff format --check .
```

---

## Documentation Guidelines for Agents

When configuring autonomous agents to generate reviews and explanations, follow the structural specifications in [GUIDELINES.md](GUIDELINES.md):

- **Code Reviews (`docs/code-reviews/`)**: Actionable reviews categorized by severity (Critical, Improvement, Nitpick) and standards compliance.
- **Code Explanations (`docs/explanations/`)**: User-focused deep dives describing what the code does, the underlying mental model, and the rationale behind architectural tradeoffs.
