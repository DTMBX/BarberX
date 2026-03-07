# Embed Contract — Tillerstead Toolkit

**Document:** Integration specification for embedding Tillerstead Toolkit  
**Date:** 2026-03-06  
**Status:** Draft  
**Parties:** Tillerstead LLC (site) ↔ Tillerstead LLC (toolkit)

---

## Purpose

This document defines how the Tillerstead Toolkit (calculator hub + API) may be
embedded or surfaced on the Tillerstead marketing site (`tillerstead.com`) while
preserving deployment independence and clean boundaries.

---

## Integration Method

**Primary:** iframe embed  
**Fallback:** Linked standalone app

### iframe Embed

The Tillerstead site renders an `<iframe>` on its `/tools/` or `/calculators/`
page. The iframe `src` points to the toolkit's deployed URL.

```html
<iframe
  id="tillerstead-toolkit"
  src="https://api.tillerstead.com/calculators/"
  title="Tillerstead Calculator Hub"
  loading="lazy"
  sandbox="allow-scripts allow-forms allow-same-origin"
  style="width: 100%; border: none; min-height: 600px;"
></iframe>
```

### Linked Fallback

If the iframe is unavailable or JavaScript is disabled, the page displays a
direct link:

```html
<noscript>
  <p>
    <a href="https://api.tillerstead.com/calculators/">
      Open Tillerstead Calculator Hub
    </a>
  </p>
</noscript>
```

---

## Communication Protocol

### Parent → Toolkit (optional)

| Message | Payload | Purpose |
|---------|---------|---------|
| `theme-sync` | `{ theme: "dark" \| "light" }` | Match parent site theme |
| `context` | `{ page: string }` | Inform toolkit which parent page loaded it |

### Toolkit → Parent

| Message | Payload | Purpose |
|---------|---------|---------|
| `resize` | `{ height: number }` | Allow parent to adjust iframe height |
| `result` | `{ calculator: string, summary: string }` | Pass calculator result to parent (optional) |
| `navigate` | `{ url: string }` | Request parent to navigate (e.g., to contact page) |

### Message Format

All messages use `window.postMessage` with a structured envelope:

```json
{
  "source": "tillerstead-toolkit",
  "type": "resize",
  "payload": { "height": 840 }
}
```

The parent must validate that `event.origin` matches the expected toolkit
domain before processing any message.

---

## Boundary Rules

### Toolkit iframe MUST NOT:

- Access or modify the parent page DOM.
- Read cookies, localStorage, or sessionStorage from the parent origin.
- Make authenticated API calls on behalf of the parent site.
- Display Evident Technologies branding.
- Load scripts from Evident-owned domains.

### Parent site MUST NOT:

- Inject scripts into the iframe.
- Override iframe styles via parent CSS.
- Intercept or modify toolkit API requests.
- Present toolkit results as Evident products.

### Shared Resources: NONE

- No shared `node_modules`.
- No shared JavaScript bundles.
- No shared CSS files (theme sync via `postMessage` only).
- No shared API endpoints.
- No shared auth tokens or session state.

---

## Deployment Independence

| Aspect | Tillerstead Site | Tillerstead Toolkit |
|--------|-----------------|-------------------|
| **Repo** | `DTMBX/Tillerstead` | `DTMBX/tillerstead-toolkit` |
| **Hosting** | Netlify | Railway |
| **Domain** | tillerstead.com | api.tillerstead.com (or Railway default) |
| **Build** | Jekyll | FastAPI + Uvicorn |
| **Deploy trigger** | Push to main | Push to main |
| **Can deploy independently?** | Yes | Yes |

---

## Branding Inside Embed

The toolkit UI inside the iframe must use **Tillerstead LLC branding only**:

- Dark theme with emerald/gold accents (per UI_DESIGN_SPEC.md)
- Tillerstead logo or wordmark
- No Evident Technologies references
- Footer: "Tillerstead LLC — tillerstead.com"

---

## CORS Configuration

The toolkit API must allow the following origins:

```
https://tillerstead.com
https://www.tillerstead.com
http://localhost:3000 (development only)
```

It must NOT allow:

```
https://evident.icu
https://evidenttechnologies.com
https://devon-tyler.com
```

---

## Future Considerations

- **White-label licensing:** If the toolkit were ever offered as a licensed
  module to other contractors, this contract would need versioning and a
  separate licensing section.
- **API key authentication:** If the toolkit API requires authentication for
  embedded use, the parent site would pass an API key as a URL parameter or
  via `postMessage`, never via shared cookies.
- **Analytics:** Each surface tracks its own analytics independently. The
  parent does not inject analytics scripts into the iframe.
