# Implementation Plan - Agent Log App

## Overview
A local web application built with Python (Flask) and vanilla ES modules to inspect and read agent-generated code reviews and explanations across local projects.

---

## File Structure

```
D:\agent-log\
├── pyproject.toml
├── uv.lock
├── app.py
├── settings.json              (persisted user state: selected & recent roots)
├── agent_log/
│   ├── __init__.py
│   ├── paths.py              (central path validation and resolution)
│   ├── settings.py           (settings.json persistence and recent roots)
│   ├── browse.py             (directory browsing for folder picker)
│   └── routes.py             (Flask Blueprint for read-only GET endpoints)
├── static/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── api.js            (backend API client)
│   │   ├── list.js           (file list, search, sort, auto-refresh polling)
│   │   ├── viewer.js         (Markdown rendering, highlighting, sanitization)
│   │   ├── picker.js         (folder picker modal logic)
│   │   └── app.js            (application entry and coordinator)
│   └── vendor/
│       ├── marked.min.js
│       ├── purify.min.js
│       ├── highlight.min.js
│       └── highlight-dark.css
└── tests/
    ├── conftest.py
    ├── test_paths.py
    ├── test_settings.py
    └── test_api.py
```

---

## Step-by-Step Implementation

### Step 0: Git and Workspace Initialization
- Initialize Git repository with `git init`.
- Create `.gitignore` for Python caches, `.venv`, `.pytest_cache`, `.ruff_cache`, and `settings.json`.
- Ensure `uv` toolchain is available.
- Defer initial commit until the full suite is implemented and verified.

### Step 1: Initialize Project and Tooling
- Create `pyproject.toml` with dependencies: `flask`, `pytest`, `ruff`.
- Lock dependencies and create virtual environment using `uv lock` and `uv sync`.
- Configure `ruff` rules (line length <= 100, PEP 8) in `pyproject.toml`.

### Step 2: Build Path Validation Module (`agent_log/paths.py`)
- Implement a single path validation function `validate_doc_path(root_path, folder_type, filename)`.
- Enforce folder restriction: only allow `code-reviews` and `explanations`.
- Ensure filename ends with `.md`.
- Reject any directory traversal (`..`, absolute paths, symlinks resolving outside root).
- Return normalized `pathlib.Path` or raise validation error.

### Step 3: Build Settings Management Module (`agent_log/settings.py`)
- Implement `load_settings()` to read `settings.json`.
- Implement default root fallback: use current working directory if `docs/` folder exists.
- Implement `save_selected_root(path)` to persist the selected project and maintain a list of up to 5 recent roots.

### Step 4: Build Folder Browsing Engine (`agent_log/browse.py`)
- Implement `list_drives()` to list available Windows drive letters when browsing root.
- Implement `browse_directory(path)` to list subdirectories only (no files), sorted alphabetically.
- Add inspection check for each subfolder to flag whether it contains `docs/code-reviews` or `docs/explanations`.

### Step 5: Build API Routes and Server Entry (`agent_log/routes.py` & `app.py`)
- Create Flask Blueprint in `agent_log/routes.py` with read-only GET endpoints:
  - `GET /api/root`: Return current and recent roots; accept `?set=<dir>` to update root.
  - `GET /api/browse?path=<dir>`: Return subdirectories for folder picker.
  - `GET /api/files/<folder>`: Return list of markdown files with modification timestamps, newest first.
  - `GET /api/file/<folder>/<name>`: Return markdown file content.
- Implement concise JSON error responses with proper HTTP status codes (400, 403, 404).
- Create `app.py` entry point binding Flask strictly to `127.0.0.1:5000` and serving the static directory.

### Step 6: Build Automated Test Suite (`tests/`)
- Create `tests/conftest.py` with fixtures for temporary project directories and Flask test client.
- Create `tests/test_paths.py` testing traversal attacks, invalid extensions, and valid paths.
- Create `tests/test_settings.py` testing load, fallback, and recent roots rotation.
- Create `tests/test_api.py` testing all API endpoints, status codes, and browse error handling.
- Run and pass all tests via `uv run pytest`.

### Step 7: Vendor Frontend Libraries (`static/vendor/`)
- Download and place minified offline scripts into `static/vendor/`:
  - `marked.min.js` (Markdown parsing)
  - `purify.min.js` (DOMPurify HTML sanitization)
  - `highlight.min.js` (Syntax highlighting)
  - `highlight-dark.css` (Code syntax theme)

### Step 8: Build Frontend Layout and Styles (`static/index.html` & `static/css/styles.css`)
- Create `static/index.html`:
  - Semantic markup: header with active root selector, sidebar, main viewer, and folder picker modal.
  - Two stacked sections in sidebar: "Code Reviews" and "Explanations".
  - Empty state container with hint to select a file.
- Create `static/css/styles.css`:
  - Define CSS custom properties for palette (`#0F0F0F`, `#202020`, `#F8F8F8`, `#5DD62C`, `#337418`).
  - Implement two-column responsive layout with small-screen adaptations.
  - Style modal, cards, search input, active states, and code blocks.

### Step 9: Build Frontend Client Modules (`static/js/`)
- `static/js/api.js`: Thin fetch wrapper for all `/api/*` endpoints.
- `static/js/viewer.js`: Render markdown using `marked`, apply `hljs` highlighting, sanitize with `DOMPurify`, and display empty state.
- `static/js/list.js`: Render file lists, filter with search input, sort newest first, and poll for file changes every 3 seconds.
- `static/js/picker.js`: Folder picker modal handling navigation (Up button, drive letters, subfolder clicking, project highlighting, Select button).
- `static/js/app.js`: Initialize application state, load active root, bind components, and trigger initial render.

### Step 10: Linting, Test Verification, and Manual Smoke Test
- Run `uv run ruff check .` and `uv run ruff format --check .`.
- Run `uv run pytest` to ensure complete test coverage.
- Create sample review and explanation markdown files in `docs/` and run the app with `uv run app.py`.
- Verify folder browsing, file viewing, syntax highlighting, search/filter, and live auto-refresh in browser.
