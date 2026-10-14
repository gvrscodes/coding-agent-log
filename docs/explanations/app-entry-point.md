# Application Entry Point

## Executive Summary

`app.py` is the process entry point for the local Agent Log viewer. It builds a Flask application that serves the static page and registers the read-only `/api` blueprint. The development server listens only on `127.0.0.1:5000`, so the viewer stays on the machine that started it.

## What the Code Does

The module exposes one function, `create_app() -> Flask`, and a module-level `app` instance created by calling it. Importing the module builds the application. Starting the HTTP server happens only when the file is run as a script.

`create_app` does three things:

1. Construct a `Flask` app with `static_folder="static"` and `static_url_path=""`.
2. Register `api_bp` from `agent_log.routes`, which owns every `/api` route.
3. Add a `/` route that returns `static/index.html`.

`static_url_path=""` places files from `static/` at the site root. A request for `/css/styles.css` reads `static/css/styles.css`. The same mapping covers `js/` and `vendor/`. The index page can keep root-relative URLs such as `css/styles.css` and `js/app.js`.

The `/` handler calls `send_from_directory` with the filename `index.html`. The directory is `app.static_folder`, or `"static"` if that attribute is empty. The function returns the configured app and does not bind a port.

At import time the module assigns `app = create_app()`. Tests and `flask --app app` use that factory or the resulting instance without starting a server. `tests/conftest.py` calls `create_app()`, then sets `TESTING` and `SETTINGS_PATH` on the new instance.

When the file is executed directly, the `if __name__ == "__main__"` block calls `app.run(host="127.0.0.1", port=5000, debug=False)`.

A browser load proceeds as follows:

1. `GET /` hits `index` and returns `static/index.html`.
2. The browser requests CSS, JavaScript, and vendor scripts. Flask's static handler serves them from `static/`.
3. Client modules call `/api/root`, `/api/browse`, `/api/files/<folder>`, and `/api/file/<folder>/<name>`. Those paths match `api_bp`, not the index route.

## Why It Was Built This Way

The application factory exists so tests can build an isolated app and point it at a temporary `settings.json`. A server started inside `create_app` would bind a port on every import, including pytest.

Routes live on a blueprint in `agent_log.routes`. The entry point stays a short wiring file, in line with the project limit of small modules. Path checks, settings, and browse logic stay behind the blueprint.

`static_url_path=""` matches the HTML as written. Serving static files under the default `/static` prefix would require rewriting every stylesheet, script, and vendor URL in `index.html`. An explicit `/` route is still required: the static handler serves `/index.html`, and it does not treat `/` as that file.

The server binds to `127.0.0.1` because the viewer is a local tool that reads project folders on disk. `0.0.0.0` would accept connections from other machines on the network. `debug=False` keeps the Werkzeug debugger and the reloader off. The debugger can execute code in the server process, which is unnecessary for a read-only viewer.

## Key Scenarios and Edge Cases

- **Imported, not executed.** Pytest and other importers receive a configured Flask app. The `app.run` call does not run, so no port is taken.
- **Port already in use.** Binding `127.0.0.1:5000` raises if another process owns that port. The module does not pick a fallback port.
- **Reachable addresses.** Clients on this machine can use `127.0.0.1` or `localhost`. A request to the machine's LAN address is refused.
- **Code changes while running.** With `debug=False` there is no reloader. Edits to Python or static files apply after the process is restarted. The browser still polls the file list on its own timer.
- **Unknown URLs.** `/api/...` is handled by the blueprint, which returns JSON errors. Any other path that is not a file under `static/` gets Flask's default 404. The index route only serves the fixed name `index.html`; it does not accept a path parameter.
- **Empty `static_folder`.** `send_from_directory` falls back to the `"static"` directory. With the current constructor that attribute is always set, so the fallback is defensive.
