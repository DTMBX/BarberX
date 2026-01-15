# Faith Frontier Logo Assets

## SVG crest wordmarks

- `logo-faithfrontier-dark-bg.svg` - default for the navy header/footer. FAITH is locked to pure white (#FFFFFF) for contrast and FRONTIER sits in royal brass.
- `logo-faithfrontier-light-bg.svg` - use on white or parchment backgrounds. FAITH is emerald (#059669) and FRONTIER stays deep ink (#041322).
- `faithfrontier-logo.svg` - maintained as an alias of the dark crest for legacy references in `_config.yml` or partner embeds.
- `faithfrontier-mark.svg` - icon-only Trinitarian crest. Transparent background works on both light and dark surfaces.

Each SVG exposes `--logo-faith-color` and `--logo-frontier-color` custom properties on the ````html`n&lt;svg&gt;`n```` root. Inline the markup if you need to override those values via CSS.

## PNG fallback set

Drop the transparent PNG derivatives of the system into this folder using the exact filenames below so social previews, favicons, and fallbacks resolve cleanly:

- faithfrontier-logo-full-4000.png  (hero/full-width uses, high-resolution rendering)
- faithfrontier-logo-full-2000.png  (primary PNG fallback referenced by headers and includes)
- faithfrontier-logo-full-1500.png  (optional responsive fallback for content blocks)
- faithfrontier-logo-mark-1024.png  (OpenGraph / default social preview image)
- faithfrontier-logo-mark-512.png   (Twitter + Apple touch icon + high-DPI favicon)
- faithfrontier-logo-mark-256.png   (secondary favicon size)
- faithfrontier-logo-mark-128.png   (legacy desktop icon size)
- faithfrontier-logo-mark-64.png    (base favicon referenced by browsers)

All PNGs must remain transparent. No binary placeholders are committed so maintainers can replace them with final artwork without touching templates.
