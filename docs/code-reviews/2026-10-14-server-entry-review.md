# Code Review: Server Entry

## Review Summary

- **Scope**: `app.py`, `tests/conftest.py`, and `test_index_and_static_assets` in `tests/test_api.py` (lines 81-91). Working tree. This project is not a git repository, so there is no commit range.
- **Assessment**: Pass.

`create_app` builds a Flask app, serves `static/` at the site root, registers the API blueprint, and returns `index.html` for `/`. The listening socket is opened only under `__main__`, on `127.0.0.1:5000`, with the debugger off. Tests call `create_app()` and inject `SETTINGS_PATH` without starting that socket.

## Findings

### Critical / Blocker

None.

### Improvement

None.

### Nitpick

**1. The index view has no return type**

`app.py` lines 13-16 define nested `index()` with no annotation. Annotate the return as Flask's response type. `create_app` is already annotated, and `index` returns the result of `send_from_directory`.

**2. The localhost bind is not what the test exercises**

`app.py` lines 23-25 pass `host="127.0.0.1"` and `debug=False`. `tests/test_api.py` lines 81-91 use the Flask test client, which never calls `app.run`. The test proves `/` and `/css/styles.css` and `/js/app.js` are served. It does not prove the socket arguments.

A direct assertion on the call arguments needs a subprocess or a mock of `app.run`. Leaving the arguments in the `__main__` block is still the right place, because importing `app` must not listen. No code change is required unless a test is added that mocks `Flask.run` and checks `host` and `debug`.

## Compliance Checklist

- [x] `app.py` is 26 lines. `create_app` is within the function-length guide.
- [x] The process listens on `127.0.0.1` only, and `debug=False` keeps the Werkzeug debugger off.
- [x] `static_url_path=""` matches the root-relative asset URLs in `static/index.html`.
- [x] Tests cover `/` and the CSS and JS assets through the factory.
- [x] `tests/conftest.py` builds a separate app instance and points it at a temporary settings file.
