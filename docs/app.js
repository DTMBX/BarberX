const $q = document.getElementById("q");
const $results = document.getElementById("results");
const $meta = document.getElementById("meta");

// Configuration constants
const MAX_RESULTS = 50; // Maximum number of search results to display
const MAX_TAGS_DISPLAY = 6; // Maximum number of tags to show per item
const SCORE_PHRASE_MATCH = 10; // Bonus points for exact phrase match
const SCORE_TOKEN_MAX_HITS = 20; // Maximum points per token occurrence
const DEBOUNCE_DELAY_MS = 300; // Delay in ms before triggering search

let data = [];

/**
 * Computes a relevance score for how well a text matches a query.
 *
 * The query is lowercased and trimmed; if it is empty after trimming,
 * the function returns 0. The text is also lowercased (with `null`/`undefined`
 * treated as an empty string); if the resulting text is empty, the function
 * also returns 0.
 *
 * Scoring strategy:
 * - If the entire normalized query appears as a contiguous substring of the
 *   normalized text, a fixed bonus of SCORE_PHRASE_MATCH points is added.
 * - The query is then split on whitespace into tokens. For each token, the
 *   number of (potentially overlapping) occurrences in the text is counted,
 *   and up to SCORE_TOKEN_MAX_HITS points per token are added to the score
 *   (1 point per hit, capped at SCORE_TOKEN_MAX_HITS for that token).
 *
 * The final score is a non-negative integer; 0 indicates no match or an empty
 * query/text, and larger values indicate a stronger match. The score is not
 * upper-bounded in general but is constrained by the input lengths and the
 * per-token cap.
 *
 * @param {string} query - The search query to match against `text`.
 * @param {string} text - The text content to be scored against the `query`.
 * @returns {number} A non-negative integer relevance score for the match.
 */
function scoreMatch(query, text) {
  if (!query) return 0;
  const q = query.toLowerCase().trim();
  if (!q) return 0;

  const t = (text || "").toLowerCase();
  if (!t) return 0;

  // Simple scoring: phrase > token hits
  let score = 0;
  if (t.includes(q)) score += SCORE_PHRASE_MATCH;

  const tokens = q.split(/\s+/).filter(Boolean);
  for (const tok of tokens) {
    const hits = t.split(tok).length - 1;
    score += Math.min(hits, SCORE_TOKEN_MAX_HITS);
  }
  return score;
}

/**
 * Renders the search results for the given query.
 *
 * This function:
 * - Scores each item in the global `data` array using {@link scoreMatch},
 *   based on the query, title, case ID, tags, and text/snippet content.
 * - Filters out items with zero score when a non-empty query is provided.
 * - Sorts the remaining items by descending score and limits to the top MAX_RESULTS.
 * - Updates the `$meta` element with result and index counts.
 * - Populates the `$results` element with result cards.
 *
 * Each element in the `data` array is expected to be an object with:
 * - `title` {string} Optional human-readable title.
 * - `caseId` {string} Optional identifier shown as a badge.
 * - `tags` {string[]} Optional list of short tag strings.
 * - `snippet` {string} Optional text snippet to display.
 * - `text` {string} Optional full text used for scoring if present.
 * - `ocrNeeded` {boolean} Optional flag; when true, shows an "OCR needed" badge.
 * - `ok` {boolean} Optional flag; when falsy, shows an "Index error" badge.
 * - `error` {string} Optional error message displayed when present.
 * - `url` {string} URL to the underlying PDF resource.
 *
 * @param {string} query - The search query string; may be empty or whitespace.
 *                         An empty query shows up to MAX_RESULTS unfiltered items.
 */
function render(query) {
  const q = (query || "").trim();
  const rows = data
    .map(item => {
      const text = item.text || item.snippet || "";
      const s = scoreMatch(q, `${item.title}\n${item.caseId}\n${(item.tags || []).join(" ")}\n${text}`);
      return { item, s };
    })
    .filter(x => q ? x.s > 0 : true)
    .sort((a,b) => b.s - a.s)
    .slice(0, MAX_RESULTS);

  $meta.textContent = data.length
    ? `${rows.length} result(s) shown • ${data.length} document(s) indexed`
    : "Loading index…";

  $results.innerHTML = rows.map(({item, s}) => {
    const allTags = item.tags || [];
    const tags = allTags.slice(0, MAX_TAGS_DISPLAY);
    const hasMoreTags = allTags.length > MAX_TAGS_DISPLAY;
    const ocr = item.ocrNeeded ? `<span class="badge">OCR needed</span>` : "";
    const ok = item.ok ? "" : `<span class="badge">Index error</span>`;
    const err = item.error ? `<div class="snip">Index error: ${item.error}</div>` : "";
    return `
      <div class="card">
        <h3>${escapeHtml(item.title || item.caseId || "Untitled")}</h3>
        <div class="badges">
          <span class="badge">${escapeHtml(item.caseId || "")}</span>
          ${tags.map(t => `<span class="badge">${escapeHtml(t)}</span>`).join("")}
          ${hasMoreTags ? `<span class="badge">+${allTags.length - MAX_TAGS_DISPLAY} more</span>` : ""}
          ${ocr}
          ${ok}
          ${q ? `<span class="badge">score: ${s}</span>` : ""}
        </div>
        ${item.snippet ? `<div class="snip">${escapeHtml(item.snippet)}</div>` : ""}
        ${err}
        <div class="actions">
          <a class="btn primary" href="${sanitizeUrl(item.url)}" target="_blank" rel="noopener">Open PDF</a>
        </div>
      </div>
    `;
  }).join("");
}

/**
 * Sanitizes a URL to prevent javascript: and data: URI attacks.
 * Only allows http:, https:, and relative URLs.
 *
 * @param {string} url - The URL to sanitize.
 * @returns {string} The sanitized URL, or "#" if invalid.
 */
function sanitizeUrl(url) {
  if (!url || typeof url !== "string") return "#";
  const trimmed = url.trim();
  if (!trimmed) return "#";
  
  // Allow relative URLs (starting with / or ./ or ../)
  if (trimmed.startsWith("/") || trimmed.startsWith("./") || trimmed.startsWith("../")) {
    return trimmed;
  }
  
  // Only allow http: and https: protocols
  try {
    const parsed = new URL(trimmed, window.location.href);
    if (parsed.protocol === "http:" || parsed.protocol === "https:") {
      return trimmed;
    }
  } catch (e) {
    // Invalid URL format
  }
  
  return "#";
}

function escapeHtml(s) {
  return (s || "").replace(/[&<>"'`]/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;","`":"&#96;"
  }[c]));
}

/**
<<<<<<< HEAD
 * Sanitizes a URL to ensure it uses a safe protocol (http or https) or is a safe relative path.
 *
 * This function validates URLs to prevent XSS attacks via malicious protocols (e.g., javascript:, data:).
 * It accepts:
 * - Absolute URLs with http: or https: protocols
 * - Relative paths explicitly starting with /, ./, or ../
 *
 * All other URLs, including protocol-relative URLs (//), are rejected.
 *
 * @param {string} url - The URL to sanitize.
 * @returns {string} The sanitized URL if it uses a safe protocol or is a safe relative path, or "#" otherwise.
 */
function sanitizeUrl(url) {
  if (!url) return "#";
  const trimmed = String(url).trim();
  if (!trimmed) return "#";
  
  // Reject protocol-relative URLs (e.g., //malicious.com)
  if (trimmed.startsWith("//")) return "#";
  
  // Allow explicit relative paths
  if (trimmed.startsWith("/") || trimmed.startsWith("./") || trimmed.startsWith("../")) {
    return trimmed;
  }
  
  // Only allow URLs with explicit http or https protocol
  try {
    const parsed = new URL(trimmed);
    if (parsed.protocol === "http:" || parsed.protocol === "https:") {
      return trimmed;
    }
  } catch {
    // Invalid URL or relative path without explicit prefix - reject it
  }
  
  return "#";
=======
 * Creates a debounced version of a function that delays its execution
 * until after the specified delay has elapsed since the last invocation.
 *
 * @param {Function} func - The function to debounce.
 * @param {number} delay - The delay in milliseconds.
 * @returns {Function} The debounced function.
 */
function debounce(func, delay) {
  let timeoutId;
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
>>>>>>> 505c562 (Address review comments: add constants, URL sanitization, debouncing, and tag truncation indicator)
}

async function init() {
  const res = await fetch("./data/index.json", { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch index.json: ${res.status} ${res.statusText}`);
  }
  data = await res.json();
  $meta.textContent = `${data.length} document(s) indexed`;
  render("");
}

$q.addEventListener("input", debounce(() => render($q.value), DEBOUNCE_DELAY_MS));
init().catch(err => {
  $meta.textContent = "Failed to load index.json";
  $results.innerHTML = `<div class="card"><div class="snip">${escapeHtml(String(err))}</div></div>`;
});
