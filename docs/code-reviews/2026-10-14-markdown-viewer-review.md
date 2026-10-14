# Code Review: Markdown Viewer

## Review Summary

- **Scope**: `static/js/viewer.js`, the script tags in `static/index.html` (lines 79-82), `static/vendor/marked.min.js` (marked 15.0.12), and `static/vendor/purify.min.js` (DOMPurify 3.4.17). Working tree. This project is not a git repository, so there is no commit range.
- **Assessment**: Needs changes.

The viewer fills the category, title, and modified time, parses markdown, and on the happy path sanitizes the HTML before `innerHTML`. Two branches do not do what the comments say: missing DOMPurify writes unsanitized HTML, and the highlight.js hook is not an API that marked 15 calls.

## Findings

### Critical / Blocker

**1. A missing sanitizer assigns agent HTML to `innerHTML`**

`static/js/viewer.js` lines 41-44:

```javascript
const rawHtml = window.marked ? window.marked.parse(doc.content || "") : doc.content;
const cleanHtml = window.DOMPurify ? window.DOMPurify.sanitize(rawHtml) : rawHtml;
markdownBody.innerHTML = cleanHtml;
```

Document bodies are agent output and are untrusted. `marked.parse` keeps raw HTML that was in the markdown. If `purify.min.js` fails to load or is blocked, `window.DOMPurify` is missing and `cleanHtml` is that HTML. Line 44 then inserts it. With both scripts loaded, `DOMPurify.sanitize` does run, so the current page is safe only while the vendor script loads.

Proposed fix: refuse to parse into HTML unless both libraries exist.

```javascript
if (!window.marked || !window.DOMPurify) {
  markdownBody.textContent = "Markdown renderer failed to load.";
  return;
}
const rawHtml = window.marked.parse(doc.content || "");
markdownBody.innerHTML = window.DOMPurify.sanitize(rawHtml);
```

Use `textContent` for the failure message so that branch cannot parse tags.

### Improvement

**1. Syntax highlighting never runs with marked 15.0.12**

`static/js/viewer.js` lines 6-14 pass a `highlight` function to `marked.setOptions`. The comment says this integrates highlight.js. `static/vendor/marked.min.js` is marked 15.0.12, and that build has no `highlight` option, so the function is stored and never called. Fenced code blocks render as plain `pre` / `code`. `highlight.min.js` and `highlight-dark.css` are loaded for a path that does not execute.

Proposed fix: register a code renderer, and keep the sanitize call after `parse` so highlighted markup is still cleaned.

```javascript
window.marked.use({
  gfm: true,
  breaks: false,
  renderer: {
    code({ text, lang }) {
      const language = window.hljs.getLanguage(lang) ? lang : "plaintext";
      const value = window.hljs.highlight(text, { language }).value;
      return `<pre><code class="hljs language-${language}">${value}</code></pre>\n`;
    },
  },
});
```

Use `language` in the class only after `getLanguage` accepts it, so the fence info string cannot add extra attributes. Leave `DOMPurify.sanitize` on the parse result.

**2. Viewer behavior has no test**

Pytest serves `viewer.js` as a static file and does not execute it. A regression in the sanitizer fallback or the marked options will not fail `uv run pytest`. A small node test can load the same call sequence against the vendor builds: markdown containing `<script>` must not survive sanitize, and a fenced `python` block must contain `hljs` after the renderer fix. The project has no JS test runner today, so this is new coverage rather than a change to the existing suite.

### Nitpick

**1. Unknown folders are labeled as explanations**

`static/js/viewer.js` line 30 treats every `doc.folder` other than `code-reviews` as `Explanation`. The API only allows two folders, so this is latent. Map unknown values to the raw folder name so a future category does not display the wrong badge.

## Compliance Checklist

- [x] `viewer.js` is 48 lines and is its own module.
- [x] With DOMPurify loaded, HTML is sanitized before `innerHTML` (line 44).
- [x] Vendor libraries are local files, so rendering does not depend on a network CDN.
- [ ] The unsanitized fallback contradicts the rule that rendered agent content is always sanitized.
- [ ] The highlight.js integration does not match marked 15.
- [ ] No automated test runs the renderer.
