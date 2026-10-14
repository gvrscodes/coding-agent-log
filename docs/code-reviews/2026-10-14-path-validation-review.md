# Code Review: Path Validation

## Review Summary

- **Scope**: `agent_log/paths.py`, `tests/test_paths.py`. Working tree. This project is not a git repository, so there is no commit range.
- **Assessment**: Suggestions.

`validate_folder_path` and `validate_doc_path` are the only readers for document paths. Both resolve the target and require it to stay under `root/docs` through `_ensure_within`. Category names are limited to `code-reviews` and `explanations`, and filenames cannot contain separators, a leading dot, or a non-markdown extension.

## Findings

### Critical / Blocker

None.

### Improvement

**1. Symlink escape is implemented and untested**

`agent_log/paths.py` lines 14-22 call `Path.resolve()` and reject a target that is not inside the base with `relative_to`. A markdown symlink inside `docs/code-reviews` that points at a file outside that folder should raise `PathValidationError`. `tests/test_paths.py` never builds a symlink. `tests/conftest.py` writes `secret.txt` for this case, and no test links to it.

Proposed test:

```python
def test_validate_doc_path_rejects_symlink_escape(mock_project):
    link = mock_project / "docs" / "code-reviews" / "linked.md"
    link.symlink_to(mock_project / "secret.txt")
    with pytest.raises(PathValidationError):
        validate_doc_path(mock_project, "code-reviews", "linked.md")
```

Skip the test when the platform cannot create the symlink.

**2. Leading-dot markdown names are untested**

`agent_log/paths.py` line 39 rejects any filename that starts with `.`. `tests/test_paths.py` covers `../secret.txt`, `..\\secret.txt`, and `script.py`. It does not cover `.hidden.md`, which is a different rule from separators and extensions.

Proposed test: expect `PathValidationError` for `.hidden.md`.

### Nitpick

**1. Empty exception body**

`agent_log/paths.py` line 11 is a bare `pass` under `PathValidationError`. The docstring already states the purpose. Delete the `pass`.

## Compliance Checklist

- [x] `paths.py` is 53 lines, under the 150-line guide.
- [x] Functions stay near the 20-line guide. `_ensure_within` explains why it resolves before `relative_to`.
- [x] Type hints on public functions. Paths use `pathlib`.
- [x] Invalid paths raise `PathValidationError` or `FileNotFoundError`. Callers in `agent_log/routes.py` map those to 403 and 404.
- [x] Allowed categories and traversal strings have tests.
- [ ] Symlink escape and leading-dot filenames have no test.
