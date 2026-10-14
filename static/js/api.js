/**
 * Backend API client for read-only endpoints.
 */

async function getJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP error ${res.status}`);
  }
  return res.json();
}

export async function fetchRoot() {
  return getJson("/api/root");
}

export async function setRoot(directory) {
  // Uses GET query parameter to update root while honoring GET-only server constraint
  return getJson(`/api/root?set=${encodeURIComponent(directory)}`);
}

export async function browsePath(dirPath = "") {
  return getJson(`/api/browse?path=${encodeURIComponent(dirPath)}`);
}

export async function fetchFiles(folder) {
  return getJson(`/api/files/${encodeURIComponent(folder)}`);
}

export async function fetchFileContent(folder, name) {
  return getJson(`/api/file/${encodeURIComponent(folder)}/${encodeURIComponent(name)}`);
}
