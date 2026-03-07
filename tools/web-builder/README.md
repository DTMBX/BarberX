# Evident Web Builder

A visual, drag-and-drop website builder that helps you create HTML/CSS pages without writing code from scratch.

## Quick Start

1. **Open the builder**: Double-click `index.html` or open it in Chrome/Edge
2. **Pick a template** (left sidebar → Templates tab) or start dragging components
3. **Click "Open Folder"** to select any project folder on your computer
4. **Build your page** by dragging components to the canvas
5. **Click "Export"** to save `index.html` and `styles.css` to your folder

## Features

### 🧩 Components (Drag & Drop)

| Category | Components |
| --- | --- |
| **Layout** | Section, Container, 2-Column Grid, 3-Column Grid |
| **Content** | Heading, Paragraph, Image, Video, List, Quote |
| **Interactive** | Button, Link, Form, Input |
| **Navigation** | Navbar, Footer |
| **Cards** | Basic Card, Image Card |

### 📄 Templates

- **Landing Page** – Hero, features grid, call-to-action, footer
- **Portfolio** – About section, project gallery, contact
- **Documentation** – Sidebar-friendly content layout
- **Blog Post** – Article with images and blockquotes
- **Blank Page** – Start from scratch

### 📁 Local Folder Access

Works with **any folder** on your computer:

1. Click **Open Folder** → select your project (e.g., `C:\websites\my-site`)
2. The Files tab shows existing HTML, CSS, JS files
3. **Export** writes directly to that folder
4. Push to GitHub → deploy to GitHub Pages

### 👀 Preview & Viewport

- **Desktop / Tablet / Mobile** view buttons
- **Preview** opens your page in a new browser tab
- See generated **HTML** and **CSS** in the right sidebar

## Workflow: Building a GitHub Pages Site

```text
1. Create a folder:         C:\repos\my-portfolio
2. Open folder in builder
3. Select "Portfolio" template
4. Customize by adding/removing components
5. Click Export → index.html + styles.css appear in folder
6. git init + git add . + git commit + git push
7. Enable GitHub Pages in repo Settings
8. Your site is live at https://you.github.io/my-portfolio
```

## Keyboard Shortcuts

| Key                    | Action                            |
| ---------------------- | --------------------------------- |
| `Delete` / `Backspace` | Remove selected element           |
| `Escape`               | Deselect / close modals           |
| `Arrow Left/Right`     | Navigate between tabs             |
| `Space` / `Enter`      | Add focused component to canvas   |
| `Tab`                  | Move focus through UI             |

## Accessibility

- Full keyboard navigation support
- ARIA roles and labels for screen readers
- Focus-visible indicators
- Respects `prefers-reduced-motion`
- Canvas auto-saves to survive browser refresh

## Browser Requirements

- **Chrome 86+** or **Edge 86+** (required for File System Access API)
- Firefox can preview but cannot save to folders directly

## Technical Notes

- **No server required** – runs entirely in the browser
- **File System Access API** – writes directly to your local folders
- **Clean output** – generates semantic HTML5 + modern CSS
- **Mobile-first** – grid layouts include responsive breakpoints

## Learning Path

1. **Start with templates** to see how components work together
2. **Switch to the HTML tab** to see what each component generates
3. **Read the CSS tab** to understand the styles
4. **Experiment** – add/remove components, preview, iterate
5. **Graduate to editing** the exported files by hand

## Folder Structure After Export

```text
your-project/
├── index.html      ← Your page
├── styles.css      ← All component styles
└── (your images, etc.)
```

## Extending the Builder

The builder stores component definitions in the `COMPONENTS` object. To add your own:

```javascript
COMPONENTS['my-feature'] = {
  name: 'My Feature',
  html: `<div class="my-feature">Content here</div>`,
  css: `.my-feature { padding: 20px; background: #f0f0f0; }`,
  editable: ['text', 'background'],
};
```

Then add a button in the sidebar with `data-component="my-feature"`.

---

Built for Evident Technologies – making web development accessible to everyone.
