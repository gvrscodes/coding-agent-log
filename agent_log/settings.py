"""Persistence for user project root selection in settings.json."""

import json
from pathlib import Path
from typing import Any

DEFAULT_SETTINGS_PATH = Path("settings.json")
MAX_RECENT_ROOTS = 5


def _get_default_root() -> str:
    # Use current working directory if it contains agent docs, else fallback to cwd
    cwd = Path.cwd().resolve()
    return str(cwd)


def load_settings(path: Path | str = DEFAULT_SETTINGS_PATH) -> dict[str, Any]:
    """Load settings from JSON, initializing defaults if file does not exist."""
    file_path = Path(path)
    if not file_path.is_file():
        default_root = _get_default_root()
        return {"selected_root": default_root, "recent_roots": [default_root]}

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # Corrupted settings reset to safe defaults
        default_root = _get_default_root()
        return {"selected_root": default_root, "recent_roots": [default_root]}

    selected = data.get("selected_root") or _get_default_root()
    recent = data.get("recent_roots") or [selected]
    return {"selected_root": selected, "recent_roots": recent[:MAX_RECENT_ROOTS]}


def save_selected_root(
    new_root: str | Path, path: Path | str = DEFAULT_SETTINGS_PATH
) -> dict[str, Any]:
    """Validate directory, update active root, and rotate recent roots list."""
    resolved_dir = Path(new_root).resolve()
    if not resolved_dir.is_dir():
        raise ValueError(f"Root path must be an existing directory: {new_root}")

    normalized = str(resolved_dir)
    settings = load_settings(path)

    # Move selected root to front of recent roots and deduplicate
    recent: list[str] = [normalized]
    for r in settings.get("recent_roots", []):
        if r != normalized and Path(r).exists():
            recent.append(r)

    updated = {
        "selected_root": normalized,
        "recent_roots": recent[:MAX_RECENT_ROOTS],
    }
    Path(path).write_text(json.dumps(updated, indent=2), encoding="utf-8")
    return updated
