# Code Review: Settings and Root Selection

## Review Summary

- **Scope**: `agent_log/settings.py`, `handle_root` in `agent_log/routes.py` (lines 10-26), `setRoot` in `static/js/api.js` (lines 18-20), `tests/test_settings.py`, and the root tests in `tests/test_api.py` (lines 4-27). Working tree. This project is not a git repository, so there is no commit range.
- **Assessment**: Needs changes.

Selected and recent roots persist in `settings.json`. Recent entries are deduplicated, capped at five, and moved to the front on select. The risky part is that the update is a GET query parameter with no check that the caller is this app.

## Findings

### Critical / Blocker

**1. `GET /api/root?set=` changes saved state for any local page**

`agent_log/routes.py` lines 18-23 write `settings.json` when the `set` query parameter is present. `static/js/api.js` lines 18-20 call that URL. The server binds to localhost and does not send CORS headers, so another site cannot read the JSON response. The write still happens for a simple GET. A page the user has open can request `http://127.0.0.1:5000/api/root?set=C:\Users\Public` from an image or a script tag. Flask does not check `Origin`. Any existing directory is accepted (`agent_log/settings.py` lines 40-42).

Impact is the saved project and the recent list. Document bodies stay unreadable cross-origin. The project requires GET-only routes, so the fix should stay a GET and reject browser-triggered side effects.

Proposed fix: require a custom header that image and script tags cannot set.

```python
# agent_log/routes.py, inside the set_path branch
if request.headers.get("X-Agent-Log") != "1":
    return jsonify({"error": "Missing client header"}), 400
```

```javascript
// static/js/api.js
async function getJson(url, options) {
  const res = await fetch(url, options);
  // existing status and JSON handling stays here
}

export async function setRoot(directory) {
  return getJson(`/api/root?set=${encodeURIComponent(directory)}`, {
    headers: { "X-Agent-Log": "1" },
  });
}
```

Add a test that `set` without the header returns 400 and does not change `selected_root`.

### Improvement

**1. Corrupt or unreadable settings are discarded with no signal**

`agent_log/settings.py` lines 26-29 catch `JSONDecodeError` and `OSError`, then return the working directory. The project standard says not to swallow exceptions silently. A truncated `settings.json` makes the viewer look like no project was ever chosen.

Proposed fix: log the exception with `logging.exception` before returning defaults. Keep the fallback so a bad file does not take down the process.

**2. A saved root that is no longer a directory is still treated as selected**

`agent_log/settings.py` line 31 uses `selected_root` whenever the string is non-empty. It does not check `is_dir()`. After a project folder is deleted, load keeps serving that path, and the file lists come back empty.

Proposed fix:

```python
selected = data.get("selected_root") or _get_default_root()
if not Path(selected).is_dir():
    selected = _get_default_root()
```

Apply the same `Path(r).is_dir()` filter to `recent_roots` here. Today that filter runs only inside `save_selected_root` (lines 49-51), so stale entries stay in the dropdown until the next save.

**3. Settings writes are not atomic, and write errors become a generic 500**

`agent_log/settings.py` line 57 uses `write_text` on the real file. A crash mid-write leaves JSON that the next load treats as corrupt. `handle_root` only catches `ValueError` (`agent_log/routes.py` lines 21-25). `OSError` from a read-only folder or a full disk becomes Flask's HTML 500, while the client expects JSON.

Proposed fix: write `settings.json.tmp` in the same directory and `Path.replace` it into place. In `handle_root`, catch `OSError` and return `jsonify({"error": str(exc)}), 500`.

**4. The default-root comment describes a check the code does not do**

`agent_log/settings.py` lines 11-14 say the working directory is used when it contains agent docs, and otherwise the working directory is the fallback. Both outcomes are the same, and the function never looks for `docs/`. Replace the comment with: the default is the process working directory until the user selects a project.

### Nitpick

**1. Settings path helper has no return type**

`agent_log/routes.py` line 10 defines `_get_settings_path()` with no annotation. Return `Path | str` so it matches `load_settings`.

**2. The five-root cap is untested**

`MAX_RECENT_ROOTS` is applied at `agent_log/settings.py` lines 33 and 55. `tests/test_settings.py` covers deduplication with two directories and does not add a sixth.

## Compliance Checklist

- [x] `settings.py` is 59 lines. Public functions have type hints and use `pathlib`.
- [x] Invalid directories raise `ValueError`, and the route maps that to 400 JSON.
- [x] Tests cover a missing settings file, a bad directory, and recent-root deduplication.
- [ ] `save_selected_root` is 23 lines, just over the function-length guide.
- [ ] Corrupt JSON, the recent-root cap, and a deleted selected root are untested.
- [ ] The `set` query parameter is a state change without a same-app check.
