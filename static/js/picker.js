/**
 * Modal folder picker component for navigating project directories.
 */

import { browsePath } from "./api.js";

const modal = document.getElementById("picker-modal");
const currentPathEl = document.getElementById("picker-current-path");
const folderListEl = document.getElementById("picker-folder-list");
const upBtn = document.getElementById("picker-up-btn");
const selectBtn = document.getElementById("picker-select-btn");
const cancelBtn = document.getElementById("picker-cancel-btn");
const closeBtn = document.getElementById("picker-close-btn");

let pickerState = {
  currentPath: "",
  parentPath: null,
  selectedItemPath: "",
  onSelectCallback: null,
};

function renderFolders(folders) {
  folderListEl.innerHTML = "";
  if (folders.length === 0) {
    const li = document.createElement("li");
    li.className = "folder-item";
    li.textContent = "No subdirectories";
    li.style.opacity = "0.5";
    folderListEl.appendChild(li);
    return;
  }

  for (const item of folders) {
    const li = document.createElement("li");
    li.className = "folder-item";
    if (item.has_docs) li.classList.add("has-docs");

    li.textContent = item.name + (item.has_docs ? " (docs found)" : "");
    li.tabIndex = 0;

    // Single-click selects, double-click navigates inside
    li.addEventListener("click", () => {
      pickerState.selectedItemPath = item.path;
      Array.from(folderListEl.children).forEach((el) => el.classList.remove("selected"));
      li.classList.add("selected");
    });

    li.addEventListener("dblclick", () => navigateTo(item.path));
    li.addEventListener("keydown", (e) => {
      if (e.key === "Enter") navigateTo(item.path);
    });

    folderListEl.appendChild(li);
  }
}

async function navigateTo(targetPath) {
  try {
    const data = await browsePath(targetPath);
    pickerState.currentPath = data.current_path;
    pickerState.parentPath = data.parent_path;
    pickerState.selectedItemPath = data.current_path;

    currentPathEl.textContent = data.current_path || "(Drives Overview)";
    upBtn.disabled = data.parent_path === null;
    renderFolders(data.folders);
  } catch (err) {
    alert("Could not open directory: " + err.message);
  }
}

export function openPicker(startPath, onSelect) {
  pickerState.onSelectCallback = onSelect;
  modal.hidden = false;
  navigateTo(startPath || "");
}

export function closePicker() {
  modal.hidden = true;
}

export function initPicker() {
  upBtn.addEventListener("click", () => {
    if (pickerState.parentPath !== null) navigateTo(pickerState.parentPath);
  });

  cancelBtn.addEventListener("click", closePicker);
  closeBtn.addEventListener("click", closePicker);

  selectBtn.addEventListener("click", () => {
    const chosen = pickerState.selectedItemPath || pickerState.currentPath;
    if (chosen && pickerState.onSelectCallback) {
      pickerState.onSelectCallback(chosen);
    }
    closePicker();
  });
}
