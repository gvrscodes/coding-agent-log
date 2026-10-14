"""Integration tests for read-only Flask API endpoints."""


def test_api_root_get(app_client, mock_project):
    """GET /api/root returns selected root and recent roots."""
    res = app_client.get("/api/root")
    assert res.status_code == 200
    data = res.get_json()
    assert data["selected_root"] == str(mock_project.resolve())
    assert isinstance(data["recent_roots"], list)


def test_api_root_set(app_client, tmp_path):
    """GET /api/root?set=<dir> updates the active root."""
    new_dir = tmp_path / "new_project"
    new_dir.mkdir()

    res = app_client.get(f"/api/root?set={new_dir}")
    assert res.status_code == 200
    assert res.get_json()["selected_root"] == str(new_dir.resolve())


def test_api_root_set_invalid(app_client, tmp_path):
    """GET /api/root?set=<invalid> returns 400."""
    res = app_client.get(f"/api/root?set={tmp_path}/does_not_exist")
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_api_browse_valid(app_client, mock_project):
    """GET /api/browse lists subfolders with doc indicators."""
    res = app_client.get(f"/api/browse?path={mock_project}")
    assert res.status_code == 200
    data = res.get_json()
    assert "folders" in data
    folder_names = [f["name"] for f in data["folders"]]
    assert "docs" in folder_names


def test_api_browse_invalid_path(app_client, tmp_path):
    """GET /api/browse on non-existent path returns 404."""
    res = app_client.get(f"/api/browse?path={tmp_path}/invalid")
    assert res.status_code == 404


def test_api_files_list(app_client):
    """GET /api/files/<folder> returns markdown files in category."""
    res = app_client.get("/api/files/code-reviews")
    assert res.status_code == 200
    files = res.get_json()
    assert len(files) == 1
    assert files[0]["name"] == "2026-10-14-initial-review.md"


def test_api_files_invalid_category(app_client):
    """GET /api/files/<invalid> returns 403."""
    res = app_client.get("/api/files/passwords")
    assert res.status_code == 403


def test_api_file_content(app_client):
    """GET /api/file/<folder>/<name> returns markdown text."""
    res = app_client.get("/api/file/code-reviews/2026-10-14-initial-review.md")
    assert res.status_code == 200
    data = res.get_json()
    assert "# Review" in data["content"]


def test_api_file_not_found(app_client):
    """GET /api/file/<folder>/<missing> returns 404."""
    res = app_client.get("/api/file/code-reviews/missing.md")
    assert res.status_code == 404


def test_api_file_traversal_blocked(app_client):
    """GET /api/file with traversal path returns 403."""
    res = app_client.get("/api/file/code-reviews/..%2Fsecret.txt")
    assert res.status_code in (403, 404)


def test_index_and_static_assets(app_client):
    """Verify index.html and static assets are properly served."""
    index_res = app_client.get("/")
    assert index_res.status_code == 200
    assert b"Agent Log" in index_res.data

    css_res = app_client.get("/css/styles.css")
    assert css_res.status_code == 200
    assert b"--bg-page" in css_res.data

    js_res = app_client.get("/js/app.js")
    assert js_res.status_code == 200
