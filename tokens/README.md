# Evident Ecosystem — Foundation Tokens

Design tokens for the Evident Technologies ecosystem. Each product family has
its own token file. Tokens define the visual contract that keeps products within
a family recognizable without forcing identical UI.

## Files

| File | Family | Prefix | Applies To |
| --- | --- | --- | --- |
| `evident.foundation.css` | Evident | `--ev-` | Main suite, companions (DOJ Library, Civics, ICC, EGL, Founder-Hub) |
| `tillerstead.foundation.css` | Tillerstead | `--ts-` | Tillerstead, toolkit, Contractor Command, Sweat Equity |

## Usage

### Static HTML / Jekyll

```html
<link rel="stylesheet" href="/path/to/evident.foundation.css">
```

### Vite / React

```js
import './tokens/evident.foundation.css';
```

### Tailwind (reference tokens in config)

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'var(--ev-color-primary)',
        accent: 'var(--ev-color-accent)',
      }
    }
  }
};
```

## Token Categories

Each foundation file defines these categories:

- **Color** — Brand palette and semantic colors (success, warning, danger, info)
- **Background** — Surface and elevation colors
- **Text** — Text color hierarchy for dark and light surfaces
- **Font** — Font family stacks (sans, serif/display, mono)
- **Size** — Type scale
- **Spacing** — Margin and padding scale
- **Radius** — Border radius
- **Shadow** — Elevation and focus shadows
- **Duration** — Animation timing (zeroed under `prefers-reduced-motion`)
- **Ease** — Easing functions
- **Z-Index** — Stacking order

## Naming Convention

```text
--{brand}-{category}-{variant}
```

- `{brand}` — `ev` for Evident, `ts` for Tillerstead
- `{category}` — One of the categories above
- `{variant}` — Specific value (e.g., `primary`, `sm`, `ink`)

## Extending Tokens

A satellite product may add its own tokens with its own prefix on top of the
family foundation. For example, the DOJ Document Library could add:

```css
--doj-color-highlight: #fcd34d;
```

Do not redefine foundation token values. If a value needs to change, it goes
through a review of the foundation file.

## Accessibility

Both files include `*-accessible` variants for primary and accent colors that
meet WCAG AA contrast requirements. Both files zero out animation durations
under `prefers-reduced-motion: reduce`.

## Version

v1.0 — Initial foundation tokens derived from existing per-repo token files.

See `docs/architecture/CROSS-REPO-CONSISTENCY.md` for the full consistency
strategy.
