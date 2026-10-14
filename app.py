"""Application entry point for Agent Log viewer."""

from flask import Flask, send_from_directory

from agent_log.routes import api_bp


def create_app() -> Flask:
    """Configure and initialize Flask instance serving API and static assets."""
    app = Flask(__name__, static_folder="static", static_url_path="")
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        # Serve main SPA interface
        return send_from_directory(app.static_folder or "static", "index.html")

    return app


app = create_app()

if __name__ == "__main__":
    # Restrict server strictly to localhost per security requirements in AGENTS.md
    app.run(host="127.0.0.1", port=5000, debug=False)
