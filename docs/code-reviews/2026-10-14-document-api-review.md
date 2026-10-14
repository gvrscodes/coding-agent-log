# Code Review: Document List and File API

## Review Summary

- **Scope**: `handle_list_files` and `handle_get_file` in `agent_log/routes.py` (lines 42-87), and the file tests in `tests/test_api.py` (lines 46-78). Working tree. This project is not a git repository, so there is no commit range.
- **Assessment**: Suggestions.

`GET /api/files/<folder>` lists `.md` files newest-modified first. `GET /api/file/<folder>/<name>` returns one file after `validate_doc_path`. Unknown categories return 403. A missing file returns 404. A missing category directory returns an empty list rather than an error.

## Findings

### Critical / Blocker

None.

### Improvement

**1. The list shows files the reader will reject**

`agent_log/routes.py` lines 57-60 keep every file whose name ends in `.md`. `validate_doc_path` in `agent_log/paths.py` lines 39-40 and 47 then rejects a leading dot and a resolved path that leaves the category folder. Two cases show up in the sidebar and fail on open:

- `.hidden.md` is listed, then `GET` returns 403.
- A symlink whose target is outside the category folder is listed because `Path.is_file()` follows links, then `GET` returns 403.

Proposed fix: build each row through the same rules as the reader. Skip names that fail them.

```python
try:
    validate_doc_path(root, folder, entry.name)
except (PathValidationError, FileNotFoundError):
    continue
```

`validate_doc_path` already checks the folder, so the list loop can use the resolved `folder_path` only for iteration.

**2. Filesystem errors on list and read bypass the JSON error shape**

`agent_log/routes.py` line 57 (`iterdir`) and line 78 (`read_text`) are outside the `PathValidationError` / `FileNotFoundError` handlers. A file removed after the existence check, or a directory the process cannot read, raises `OSError` and Flask returns an HTML 500. The client only understands `{"error": "..."}`.

Proposed fix: catch `OSError` in both handlers and return 404 JSON with the exception message.

**3. Newest-first order is untested, and the traversal assertion accepts a miss**

`agent_log/routes.py` line 62 sorts by `st_mtime` descending. `tests/test_api.py` lines 46-52 assert one known filename and never a relative order. Lines 75-78 accept status 403 or 404 for `..%2Fsecret.txt`. A 404 from the router means the filename never reached `validate_doc_path`, so the assertion passes when the security check did not run.

Proposed fixes:

- Create two markdown files, set `st_mtime` so the older name sorts last, and assert that order on `/api/files/code-reviews`.
- Assert 403 only. Add a name the router forwards and the validator rejects, such as `.secret.md`.
- Request `/api/files/explanations` and an empty or missing category folder. The empty-list branch at lines 52-53 has no test.

### Nitpick

**1. `routes.py` has no module docstring**

The other Python modules state their job in the first line. Add one: Flask routes for the read-only document and project API.

**2. Both handlers sit just over the 20-line guide**

`handle_list_files` is lines 43-63. `handle_get_file` is lines 67-87. Moving the markdown scan into a helper removes the length and is the same change as finding 1.

## Compliance Checklist

- [x] `routes.py` is 88 lines, under the 150-line guide.
- [x] Both document routes are GET. Category and filename checks go through `agent_log/paths.py`.
- [x] Validation failures return 403. Missing files return 404. Bodies are short JSON.
- [x] Happy-path list, invalid category, file read, and missing file are tested.
- [ ] List filtering does not match the filename and symlink rules used on read.
- [ ] Sort order, the explanations category, and the empty-directory response are untested.
