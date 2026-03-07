# Web Builder — Modularization Roadmap

This document maps the logical sections in `index.html` for future extraction into
separate files. The monolith is functional but can be split as complexity grows.

---

## Current Structure (Single-File)

| Section | Lines (approx) | Description | Extraction Priority |
| ------- | -------------- | ----------- | ------------------- |
| **CSS: Variables** | 8-65 | Design tokens, color palette | MEDIUM — `tokens.css` |
| **CSS: Reset** | 48-65 | Base reset styles | LOW — common pattern |
| **CSS: Layout** | 67-140 | Header, sidebar, main grid | MEDIUM — `layout.css` |
| **CSS: Components** | 143-700 | Tabs, buttons, cards, etc. | HIGH — `components.css` |
| **CSS: Canvas** | 700-880 | Builder canvas, elements | HIGH — `canvas.css` |
| **CSS: Copilot UI** | 1080-1186 | Prompt cards, categories | MEDIUM — `copilot.css` |
| **HTML: Header** | 1189-1244 | App header, toolbar | LOW — static |
| **HTML: Sidebar** | 1244-2170 | Components, templates, Copilot | MEDIUM — could be web components |
| **HTML: Main Canvas** | 2170-2200 | Canvas area | LOW — simple |
| **HTML: Modal** | 2172-2200 | New page modal | LOW — simple |
| **JS: State** | 2215-2260 | State object, persistence | HIGH — `state.js` |
| **JS: Components** | 2262-2420 | COMPONENTS definitions | HIGH — `components.js` |
| **JS: Canvas Render** | 2454-2565 | renderCanvas, select, delete | HIGH — `canvas.js` |
| **JS: Code View** | 2565-2700 | updateCodeView, export | MEDIUM — `export.js` |
| **JS: Drag & Drop** | 2700-2780 | Drag/drop handlers | MEDIUM — `dnd.js` |
| **JS: File System** | 2780-2930 | File System Access API | HIGH — `filesystem.js` |
| **JS: Copilot Prompts** | 3625-4140 | COPILOT_PROMPTS registry | HIGH — `prompts.js` |
| **JS: Copilot UI** | 4143-4550 | Categories, history, UI | MEDIUM — `copilot-ui.js` |
| **JS: Command Bar** | 4550-5100 | Natural language parsing | MEDIUM — `commands.js` |
| **JS: Style Presets** | 5000-5070 | Quick style buttons | LOW — simple |
| **JS: Init** | 5150-5170 | Initialization | LOW — glue code |

---

## Extraction Phases (Future)

### Phase A: CSS Separation

Extract CSS into external files while keeping JS inline. Simplest first step.

```text
index.html (HTML + JS)
├── css/tokens.css
├── css/layout.css
├── css/components.css
├── css/canvas.css
└── css/copilot.css
```

### Phase B: JS Modules (ESM)

Split JavaScript into ES modules. Requires bundler or native ESM.

```text
index.html (HTML only)
├── js/state.js
├── js/components.js
├── js/canvas.js
├── js/export.js
├── js/filesystem.js
├── js/prompts.js
├── js/copilot-ui.js
├── js/commands.js
└── js/main.js (orchestrator)
```

### Phase C: Web Components

Convert sidebar sections into custom elements for encapsulation.

```html
<wb-sidebar>
  <wb-component-palette></wb-component-palette>
  <wb-template-library></wb-template-library>
  <wb-copilot-panel></wb-copilot-panel>
</wb-sidebar>
```

---

## Constraints

1. **Portability First** — Must still work from `file://` without build step
2. **No Frameworks** — Vanilla JS only (no React, Vue, etc.)
3. **Single-File Option** — Keep a bundled version for simple deployment
4. **Backward Compatible** — Existing localStorage data must survive

---

## Status

- [x] Sections marked with `═══` comments
- [x] Logical boundaries identified
- [ ] CSS extraction (future)
- [ ] JS module extraction (future)
- [ ] Web component conversion (future)

---

Last updated: Phase 7 of 10-phase stabilization
