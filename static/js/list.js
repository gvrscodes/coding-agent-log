/**
 * Document list management, filtering, and auto-refresh polling.
 */

import { fetchFiles } from "./api.js";

const listReviews = document.getElementById("list-code-reviews");
const listExplanations = document.getElementById("list-explanations");

let state = {
  reviews: [],
  explanations: [],
  activeFolder: null,
  activeName: null,
  searchQuery: "",
  onSelect: null,
};

function formatTimestamp(epochSeconds) {
  const d = new Date(epochSeconds * 1000);
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function createItemElement(folder, file) {
  const li = document.createElement("li");
  li.className = "file-item";
  if (state.activeFolder === folder && state.activeName === file.name) {
    li.classList.add("active");
  }

  const nameSpan = document.createElement("span");
  nameSpan.textContent = file.name;

  const dateSpan = document.createElement("span");
  dateSpan.className = "file-date";
  dateSpan.textContent = formatTimestamp(file.modified);

  li.append(nameSpan, dateSpan);
  li.addEventListener("click", () => {
    state.activeFolder = folder;
    state.activeName = file.name;
    render();
    if (state.onSelect) state.onSelect(folder, file.name);
  });
  return li;
}

function renderSection(ul, folder, items) {
  ul.innerHTML = "";
  const query = state.searchQuery.toLowerCase();
  const filtered = items.filter((f) => f.name.toLowerCase().includes(query));

  if (filtered.length === 0) {
    const emptyLi = document.createElement("li");
    emptyLi.className = "file-item";
    emptyLi.style.opacity = "0.5";
    emptyLi.textContent = query ? "No matching files" : "No documents found";
    ul.appendChild(emptyLi);
    return;
  }

  for (const file of filtered) {
    ul.appendChild(createItemElement(folder, file));
  }
}

export function render() {
  renderSection(listReviews, "code-reviews", state.reviews);
  renderSection(listExplanations, "explanations", state.explanations);
}

export async function reloadLists() {
  try {
    const [revs, exps] = await Promise.all([
      fetchFiles("code-reviews"),
      fetchFiles("explanations"),
    ]);

    // Check if contents changed before re-rendering to prevent UI jitter
    const revsJson = JSON.stringify(revs);
    const expsJson = JSON.stringify(exps);
    const changed = revsJson !== JSON.stringify(state.reviews) || expsJson !== JSON.stringify(state.explanations);

    if (changed) {
      state.reviews = revs;
      state.explanations = exps;
      render();
    }
  } catch {
    // Suppress network poll glitches to keep UI stable
  }
}

export function initList(onSelectHandler) {
  state.onSelect = onSelectHandler;
  const searchInput = document.getElementById("file-search");
  searchInput.addEventListener("input", (e) => {
    state.searchQuery = e.target.value.trim();
    render();
  });

  // Initial fetch and start 3-second auto-refresh polling
  reloadLists();
  setInterval(reloadLists, 3000);
}
