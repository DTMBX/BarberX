// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

// Status filter values must match normalized case status fields: active, pending, closed
(async () => {
  const list = document.getElementById("case-list");
  const q = document.getElementById("q"),
    status = document.getElementById("status");
  if (!list || !q || !status) return;

  const casesUrl = (list.dataset && list.dataset.casesJson) || "/cases.json";
  let items = [];
  try {
    const res = await fetch(casesUrl, { credentials: "same-origin" });
    if (!res.ok) throw new Error("Failed to load cases.json");
    items = await res.json();
  } catch (_err) {
    list.textContent = "Unable to load case index.";
    return;
  }

  const el = (tag, attrs) => {
    const node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach((k) => {
        if (k === "text") node.textContent = attrs[k];
        else if (k === "class") node.className = attrs[k];
        else node.setAttribute(k, attrs[k]);
      });
    }
    return node;
  };

  const clear = (node) => {
    while (node.firstChild) node.removeChild(node.firstChild);
  };

  const render = (rows) => {
    clear(list);
    rows.forEach((c) => {
      const li = el("li", { class: "case-item" });
      const a = el("a", { href: c.url });
      const strong = el("strong", {
        text: c.short_title || c.title || "Untitled",
      });
      a.appendChild(strong);

      const docket = Array.isArray(c.docket)
        ? c.docket.join(", ")
        : c.docket || "";
      const metaText = [
        (c.court || "").trim(),
        ("Docket: " + (docket || "")).trim(),
        ("Status: " + (c.status || "")).trim(),
        ("Filed: " + (c.filed_date || "")).trim(),
      ]
        .filter(Boolean)
        .join(" · ");
      const meta = el("div", { class: "meta", text: metaText });

      li.appendChild(a);
      li.appendChild(meta);
      list.appendChild(li);
    });
  };
  const filter = () => {
    const term = (q.value || "").toLowerCase(),
      st = status.value.toLowerCase();
    render(
      items.filter((c) => {
        const title = c && c.title ? String(c.title) : "";
        const shortTitle = c && c.short_title ? String(c.short_title) : "";
        const docketRaw =
          c && c.docket !== null && c.docket !== undefined ? c.docket : "";
        const docketStr = Array.isArray(docketRaw)
          ? docketRaw.join(" ")
          : String(docketRaw || "");
        const tags = c && Array.isArray(c.tags) ? c.tags.join(" ") : "";
        const hay = (
          title +
          " " +
          shortTitle +
          " " +
          docketStr +
          " " +
          tags
        ).toLowerCase();
        const cStatus = c && c.status ? String(c.status).toLowerCase() : "";
        return (!term || hay.includes(term)) && (!st || cStatus === st);
      }),
    );
  };
  q.addEventListener("input", filter);
  status.addEventListener("change", filter);
  render(items);
})();
