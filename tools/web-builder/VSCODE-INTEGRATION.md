# VS Code Web Builder Integration

Quick reference for using the Web Builder with VS Code — **no coding required**.

## For Designers (No Code Needed)

### Command Bar — Just Type What You Want

Instead of writing CSS, type natural commands:

| Type This                  | Result                    |
| -------------------------- | ------------------------- |
| `make bigger`              | Increases font size       |
| `make bold`                | Bold text                 |
| `center`                   | Centers the element       |
| `add shadow`               | Adds drop shadow          |
| `round corners`            | Rounds the corners        |
| `add padding`              | Adds spacing inside       |
| `make blue` / `red` / etc. | Changes color             |
| `full width`               | Stretches to full width   |
| `add hover`                | Adds hover animation      |
| `delete`                   | Removes selected element  |

1. Select an element on canvas
2. Type command in the top bar
3. Press Enter or click suggestion

### Visual Style Panel — Click, Don't Code

In the right sidebar, use:

- **Color swatches**: Click a color to apply instantly
- **Typography sliders**: Drag to change size, weight, spacing
- **Spacing sliders**: Adjust padding, margin, border radius
- **Style presets**: One-click themes (Minimal, Bold, Dark, etc.)

### Quick Fix Buttons

Click to instantly apply common fixes:

| Button          | What It Does                        |
| --------------- | ----------------------------------- |
| Center          | Centers content                     |
| Add Shadow      | Professional drop shadow            |
| Round Corners   | Soft rounded edges                  |
| Make Responsive | Works on all screen sizes           |
| Add Padding     | More breathing room                 |
| Fix Contrast    | Better text readability             |
| Full Width      | Stretches across screen             |
| Add Hover       | Interactive hover effect            |

### Accessibility Checker

The Fixes tab shows:

- Accessibility score (A/B/C)
- Issues like missing alt text
- **Auto-fix buttons** to fix problems instantly

### AI/Copilot Integration

Click prompts in the AI tab to generate ready-to-use Copilot commands:

- **Improve Design** — Get design suggestions
- **Add Animations** — Smooth CSS animations
- **Mobile Optimize** — Make it work on phones
- **Fix Accessibility** — WCAG compliance
- **SEO Optimize** — Better search rankings
- **Add Dark Mode** — Toggle for light/dark
- **Explain Code** — Understand what code does

The prompt is copied to clipboard. Paste it in VS Code's Copilot Chat.

---

## Quick Start

Press `Ctrl+Shift+P` → type "Run Task" → select from:

| Task                                | What It Does                      |
| ----------------------------------- | --------------------------------- |
| **Web Builder: Open**               | Launch visual builder in browser  |
| **Web Builder: Open (Live Server)** | Builder with auto-reload          |
| **Web Builder: Preview Site**       | Preview your site at localhost    |
| **Git: Full Deploy**                | Stage + commit + push in one step |

## Keyboard Shortcuts (Recommended)

Add these to your `keybindings.json` (`Ctrl+Shift+P` → "Open Keyboard Shortcuts (JSON)"):

```json
[
  {
    "key": "ctrl+shift+w",
    "command": "workbench.action.tasks.runTask",
    "args": "Web Builder: Open"
  },
  {
    "key": "ctrl+shift+g",
    "command": "workbench.action.tasks.runTask",
    "args": "Git: Full Deploy"
  },
  {
    "key": "ctrl+shift+p",
    "command": "workbench.action.tasks.runTask",
    "args": "Web Builder: Preview Site"
  }
]
```

## HTML Snippets

When editing HTML files, type these prefixes and press `Tab`:

| Prefix            | Inserts                          |
| ----------------- | -------------------------------- |
| `wb-page`         | Complete HTML5 page structure    |
| `wb-navbar`       | Navigation bar                   |
| `wb-hero`         | Hero section with CTA            |
| `wb-section`      | Content section                  |
| `wb-container`    | Centered container               |
| `wb-grid2`        | 2-column responsive grid         |
| `wb-grid3`        | 3-column responsive grid         |
| `wb-heading`      | Styled heading (h1-h6)           |
| `wb-paragraph`    | Styled paragraph                 |
| `wb-button`       | Styled button                    |
| `wb-link`         | Styled link                      |
| `wb-card`         | Card component                   |
| `wb-card-image`   | Card with image                  |
| `wb-form`         | Contact form                     |
| `wb-quote`        | Blockquote                       |
| `wb-list`         | Styled list                      |
| `wb-image`        | Responsive image                 |
| `wb-footer`       | Footer component                 |

## Workflow Options

### Option 1: Visual Builder (No Code)

```text
1. Ctrl+Shift+P → "Run Task" → "Web Builder: Open"
2. Drag components, pick templates
3. Click "Export" → saves HTML/CSS to your folder
4. Ctrl+Shift+P → "Run Task" → "Git: Full Deploy"
```

### Option 2: Code + Snippets (Learning Mode)

```text
1. Create new file: index.html
2. Type wb-page, press Tab → full HTML structure
3. Add wb-navbar, wb-hero, wb-footer
4. Preview with Live Server (Alt+L, Alt+O)
5. Commit with Git: Full Deploy task
```

### Option 3: Hybrid (Best of Both)

```text
1. Start in Web Builder → export basic structure
2. Open exported files in VS Code
3. Use snippets to add more components
4. Refine CSS manually
5. Deploy with Git tasks
```

## Common Tasks

### Open Web Builder

```text
Ctrl+Shift+P → Tasks: Run Task → Web Builder: Open
```

### Preview Your Site

```text
Ctrl+Shift+P → Tasks: Run Task → Web Builder: Preview Site
```

Or use Live Server extension:

```text
Right-click index.html → Open with Live Server
```

### Deploy Changes

```text
Ctrl+Shift+P → Tasks: Run Task → Git: Full Deploy
```

Or step-by-step:

```text
1. Git: Stage All
2. Git: Status (review)
3. Git: Quick Commit
4. Git: Push to Main
```

### Format Your Code

```text
Ctrl+Shift+P → Tasks: Run Task → Format: All Files
```

Or in a single file:

```text
Shift+Alt+F (format document)
```

## Installing Recommended Extensions

When you open this workspace, VS Code may prompt to install recommended extensions. Accept to get:

- **Live Server** - Preview with auto-reload
- **Auto Rename Tag** - Edit tags in pairs
- **CSS Peek** - Jump to CSS from HTML
- **GitLens** - Enhanced Git features
- **Prettier** - Consistent formatting

Or install manually:

```text
Ctrl+Shift+P → Extensions: Show Recommended Extensions
```

## Using with Other Repositories

The Web Builder works with **any folder**. To use it on another repo:

### Method 1: Copy the Builder

```powershell
# Copy builder to another project
Copy-Item -Recurse "C:\path\to\Evident\tools\web-builder" "C:\other-repo\tools\"
```

### Method 2: Open Builder from Any Location

1. Open Web Builder in browser
2. Click "Open Folder" → navigate to any repo
3. Build and export there

### Method 3: Create a Global Shortcut

Create `C:\tools\open-web-builder.bat`:

```batch
@echo off
start "" "C:\path\to\Evident\tools\web-builder\index.html"
```

Then run it from anywhere.

## File Structure After Export

```text
your-project/
├── index.html      ← Your page
├── styles.css      ← Component styles
├── deploy.bat      ← One-click deploy (Windows)
├── deploy.ps1      ← One-click deploy (PowerShell)
└── assets/         ← Your images (add manually)
```

## Customizing Components

Edit web-builder/index.html to add your own components:

1. Find the `COMPONENTS` object in the JavaScript
2. Add your component definition
3. Add a button in the sidebar

Example:

```javascript
COMPONENTS['my-banner'] = {
  name: 'My Banner',
  html: `<div class="my-banner">Your custom HTML</div>`,
  css: `.my-banner { background: #f00; padding: 20px; }`,
  editable: ['text', 'background'],
};
```

## Troubleshooting

### "Open Folder" doesn't work

Use Chrome or Edge. Firefox doesn't support the File System Access API.

### Git push fails

```text
1. Check if remote is configured: git remote -v
2. If not: git remote add origin https://github.com/user/repo.git
3. Try again: git push -u origin main
```

### Live Server doesn't start

Install it globally:

```powershell
npm install -g live-server
```

### Snippets don't appear

1. Make sure file is saved as `.html`
2. Check language mode (bottom-right) says "HTML"
3. Restart VS Code if needed

## Tips for Beginners

1. **Start with templates** - Don't start from scratch
2. **Use the Git tab** - Copy commands one at a time to learn
3. **Preview often** - Use Live Server to see changes instantly
4. **Read the generated code** - Switch to HTML/CSS tabs to learn
5. **Format your code** - Run "Format: All Files" regularly
6. **Commit frequently** - Small commits are easier to manage

## Getting Help

- **Element Inspector**: [tools/element-inspector.html](../element-inspector.html) — Learn CSS selectors
- **Web Builder**: [tools/web-builder/index.html](index.html) — Visual builder
- **Builder README**: [tools/web-builder/README.md](README.md) — Full documentation
