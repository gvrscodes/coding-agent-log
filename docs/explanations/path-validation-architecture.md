# Path Validation and Directory Isolation

## Executive Summary
This document explains how Agent Log prevents directory traversal attacks and restricts filesystem reading strictly to agent documentation directories.

## What the Code Does
The `agent_log.paths` module provides a single validation choke-point `validate_doc_path(root, folder, filename)`.

1. Rejects path separators (`/`, `\`) and hidden dotfiles in `filename`.
2. Restricts folder categories strictly to `code-reviews` and `explanations`.
3. Ensures only `.md` extension files are requested.
4. Resolves the full target path using `pathlib.Path.resolve()`.
5. Verifies that the resolved path is strictly within the allowed folder tree using `relative_to()`.

## Why It Was Built This Way
Local viewer utilities run with user-level privileges. Without strict single-function validation, an agent-generated link or malicious file request could read sensitive files (such as SSH keys or system files). Centralizing path validation guarantees that no endpoint can accidentally bypass this check.

## Edge Cases Handled
- Directory traversal sequences like `../../etc/passwd` or `..\secret.txt`.
- Non-markdown file requests (e.g. `.env`, `.py`, `.json`).
- Requests referencing folders outside `code-reviews` and `explanations`.
