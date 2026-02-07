# Migration to Eleventy + Tailwind

Quick start (Windows):

1. Install dev dependencies:

```powershell
npm install
```

2. Start dev server (builds CSS then serves Eleventy):

```powershell
npm run dev
```

3. Build for production:

```powershell
npm run build
```

Notes:

- This repository has been scaffolded with Eleventy (`@11ty/eleventy`) and
  Tailwind CSS.
- CSS entry: `src/assets/css/tailwind.css` compiled to
  `_site/assets/css/styles.css`.
- Templates live in `src/` (Nunjucks). Layouts in `src/_includes/layouts/`.
- Next steps: move content from existing Jekyll `_*` folders into `src/` and
  convert Liquid → Nunjucks includes.
