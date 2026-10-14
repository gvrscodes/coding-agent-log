/**
 * Markdown rendering and viewer state management.
 */

// Configure marked with highlight.js integration
if (window.marked && window.hljs) {
  window.marked.setOptions({
    highlight: function (code, lang) {
      const language = window.hljs.getLanguage(lang) ? lang : "plaintext";
      return window.hljs.highlight(code, { language }).value;
    },
    gfm: true,
    breaks: false,
  });
}

const emptyState = document.getElementById("empty-state");
const docViewer = document.getElementById("doc-viewer");
const docCategory = document.getElementById("doc-category");
const docTitle = document.getElementById("doc-title");
const docTime = document.getElementById("doc-time");
const markdownBody = document.getElementById("markdown-body");

export function renderEmpty() {
  emptyState.hidden = false;
  docViewer.hidden = true;
}

export function renderDocument(doc) {
  docCategory.textContent = doc.folder === "code-reviews" ? "Code Review" : "Explanation";
  docTitle.textContent = doc.name;

  if (doc.modified) {
    const date = new Date(doc.modified * 1000);
    docTime.textContent = `Updated: ${date.toLocaleString()}`;
  } else {
    docTime.textContent = "";
  }

  // Parse markdown then sanitize HTML to prevent XSS from agent files
  const rawHtml = window.marked ? window.marked.parse(doc.content || "") : doc.content;
  const cleanHtml = window.DOMPurify ? window.DOMPurify.sanitize(rawHtml) : rawHtml;

  markdownBody.innerHTML = cleanHtml;
  emptyState.hidden = true;
  docViewer.hidden = false;
}
