"""Pytest fixtures for Agent Log test suite."""

import pytest
from flask.testing import FlaskClient

from agent_log.settings import save_selected_root
from app import create_app


@pytest.fixture
def mock_project(tmp_path):
    """Create a temporary project structure with mock agent documents."""
    proj = tmp_path / "sample_project"
    reviews = proj / "docs" / "code-reviews"
    explanations = proj / "docs" / "explanations"
    reviews.mkdir(parents=True)
    explanations.mkdir(parents=True)

    # Populate sample documents
    rev_file = reviews / "2026-10-14-initial-review.md"
    rev_file.write_text("# Review\nEverything looks good.", encoding="utf-8")

    exp_file = explanations / "architecture-overview.md"
    exp_file.write_text("# Architecture\nDetailed system explanation.", encoding="utf-8")

    # Outside file to test path traversal isolation
    (proj / "secret.txt").write_text("classified", encoding="utf-8")
    return proj


@pytest.fixture
def app_client(tmp_path, mock_project) -> FlaskClient:
    """Provide Flask test client configured with an isolated settings file."""
    settings_file = tmp_path / "test_settings.json"
    save_selected_root(mock_project, path=settings_file)

    app = create_app()
    app.config["TESTING"] = True
    app.config["SETTINGS_PATH"] = str(settings_file)

    with app.test_client() as client:
        yield client
