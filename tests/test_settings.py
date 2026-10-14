"""Tests for settings persistence and recent roots management."""

import pytest

from agent_log.settings import load_settings, save_selected_root


def test_load_settings_default(tmp_path):
    """Missing settings file falls back gracefully."""
    settings_file = tmp_path / "nonexistent.json"
    data = load_settings(settings_file)
    assert "selected_root" in data
    assert len(data["recent_roots"]) >= 1


def test_save_selected_root(tmp_path):
    """Saving root directory updates active root and recent roots list."""
    settings_file = tmp_path / "settings.json"
    proj_a = tmp_path / "proj_a"
    proj_a.mkdir()

    updated = save_selected_root(proj_a, path=settings_file)
    assert updated["selected_root"] == str(proj_a.resolve())
    assert str(proj_a.resolve()) in updated["recent_roots"]


def test_save_selected_root_invalid_dir(tmp_path):
    """Attempting to select a nonexistent directory raises ValueError."""
    settings_file = tmp_path / "settings.json"
    with pytest.raises(ValueError):
        save_selected_root(tmp_path / "missing_dir", path=settings_file)


def test_recent_roots_deduplication(tmp_path):
    """Selecting an already present root moves it to the front without duplicates."""
    settings_file = tmp_path / "settings.json"
    p1 = tmp_path / "p1"
    p2 = tmp_path / "p2"
    p1.mkdir()
    p2.mkdir()

    save_selected_root(p1, path=settings_file)
    save_selected_root(p2, path=settings_file)
    final = save_selected_root(p1, path=settings_file)

    assert final["selected_root"] == str(p1.resolve())
    assert final["recent_roots"][0] == str(p1.resolve())
    assert final["recent_roots"].count(str(p1.resolve())) == 1
