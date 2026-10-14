# Agent Log App
## Description
This is an app to read and display code-review and code explanations from agents to users. The main feature is to read two folders /docs/code-reviews and /docs/explanations, each folder contains .md files, and display them for the user to view. The app will run locally.

The docs folders belong to other projects the user is developing. Agents write reviews and explanations into each project's docs folders, and this app views them. The user can switch between projects.

Guidelines and structure for agent-generated reviews and explanations are documented in @GUIDELINES.md

## Business Requirements
* A folder picker (in-app modal) lets the user choose the root folder of a project. It shows the current path, an Up button, a list of subfolders and a Select button. On Windows, the top level lists drive letters.
* Folders that contain `docs/code-reviews` or `docs/explanations` are highlighted in the picker.
* The selected root persists across restarts, and the user can switch between recent roots.
* Two column design, Left column a list of the files, right (main area) column the contents of the file.
* The left column shows two labeled sections stacked: Code Reviews and Explanations.
* Files are listed by filename, newest modified first.
* On load, the main area shows an empty state with a hint to pick a file.
* The file list can be searched and filtered.
* The file list refreshes automatically when files change.
* Responsive layout that works on small screens.
* No editing, only viewing.


# Technical Decisions

## Stack
* Backend: Python with Flask, run locally.
* Frontend: plain HTML, CSS and JavaScript, no build step.
* Markdown: rendered in the browser with `marked`, with tables and `highlight.js` for code blocks.
* Rendered HTML must be sanitized with `DOMPurify` before display, since files come from agents.
* Auto-refresh: the browser polls the file list every few seconds and updates when files change.
* The server exposes read-only GET endpoints only:
  * `/api/files/<folder>` lists the .md files of a folder, newest modified first.
  * `/api/file/<folder>/<name>` returns the contents of one file.
  * `/api/browse?path=<dir>` lists subfolder names only, for the folder picker. It never returns file contents. Folders containing `docs/code-reviews` or `docs/explanations` are flagged.
  * `/api/root` returns the selected root and recent roots.
* Selecting a root is the only state the app saves: the selected root and recent roots are stored in a local `settings.json`.
* Only the `code-reviews` and `explanations` folders of the selected root may be read. Reject any other path, including `..` traversal. The browse endpoint is the only exception and lists folder names only.
* The server binds to `127.0.0.1` only.
* Use `uv` to manage the environment and dependencies: dependencies are declared in `pyproject.toml` and locked in `uv.lock`. Run the app with `uv run` and the tests with `uv run pytest`.
* Tests with `pytest`, covering path validation and the API endpoints, including browse with bad paths and non-directories.

## Color Pallete

Roles:
* `#0F0F0F` page and main content background.
* `#202020` sidebar, cards, code blocks.
* `#F8F8F8` text.
* `#5DD62C` accent: active file, links, headings.
* `#337418` hover states, borders, dividers.

# Coding Standards
1. Focus on simplicity. Keep files small (about 150 lines max where is possible) and break code into separate files as needed.
2. Use small, easy to understand functions (about 20 lines max where is possible) with comments that explain why, not what.
3. Never use emojis.
4. Be concise.
5. Python: follow PEP 8, use type hints and `pathlib` for paths. Format and lint with `ruff`.
6. JavaScript: plain ES modules, `const` and `let` (never `var`), no frameworks. Split by purpose, for example `api.js`, `list.js`, `viewer.js`.
7. Security: all path checks go through one validation function. Always sanitize rendered content.
8. Prefer the standard library. Add a dependency only with a clear need.
9. Errors: return clear HTTP errors (400, 403, 404) with short JSON messages. Never swallow exceptions silently.
10. Every new endpoint or validation rule gets a test.
11. Use semantic HTML, keyboard-friendly controls and sufficient color contrast.

## Project Structure
* `app.py` entry point.
* `agent_log/` Python modules.
* `static/` HTML, CSS and JavaScript.
* `tests/` pytest tests.

Always test the code before you say task is finished.
