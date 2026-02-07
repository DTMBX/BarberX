// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

// Cloudflare Worker: Semantic Docket URL Routing
// This worker maps /cases/<slug>/docket/<entry-id> to the correct PDF in /cases/<slug>/filings/...
// Place this logic in your worker.js (or merge with existing logic)

addEventListener("fetch", (event) => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);

  // Semantic docket URL pattern: /cases/<slug>/docket/<entry-id>
  const docketPattern = /^\/cases\/([\w-]+)\/docket\/([\w-]+)/;
  const match = url.pathname.match(docketPattern);

  if (match) {
    const slug = match[1];
    const entryId = match[2];

    // Fetch the docket YAML for this case from GitHub raw (public)
    const docketUrl = `https://raw.githubusercontent.com/XTX33/FaithFrontier/main/_data/docket/${slug}.yml`;
    const docketResp = await fetch(docketUrl);
    if (!docketResp.ok) {
      return new Response("Docket not found", { status: 404 });
    }
    const docketText = await docketResp.text();

    // Find the entry with id == entryId
    const entryRegex = new RegExp(`- id: ${entryId}\\n([\\s\\S]*?)file: (.+)`, "m");
    const entryMatch = docketText.match(entryRegex);
    if (!entryMatch) {
      return new Response("Docket entry not found", { status: 404 });
    }
    const pdfPath = entryMatch[2].trim();
    // Absolute URL to the PDF asset
    const pdfUrl = `https://faithfrontier.org${pdfPath}`;

    // Redirect to the PDF
    return Response.redirect(pdfUrl, 302);
  }

  // ...existing upload logic or other routes...
  return new Response("Not found", { status: 404 });
}
