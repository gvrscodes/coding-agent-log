/**
 * Application bootstrapper and orchestrator.
 */

import { fetchFileContent, fetchRoot, setRoot } from "./api.js";
import { initList, reloadLists } from "./list.js";
import { initPicker, openPicker } from "./picker.js";
import { renderDocument, renderEmpty } from "./viewer.js";

const recentSelect = document.getElementById("recent-roots-select");
const openPickerBtn = document.getElementById("open-picker-btn");

let currentActiveRoot = "";

function updateRecentDropdown(settings) {
  currentActiveRoot = settings.selected_root;
  recentSelect.innerHTML = "";

  for (const root of settings.recent_roots || [settings.selected_root]) {
    const opt = document.createElement("option");
    opt.value = root;
    opt.textContent = root;
    opt.selected = root === settings.selected_root;
    recentSelect.appendChild(opt);
  }
}

async function handleRootChange(newPath) {
  try {
    const updated = await setRoot(newPath);
    updateRecentDropdown(updated);
    renderEmpty();
    reloadLists();
  } catch (err) {
    alert("Failed to switch root: " + err.message);
  }
}

async function handleFileSelect(folder, name) {
  try {
    const doc = await fetchFileContent(folder, name);
    renderDocument(doc);
  } catch (err) {
    alert("Failed to read document: " + err.message);
  }
}

async function bootstrap() {
  initPicker();
  renderEmpty();

  const settings = await fetchRoot();
  updateRecentDropdown(settings);

  initList(handleFileSelect);

  recentSelect.addEventListener("change", (e) => handleRootChange(e.target.value));
  openPickerBtn.addEventListener("click", () => {
    openPicker(currentActiveRoot, (chosenPath) => handleRootChange(chosenPath));
  });
}

bootstrap().catch((err) => console.error("Agent Log failed to initialize:", err));
