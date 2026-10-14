"""Tests for path traversal prevention and document resolution."""

import pytest

from agent_log.paths import (
    PathValidationError,
    validate_doc_path,
    validate_folder_path,
)


def test_validate_folder_path_success(mock_project):
    """Allowed doc folders resolve within root/docs."""
    folder = validate_folder_path(mock_project, "code-reviews")
    assert folder == (mock_project / "docs" / "code-reviews").resolve()


def test_validate_folder_path_invalid_category(mock_project):
    """Disallowed category names are rejected."""
    with pytest.raises(PathValidationError):
        validate_folder_path(mock_project, "secret_docs")


def test_validate_doc_path_success(mock_project):
    """Existing markdown files resolve accurately."""
    doc = validate_doc_path(mock_project, "code-reviews", "2026-10-14-initial-review.md")
    assert doc.is_file()
    assert doc.name == "2026-10-14-initial-review.md"


def test_validate_doc_path_missing_file(mock_project):
    """Non-existent markdown files trigger FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        validate_doc_path(mock_project, "code-reviews", "nonexistent.md")


def test_validate_doc_path_non_markdown(mock_project):
    """Non-markdown files are rejected with PathValidationError."""
    with pytest.raises(PathValidationError):
        validate_doc_path(mock_project, "code-reviews", "script.py")


def test_validate_doc_path_traversal_attempts(mock_project):
    """Path traversal sequences in filename are strictly blocked."""
    with pytest.raises(PathValidationError):
        validate_doc_path(mock_project, "code-reviews", "../secret.txt")

    with pytest.raises(PathValidationError):
        validate_doc_path(mock_project, "code-reviews", "..\\secret.txt")
