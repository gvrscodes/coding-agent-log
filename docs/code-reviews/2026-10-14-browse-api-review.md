# Code Review: Browse API

## Review Summary

- **Scope**: `agent_log/browse.py`, `handle_browse` in `agent_log/routes.py` (lines 29-39), browse tests in `tests/test_api.py` (lines 30-43). Working tree. This project is not a git repository, so there is no commit range.
- **Assessment**: Suggestions.

`GET /api/browse` lists child directory names, full paths, and a `has_docs` flag. It returns file contents nowhere. An empty path returns Windows drive letters, and a missing or non-directory path raises `FileNotFoundError`, which the route maps to 404. Permission failures while iterating become 403.

## Findings

### Critical / Blocker

None.

### Improvement

**1. `os.path.exists` on every drive letter can stall the picker**

`agent_log/browse.py` lines 14-16 call `os.path.exists` for `A:\` through `Z:\`. On Windows, a disconnected network drive or an empty card reader can block that call for a long time. The folder picker waits on this response before it can draw.

Proposed fix: ask Windows for the drive type and skip drives with no media before `exists`.

```python
import ctypes

# DRIVE_NO_ROOT_DIR means the letter is present and the media is not.
if ctypes.windll.kernel32.GetDriveTypeW(drive_path) == 1:
    continue
```

Keep `_has_agent_docs` only for drives that pass that check.

**2. Non-directory browse is required coverage and is only half tested**

`agent_log/browse.py` lines 52-53 reject any path where `is_dir()` is false, including an existing file. `tests/test_api.py` lines 40-43 request a path that does not exist. The project standard asks for browse coverage of bad paths and non-directories. Those are different inputs: a missing path and a file both return 404, and only the missing path is tested.

Proposed test, using the `secret.txt` file the fixture already creates:

```python
def test_api_browse_file_path(app_client, mock_project):
    res = app_client.get(f"/api/browse?path={mock_project / 'secret.txt'}")
    assert res.status_code == 404
    assert "error" in res.get_json()
```

**3. `has_docs` is untested**

`agent_log/browse.py` lines 30-34 set `has_docs` when `docs/code-reviews` or `docs/explanations` is a directory. `test_api_browse_valid` only checks that a child named `docs` appears. Browsing the project root lists `docs`, and that child does not itself contain `docs/code-reviews`, so the assertion never observes `has_docs: true`.

Proposed test: browse `mock_project.parent` and assert the sample project entry has `has_docs` true. Add a second directory without those folders and assert `has_docs` false.

**4. `browse_directory` is past the function-length guide**

`agent_log/browse.py` lines 46-77 mix path checks, iteration, per-entry permission handling, and the response shape. Move the loop that builds the folder dicts into a helper such as `_list_child_folders(target)`.

### Nitpick

**1. Drive overview and parent path have no test**

An empty `path` query returns `parent_path: null` and drive entries (`agent_log/browse.py` lines 48-49). A drive root returns `parent_path: ""` so the client can go back to that overview (`agent_log/browse.py` lines 39-43). Neither response is asserted.

## Compliance Checklist

- [x] `browse.py` is 78 lines. The route handler is short and maps `FileNotFoundError` to 404 and `PermissionError` to 403.
- [x] The endpoint is GET and returns folder names only, which is the documented exception to document-root locking.
- [ ] `browse_directory` exceeds the ~20-line function guide.
- [ ] Tests miss existing non-directories, the `has_docs` flag, and the empty-path drive list.
