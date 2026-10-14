# Code Review: Frontend Shell

## Review Summary

- **Scope**: `static/index.html`, `static/css/styles.css`, `static/js/app.js`, `static/js/api.js`, `static/js/list.js`, `static/js/picker.js`. Working tree. This project is not a git repository, so there is no commit range. Markdown rendering is reviewed separately.
- **Assessment**: Needs changes.

The page has a header, a two-section sidebar, an empty state, search, a three-second list refresh, and a folder picker with Up, Select, and a drive overview. The file list cannot be used from the keyboard, and the picker can close or confirm a stale path.

## Findings

### Critical / Blocker

None.

### Improvement

**1. File rows are mouse-only**

`static/js/list.js` lines 39-43 select a document on `click`. The row has no `tabIndex`, no keyboard listener, and no button. `static/js/picker.js` lines 39-50 already make folder rows focusable and activate them on Enter. The project standard asks for keyboard-friendly controls. A keyboard user can reach search, the recent-root select, and Browse, and cannot open a review or an explanation.

Proposed fix: on each file row set `tabIndex = 0` and `role = "button"`. On `keydown`, Enter or Space runs the same handler as `click`. Add a visible focus ring:

```css
.file-item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
```

**2. Select can confirm a stale path, or close without a path**

`static/js/picker.js` lines 72-76 show the dialog and start `navigateTo` without clearing `selectedItemPath`. Lines 90-95 call the callback when `selectedItemPath` or `currentPath` is non-empty, then always call `closePicker()`.

Two outcomes follow:

- Select before the browse response arrives reuses the path from the previous open.
- Select on the drive overview, where both paths are empty, closes the dialog and leaves the root unchanged. The user gets no indication that nothing was selected.

Proposed fix: at the start of `openPicker`, set `selectedItemPath` to `""` and ignore Select while a `navigating` flag is true. Set that flag around the `browsePath` call in `navigateTo`. If the chosen path is still empty, leave the dialog open.

**3. Folder keyboard input navigates and never selects**

`static/js/picker.js` lines 49-50 treat Enter as "open this folder". Click selects a row (lines 42-46) and Select Folder confirms it. There is no key for that first step. Space should run the click handler. Enter can keep navigating.

**4. The dialog does not take focus and does not close on Escape**

`static/index.html` line 59 sets `role="dialog"` and `aria-modal="true"`. `initPicker` in `static/js/picker.js` lines 82-96 never moves focus into the dialog and never listens for Escape. Focus can stay on the Browse button behind the overlay.

Proposed fix: on open, focus `#picker-close-btn`. On `keydown` for Escape, call `closePicker` and return focus to `#open-picker-btn`.

**5. A failed poll is invisible, including the first load**

`static/js/list.js` lines 89-91 catch every error from `reloadLists` and do nothing. That function is also the initial fetch (line 103). If `/api/files/...` fails, both sections stay empty, which is the same UI as a project with no documents. The project standard says not to swallow exceptions silently.

Proposed fix: `console.error` the exception. When `state.reviews` and `state.explanations` are still empty, render the row text `Could not load documents` instead of `No documents found`.

**6. An open document stays stale after the file changes on disk**

Lines 84-87 re-render the sidebar when the JSON payload changes, including `modified`. `state.onSelect` is not called. The main pane keeps the previous markdown until the user clicks the row again.

Proposed fix: before replacing state, if `activeName` is set and the new entry's `modified` differs, call `state.onSelect(activeFolder, activeName)` after updating state.

**7. Active rows use the hover color**

`static/css/styles.css` lines 51-52 set both `:hover` and `.active` to `background: var(--border)` (`#337418`). The palette assigns `#337418` to hover and borders, and `#5DD62C` to the active file. The active row only adds a 3px accent border and bold text, so it matches a hovered row.

Proposed fix: leave hover on `var(--border)`. Set `.file-item.active` to a dark fill with accent text and the accent border:

```css
.file-item.active {
  background: #17360c;
  color: var(--accent);
  border-left: 3px solid var(--accent);
  font-weight: 600;
}
```

**8. The picker dialog is wider than a phone viewport**

`static/css/styles.css` line 80 sets `.modal-dialog` to `width: 550px`. The media query on lines 92-95 stacks the sidebar and does not change the dialog. Below 550px the dialog overflows the viewport.

Proposed fix: `width: min(550px, calc(100vw - 2rem));`. In that same media query, allow `.app-header` to wrap so the recent-root select (line 26, `max-width: 60%`) and the title can stack.

**9. Errors use `alert`**

`static/js/app.js` lines 35 and 44, and `static/js/picker.js` line 68, report failures with `alert`. That traps keyboard focus in a browser dialog outside the page. Put the message in an element with `role="alert"` in the header, and clear it on the next successful load or browse.

### Nitpick

**1. Empty-row styling is inline**

`static/js/list.js` line 56 and `static/js/picker.js` line 28 set `style.opacity`. Add a class, for example `.muted-row { opacity: 0.5; }`, and use it in both files.

**2. Long filenames can push the timestamp out of the sidebar**

`.file-item` (`static/css/styles.css` lines 47-50) is a flex row. The name span has no `min-width: 0` or wrapping. `.doc-title` on line 60 does wrap. Give the name span `min-width: 0` and `overflow-wrap: anywhere`.

## Compliance Checklist

- [x] JavaScript is plain ES modules, split by purpose, and uses `const` and `let`.
- [x] Each JS file is under 150 lines. `list.js` is the largest at 106.
- [x] The list query is filtered by filename, sections are labeled, and the empty state is the first view.
- [x] The list polls every three seconds and skips a DOM rebuild when the payload is unchanged (`static/js/list.js` lines 79-87).
- [x] `api.js` encodes path segments with `encodeURIComponent`.
- [ ] File rows are not keyboard accessible. The modal does not move focus or close on Escape.
- [ ] `renderFolders` (lines 22-55) and `createItemElement` (lines 24-46) exceed the ~20-line guide.
- [ ] There is no browser test harness. Pytest does not cover list, search, or picker behavior.
