// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

const $q = document.getElementById("q");
const $results = document.getElementById("results");
const $meta = document.getElementById("meta");

let data = [];

function scoreMatch(query, text) {
  if (!query) return 0;
  const q = query.toLowerCase().trim();
  if (!q) return 0;

  const t = (text || "").toLowerCase();
  if (!t) return 0;

  // Simple scoring: phrase > token hits
  let score = 0;
  if (t.includes(q)) score += 10;

  const tokens = q.split(/\s+/).filter(Boolean);
  for (const tok of tokens) {
    const hits = t.split(tok).length - 1;
    score += Math.min(hits, 20);
  }
  return score;
}

function render(query) {
  const q = (query || "").trim();
  const rows = data
    .map((item) => {
      const text = item.text || item.snippet || "";
      const s = scoreMatch(q, `${item.title}\n${item.caseId}\n${item.tags?.join(" ")}\n${text}`);
      return { item, s };
    })
    .filter((x) => (q ? x.s > 0 : true))
    .sort((a, b) => b.s - a.s)
    .slice(0, 50);

  $meta.textContent = data.length
    ? `${rows.length} result(s) shown • ${data.length} document(s) indexed`
    : "Loading index…";

  $results.innerHTML = rows
    .map(({ item, s }) => {
      const tags = (item.tags || []).slice(0, 6);
      const ocr = item.ocrNeeded ? `<span class="badge">OCR needed</span>` : "";
      const ok = item.ok ? "" : `<span class="badge">Index error</span>`;
      const err = item.error ? `<div class="snip">Index error: ${item.error}</div>` : "";
      return `
      <div class="card">
        <h3>${escapeHtml(item.title || item.caseId || "Untitled")}</h3>
        <div class="badges">
          <span class="badge">${escapeHtml(item.caseId || "")}</span>
          ${tags.map((t) => `<span class="badge">${escapeHtml(t)}</span>`).join("")}
          ${ocr}
          ${ok}
          ${q ? `<span class="badge">score: ${s}</span>` : ""}
        </div>
        ${item.snippet ? `<div class="snip">${escapeHtml(item.snippet)}</div>` : ""}
        ${err}
        <div class="actions">
          <a class="btn primary" href="${item.url}" target="_blank" rel="noopener">Open PDF</a>
        </div>
      </div>
    `;
    })
    .join("");
}

function escapeHtml(s) {
  return (s || "").replace(
    /[&<>"']/g,
    (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      })[c]
  );
}

async function init() {
  const res = await fetch("./data/index.json", { cache: "no-store" });
  data = await res.json();
  $meta.textContent = `${data.length} document(s) indexed`;
  render("");
}

$q.addEventListener("input", () => render($q.value));
init().catch((err) => {
  $meta.textContent = "Failed to load index.json";
  $results.innerHTML = `<div class="card"><div class="snip">${escapeHtml(String(err))}</div></div>`;
});
