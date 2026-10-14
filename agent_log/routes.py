from flask import Blueprint, current_app, jsonify, request

from agent_log.browse import browse_directory
from agent_log.paths import PathValidationError, validate_doc_path, validate_folder_path
from agent_log.settings import DEFAULT_SETTINGS_PATH, load_settings, save_selected_root

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _get_settings_path():
    # Allow tests to point to temporary settings file
    return current_app.config.get("SETTINGS_PATH", DEFAULT_SETTINGS_PATH)


@api_bp.route("/root", methods=["GET"])
def handle_root():
    """Return or update the active project root."""
    set_path = request.args.get("set")
    settings_path = _get_settings_path()
    if set_path:
        try:
            settings = save_selected_root(set_path, path=settings_path)
            return jsonify(settings)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
    return jsonify(load_settings(path=settings_path))


@api_bp.route("/browse", methods=["GET"])
def handle_browse():
    """Browse directories for the folder picker modal."""
    path_param = request.args.get("path")
    try:
        data = browse_directory(path_param)
        return jsonify(data)
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 403


@api_bp.route("/files/<folder>", methods=["GET"])
def handle_list_files(folder: str):
    """List markdown files inside an allowed category folder, newest modified first."""
    settings = load_settings(path=_get_settings_path())
    root = settings.get("selected_root", "")
    try:
        folder_path = validate_folder_path(root, folder)
    except PathValidationError as exc:
        return jsonify({"error": str(exc)}), 403

    if not folder_path.is_dir():
        return jsonify([])

    items = []
    # Collect only valid markdown files and read metadata for sorting
    for entry in folder_path.iterdir():
        if entry.is_file() and entry.name.lower().endswith(".md"):
            stat = entry.stat()
            items.append({"name": entry.name, "modified": stat.st_mtime, "size": stat.st_size})

    items.sort(key=lambda x: x["modified"], reverse=True)
    return jsonify(items)


@api_bp.route("/file/<folder>/<name>", methods=["GET"])
def handle_get_file(folder: str, name: str):
    """Return content of an individual markdown file."""
    settings = load_settings(path=_get_settings_path())
    root = settings.get("selected_root", "")
    try:
        file_path = validate_doc_path(root, folder, name)
    except PathValidationError as exc:
        return jsonify({"error": str(exc)}), 403
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404

    content = file_path.read_text(encoding="utf-8", errors="replace")
    stat = file_path.stat()
    return jsonify(
        {
            "name": file_path.name,
            "folder": folder,
            "content": content,
            "modified": stat.st_mtime,
        }
    )
