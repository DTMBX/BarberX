# Web Builder — Refactor Roadmap

Technical debt and future improvements for the Web Builder satellite tool.

---

## Priority Legend

- 🔴 **HIGH** — Affects stability, maintainability, or user experience
- 🟡 **MEDIUM** — Improves code quality or developer experience
- 🟢 **LOW** — Nice-to-have, polish

---

## 🔴 HIGH Priority

### Undo/Redo System

**Problem:** No history tracking for canvas changes.

**Impact:** Users cannot undo accidental deletions or changes.

**Solution:**

```javascript
// Add to state
history: [],
historyIndex: -1,

// Before each change
function saveToHistory() {
  state.history = state.history.slice(0, state.historyIndex + 1);
  state.history.push(JSON.stringify(state.elements));
  state.historyIndex++;
}

// Ctrl+Z / Ctrl+Y handlers
```

**Effort:** Medium (2-3 hours)

---

### Element Reordering

**Problem:** No way to reorder elements in canvas.

**Impact:** Users must delete and re-add to change order.

**Solution:** Add drag handles or up/down buttons in properties panel.

**Effort:** Medium (2-3 hours)

---

### Property Editing

**Problem:** The properties panel shows element info but doesn't allow editing (text, colors, etc.).

**Impact:** Users cannot customize elements without editing exported code.

**Solution:** Add input fields for editable properties defined in COMPONENTS.

**Effort:** High (4-6 hours)

---

## 🟡 MEDIUM Priority

### Error Boundaries

**Problem:** JavaScript errors crash the entire builder.

**Solution:** Add try-catch around critical operations, show user-friendly error toasts.

**Effort:** Low (1-2 hours)

---

### Export to File

**Problem:** Export copies to clipboard only.

**Solution:** Add "Download as ZIP" with HTML, CSS, and JS files.

**Effort:** Medium (2-3 hours)

---

### Template Import

**Problem:** Can only use built-in templates.

**Solution:** Add ability to import HTML/CSS files or URL.

**Effort:** Medium (3-4 hours)

---

### Code Editor Improvements

**Problem:** Code tabs are read-only display.

**Solution:** Add syntax highlighting (highlight.js) and copy buttons per tab.

**Effort:** Low (1-2 hours)

---

## 🟢 LOW Priority

### Theme Customization

**Problem:** Single dark theme only.

**Solution:** Add light theme toggle (already using CSS variables).

**Effort:** Low (1 hour)

---

### Keyboard Shortcut Reference

**Problem:** No visible documentation of keyboard shortcuts.

**Solution:** Add "?" key to show shortcut modal.

**Effort:** Low (1 hour)

---

### Component Search

**Problem:** Must scroll through components to find one.

**Solution:** Add search/filter input in components panel.

**Effort:** Low (1 hour)

---

### Multi-Select

**Problem:** Can only select one element at a time.

**Solution:** Shift+click to add to selection, delete/move multiple.

**Effort:** High (4-6 hours)

---

## Completed

1. [x] Accessibility hardening (ARIA, focus-visible)
2. [x] Keyboard interaction (Delete, Escape, arrow nav, Space/Enter)
3. [x] Canvas persistence (localStorage auto-save)
4. [x] UX guardrails (beforeunload, new page confirmation)
5. [x] Modularization documentation (MODULARIZATION.md)

---

## Not Planned

These items are intentionally deferred or out of scope:

- **Framework migration** — Staying vanilla JS for portability
- **Server-side rendering** — File:// compatibility required
- **User accounts / cloud sync** — Out of scope for satellite tool
- **Real-time collaboration** — Out of scope

---

Last updated: Phase 9 of 10-phase stabilization
