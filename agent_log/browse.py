"""Directory listing for the in-app project folder picker."""

import os
import string
import sys
from pathlib import Path
from typing import Any


def list_drives() -> list[dict[str, Any]]:
    """Enumerate existing drive letters on Windows."""
    drives = []
    if sys.platform == "win32":
        for letter in string.ascii_uppercase:
            drive_path = f"{letter}:\\"
            if os.path.exists(drive_path):
                drives.append(
                    {
                        "name": drive_path,
                        "path": drive_path,
                        "has_docs": _has_agent_docs(Path(drive_path)),
                    }
                )
    else:
        # Fallback for non-Windows platforms
        drives.append({"name": "/", "path": "/", "has_docs": _has_agent_docs(Path("/"))})
    return drives


def _has_agent_docs(folder: Path) -> bool:
    # Flag folders containing target doc directories for immediate visual cue in picker
    try:
        docs = folder / "docs"
        return (docs / "code-reviews").is_dir() or (docs / "explanations").is_dir()
    except (PermissionError, OSError):
        return False


def _get_parent_path(target: Path) -> str | None:
    # Returning empty string when at drive root navigates back to drive letter overview
    if target.parent == target:
        return ""
    return str(target.parent)


def browse_directory(path_str: str | None) -> dict[str, Any]:
    """List subfolders for the picker, flagging those containing agent documentation."""
    if not path_str or path_str.strip() == "":
        return {"current_path": "", "parent_path": None, "folders": list_drives()}

    target = Path(path_str).resolve()
    if not target.is_dir():
        raise FileNotFoundError(f"Path is not a valid directory: {path_str}")

    folders = []
    try:
        for entry in sorted(target.iterdir(), key=lambda p: p.name.lower()):
            try:
                # Omit files completely: browse endpoint only discovers folder trees
                if entry.is_dir() and not entry.name.startswith((".", "$")):
                    folders.append(
                        {
                            "name": entry.name,
                            "path": str(entry),
                            "has_docs": _has_agent_docs(entry),
                        }
                    )
            except (PermissionError, OSError):
                continue
    except (PermissionError, OSError) as exc:
        raise PermissionError(f"Cannot access directory: {path_str}") from exc

    return {
        "current_path": str(target),
        "parent_path": _get_parent_path(target),
        "folders": folders,
    }
