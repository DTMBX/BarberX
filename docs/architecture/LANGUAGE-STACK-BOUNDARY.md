# Language / Stack Boundary

> Step 11 of the Evident Ecosystem Architecture Series
>
> Principle: **Support what you can verify. Label what you cannot. Never pretend
> to parse what you only recognize.**

---

## 0. Problem Statement

The Evident ecosystem spans seven distinct technology stacks:

| Stack | Where Used | File Types |
| --- | --- | --- |
| HTML / CSS / JS | Evident site, Tillerstead, Sweat Equity Insurance, Web Builder output | `.html`, `.css`, `.js` |
| TypeScript + React + Vite | Founder-Hub, 4 monorepo apps, CCC, ICC, DOJ Library | `.tsx`, `.ts`, `.css`, `.json` |
| Python + FastAPI | Evident backend, BWC backend, tillerstead-toolkit, AI pipeline | `.py`, `.toml`, `.txt`, `.yml` |
| Jekyll + Liquid | Tillerstead production site | `.html`, `.md`, `.yml`, `.liquid` |
| 11ty + Nunjucks | Evident marketing site | `.html`, `.njk`, `.md`, `.yml` |
| .NET / MAUI | Evident gateway + mobile | `.cs`, `.csproj`, `.slnx`, `.xaml` |
| PowerShell / Shell | Build scripts, automation, CLI tools | `.ps1`, `.sh`, `.bat` |

The web-builder currently produces **one output format**: semantic HTML + vanilla
CSS. It has no code generation, no framework transpilation, and no language
parser. This is correct. The builder is a visual layout tool, not an IDE.

The question is not "how do we make the builder generate React." The question is:
**what should the builder know about each stack, and what should it do with that
knowledge?**

---

## 1. Support Tiers

Every language and stack in the ecosystem is assigned to one of four tiers based
on what the builder can safely do with it.

### Tier 1 — Native (builder generates, validates, and exports)

The builder produces correct, production-ready output in these formats. It owns
the generation pipeline end to end.

| Format | Capability | Current Status |
| --- | --- | --- |
| **HTML5** | Generate semantic markup. Validate structure. Export as file. | Implemented |
| **CSS** | Generate stylesheets. Export linked or embedded. | Implemented |
| **JSON** (config/data) | Generate manifests, registry exports, `theme.json`. Validate against schema. | Implemented (registry + manifest) |

**What "native" means:**

- The builder can create these files from scratch.
- The builder can validate them before export.
- The builder can overwrite them with confidence.
- No external tool is required to complete the file.

### Tier 2 — Aware (builder reads, routes, and adapts export behavior)

The builder understands the structure of these stacks well enough to adjust its
behavior — choosing the right export path, suggesting the right filenames,
warning about integration requirements — but does not generate framework code.

| Stack | What the Builder Knows | What It Does |
| --- | --- | --- |
| **React + Vite** | Project uses `.tsx` components, `src/components/` convention, Tailwind classes, Radix UI patterns. | Exports HTML snippet formatted for JSX conversion. Suggests `className` instead of `class`. Warns about event handler syntax. Appends integration notes. |
| **11ty + Nunjucks** | Project uses `_includes/`, `_layouts/`, front-matter, Nunjucks `{% block %}`. | Exports HTML partial with front-matter header. Suggests layout reference. Warns about template inheritance. |
| **Jekyll + Liquid** | Project uses `_includes/`, `_layouts/`, front-matter, Liquid `{% include %}`. | Exports HTML partial with YAML front-matter. Suggests `_includes/` as target directory. |
| **Tailwind CSS** | Utility-class-driven styling. `@apply` directive. Token-based design. | Translates CSS custom properties to Tailwind utility class suggestions in export notes. |

**What "aware" means:**

- The builder recognizes the stack from the manifest or registry.
- It adjusts filenames, paths, and integration guidance.
- It does NOT generate `.tsx`, `.njk`, `.liquid`, or any framework-native code.
- The output is still HTML/CSS, but shaped to ease manual integration.

### Tier 3 — Prompt-Assisted (builder provides AI prompts, not code)

The builder cannot generate or validate these formats, but it can hand off to an
AI assistant with the right context. The builder's role is to assemble a precise,
copy-ready prompt that includes the current canvas state, the target repo's
manifest data, and the conversion instructions.

| Stack | Prompt the Builder Assembles |
| --- | --- |
| **Python + FastAPI** | "Convert this HTML form into a FastAPI endpoint with Pydantic model. Target repo: {name}, stack: {stack}. Fields: {extracted form fields}. Return a `routes/` module." |
| **TypeScript (non-React)** | "Convert this HTML component into a TypeScript module with typed props. Target repo: {name}. Props: {extracted attributes}." |
| **PowerShell** | "Generate a PowerShell script that scaffolds this HTML structure as files in {target path}. Include: {filenames}, {directory structure}." |
| **.NET / MAUI** | "Convert this HTML layout into a .NET MAUI XAML page. Target: {manifest.name}. Layout: {grid/flex structure}." |

**What "prompt-assisted" means:**

- The builder does not produce the target format.
- It produces a structured prompt that an external AI agent can execute.
- The prompt includes canvas context, manifest metadata, and conversion rules.
- The user copies the prompt into Copilot, ChatGPT, or another agent.

### Tier 4 — Inert (builder stores metadata, does nothing else)

The builder knows these formats exist because they appear in manifests and
registries. It displays the information but takes no action on them.

| Format | Builder Behavior |
| --- | --- |
| **YAML** (workflows, CI) | Displays in registry. No generation. No validation. |
| **TOML** (pyproject, config) | Displays in registry. No generation. |
| **Docker** (Dockerfile, compose) | Displays in registry. No generation. |
| **Ruby** (Gemfile) | Displays in registry. No generation. |
| **SQL** (migrations) | Displays in registry. No generation. |
| **Shell scripts** (`.sh`) | Displays in registry. No generation. |
| **C#** (`.cs`, `.csproj`) | Displays in registry. No generation. |
| **XAML** (MAUI layouts) | Displays in registry. No generation. |

**What "inert" means:**

- The builder stores the stack name in the registry.
- It may display an icon or label for the stack.
- It performs no generation, validation, or export for these formats.
- No false promises. No broken tools.

---

## 2. What the Builder Should Support Now

These capabilities exist today or require only small additions to the existing
codebase.

### 2.1 Already Implemented

| Capability | Status |
| --- | --- |
| HTML5 generation (drag-drop components) | Working |
| CSS generation (properties panel) | Working |
| Five export modes (full page, snippet, HTML-only, CSS-only, clipboard) | Working |
| Multi-repo export targeting | Working |
| Workspace registry with stack metadata | Working |
| Manifest auto-detection (`.evident-repo.json`) | Working |
| File System Access API (direct folder write) | Working |
| Export preflight checklist | Working |

### 2.2 Small Additions (Tier 1 completions)

| Addition | Effort | Value |
| --- | --- | --- |
| **Markdown export mode** | Low | Export canvas as `.md` with HTML preserved or converted to Markdown headings/lists. Useful for docs repos. |
| **JSON schema validation on export** | Low | Validate generated `theme.json` or config files against their schemas before writing. |
| **CSS custom property export** | Low | Export only the `--ev-*` or `--ts-*` variables used on the canvas as a standalone token file. |

### 2.3 Tier 2 Stack-Aware Routing

The builder already stores `stack` in the registry. It should use that field to
adjust export behavior.

**Implementation: Export Profile Stack Presets**

When a target repo's manifest declares `stack: "React 19 + TypeScript"`, the
export system should:

1. Default to **Snippet** mode (not Full Page).
2. Append a comment block to the exported HTML:

```html
<!-- Integration: React + Vite project
     Convert class="" to className=""
     Move inline styles to Tailwind utilities
     Wrap in a functional component
     Import into src/components/ -->
```

3. Offer a "Copy as JSX" button that performs mechanical transforms:
   - `class` → `className`
   - `for` → `htmlFor`
   - Self-close void elements (`<img>` → `<img />`)
   - Escape `{}` in text content

This is string replacement, not framework code generation. Safe for the builder
to own.

**Stack preset map:**

| Manifest Stack | Export Default | Comment Block | Mechanical Transform |
| --- | --- | --- | --- |
| Contains "React" | Snippet | JSX integration notes | `class` → `className`, self-close voids |
| Contains "11ty" or "Nunjucks" | Snippet | Front-matter + layout reference | Prepend `---\nlayout: base\n---` |
| Contains "Jekyll" or "Liquid" | Snippet | Front-matter + include path | Prepend `---\nlayout: default\n---` |
| Contains "FastAPI" or "Python" | HTML-only | "This is a UI mockup" disclaimer | None |
| Contains "MAUI" or ".NET" | Clipboard | "Convert to XAML" note | None |
| No stack / unknown | Full Page | None | None |

---

## 3. What Should Be Prompt-Assisted Only

These capabilities exceed the builder's generation ability but can be bridged by
assembling structured prompts from canvas + manifest context.

### 3.1 Prompt Assembly Engine

The builder's existing AI Copilot panel (52 prompts, 11 categories) is the right
home for this. Add a new category: **Stack Conversion**.

**Prompt template structure:**

```text
Convert the following HTML/CSS to {targetFormat}.

Target repository: {manifest.name}
Stack: {manifest.stack}
Output type: {manifest.outputType}
Token family: {manifest.tokenFamily}

Source HTML:
{canvasHTML}

Source CSS:
{canvasCSS}

Requirements:
- {stack-specific rules}
- Preserve semantic structure
- Use project conventions from the target stack
- Do not invent functionality not present in the source
```

**Stack-specific prompt templates:**

| Target | Template ID | Key Rules Injected |
| --- | --- | --- |
| React + TypeScript | `convert-react` | "Return a functional component. Use `className`. Type all props. Use Tailwind utilities where CSS maps to them." |
| FastAPI endpoint | `convert-fastapi` | "Extract form fields as a Pydantic BaseModel. Create a POST route. Include input validation. Return JSON." |
| 11ty partial | `convert-11ty` | "Wrap in Nunjucks block syntax. Add front-matter. Reference `_includes/` layout." |
| Jekyll include | `convert-jekyll` | "Wrap in Liquid syntax. Add YAML front-matter. Use `{% include %}` for shared fragments." |
| PowerShell scaffold | `convert-ps1` | "Generate a PowerShell script that creates this file structure. Use `New-Item` for files. Set UTF-8 encoding." |
| .NET MAUI XAML | `convert-maui` | "Convert HTML grid/flex to MAUI Grid/StackLayout. Map CSS properties to XAML attributes. Use MVVM binding placeholders." |
| Markdown | `convert-md` | "Convert headings to `#` syntax. Convert lists to `-` syntax. Preserve code blocks. Strip presentational HTML." |

### 3.2 When to Offer Prompts

The prompt button appears in the export panel when:

1. The target repo's stack does not match Tier 1 (HTML/CSS/JSON).
2. The user has canvas content to convert.
3. The manifest is loaded (so context is available).

If the manifest is not loaded, the prompt uses only the registry's `stack`
field with a note: "Manifest not detected — verify stack before executing."

---

## 4. What Should Wait for a Future Tool

These capabilities require infrastructure, parsing, or runtime that the builder
cannot safely provide today. They belong in dedicated tools, not in the
single-file web-builder.

### 4.1 Deferred Capabilities

| Capability | Why It Waits | Prerequisite |
| --- | --- | --- |
| **TypeScript/JSX transpilation** | Requires a bundler (esbuild, SWC, tsc). Cannot run in a single HTML file without loading a WASM compiler. | Modularized builder with npm build step (see REFACTOR-ROADMAP.md). |
| **Python code generation** | Requires AST awareness, import resolution, and framework convention enforcement. A visual builder cannot guarantee correct Python. | Dedicated backend scaffold tool or Copilot agent. |
| **YAML workflow generation** | GitHub Actions workflows require schema-aware validation, secret reference checking, and runner compatibility. Too complex for a canvas tool. | CI/CD configuration tool (separate). |
| **Database schema / ORM generation** | Requires model relationship awareness, migration planning, and dialect selection. | Backend-specific tool or Copilot agent. |
| **Live preview of non-HTML stacks** | Rendering React/MAUI/Jekyll requires their respective build tools running locally. The builder cannot start these processes. | Dev server integration (external). |
| **Multi-file project scaffolding** | Generating a complete project (package.json + tsconfig + vite.config + src/) requires template engine + file tree generation. Beyond a canvas tool. | Dedicated scaffold CLI (`evident init`). |
| **Diff-aware import** | Reading an existing `.tsx` file and rendering it on the canvas requires a JSX parser. | Modularized builder or external parse service. |

### 4.2 Future Tool Candidates

| Tool | Scope | Stack | Ships With |
| --- | --- | --- | --- |
| `evident init` (CLI scaffold) | Generate new project from template. Reads manifest. Creates file tree. | Node.js CLI | Phase 2 of builder modularization |
| Backend Scaffold Agent | Generate FastAPI routes, models, and tests from a spec or form definition. | Python + Copilot agent | When backend API surface stabilizes |
| Workflow Builder | Visual editor for GitHub Actions YAML. | Dedicated tool (not web-builder) | When CI/CD patterns are standardized |
| Component Sync | Import `.tsx` components into the canvas for visual editing, then export back. | Requires JSX parser (SWC WASM) | After builder modularization |

---

## 5. Honest Stack Labeling in the UI

The builder must never imply capability it does not have. Stack support is
labeled in three places.

### 5.1 Registry Item Display

When a repo is shown in the registry panel, its stack appears with a **support
badge**:

| Badge | Meaning | Visual |
| --- | --- | --- |
| **Native** | Builder generates this stack directly. | Green dot + "Native" |
| **Aware** | Builder adapts export for this stack. | Blue dot + "Aware" |
| **Prompt** | Builder assembles AI prompts for this stack. | Amber dot + "Prompt" |
| **Metadata** | Builder stores info only. | Gray dot + "Metadata" |

**Badge assignment logic** (derived from manifest `stack` field):

```text
if stack contains "HTML" or "CSS" or outputType is "static-site" → Native
if stack contains "React" or "11ty" or "Jekyll" or "Tailwind"   → Aware
if stack contains "FastAPI" or "Python" or "PowerShell" or ".NET" → Prompt
else                                                              → Metadata
```

### 5.2 Export Panel

When the user selects a target repo for export, the panel shows a **stack
compatibility notice**:

| Tier | Notice Text |
| --- | --- |
| Native | "Full export. Output is ready to use." |
| Aware | "HTML/CSS export with {stack} integration notes. Manual conversion needed." |
| Prompt | "HTML/CSS export only. Use the AI prompt to convert to {stack}." |
| Metadata | "This repo uses {stack}. The builder cannot generate files for this stack." |

### 5.3 AI Copilot Panel

When stack conversion prompts are available (Tier 3), the prompt category header
shows:

> **Stack Conversion** — The builder generated HTML/CSS. These prompts help you
> convert the output to your target stack. Copy the prompt into your AI assistant.

No claim of automatic conversion. No hidden generation. The user sees exactly
what is happening.

---

## 6. Manifest Schema Extension

Add a `stackTier` field to the manifest schema. This field is **computed by the
builder** (not set by the user) based on the `stack` field. It exists so that
export logic can branch on a single enum instead of string-matching.

```json
"stackTier": {
  "type": "string",
  "enum": ["native", "aware", "prompt", "metadata"],
  "description": "Builder support tier for this repo's stack. Computed from the stack field. native = builder generates directly. aware = builder adapts export. prompt = builder assembles AI prompts. metadata = builder stores info only."
}
```

This field is written by the builder when it loads a manifest. It is not a user
input. It is a derived classification.

---

## 7. Stack Detection Rules

When the builder loads a manifest or registry item, it classifies the stack
using this precedence:

```text
1. If manifest.outputType is "static-site" or "docs"
   AND stack is empty or contains only "HTML", "CSS", "JS"
   → Tier 1 (Native)

2. If stack contains "React" or "Vue" or "Svelte" or "Angular"
   → Tier 2 (Aware)

3. If stack contains "11ty" or "Eleventy" or "Nunjucks"
   → Tier 2 (Aware)

4. If stack contains "Jekyll" or "Liquid" or "Hugo"
   → Tier 2 (Aware)

5. If stack contains "Tailwind"
   AND no framework detected in steps 2-4
   → Tier 2 (Aware)

6. If stack contains "Python" or "FastAPI" or "Flask" or "Django"
   → Tier 3 (Prompt)

7. If stack contains "PowerShell" or ".NET" or "MAUI" or "C#"
   → Tier 3 (Prompt)

8. If stack contains "TypeScript" AND no framework detected
   → Tier 3 (Prompt)

9. Else → Tier 4 (Metadata)
```

If the manifest is missing and only the registry `stack` string is available,
the same rules apply. If both are missing, default to Tier 4.

---

## 8. Ecosystem Stack Map

Current classification of every repo in the ecosystem:

| Repo | Stack | Output Type | Tier | Builder Behavior |
| --- | --- | --- | --- | --- |
| **Evident** (site layer) | 11ty + Nunjucks + Tailwind | static-site | Aware | Snippet export with front-matter |
| **Evident** (backend) | Python + FastAPI | api | Prompt | AI prompt assembly |
| **Evident** (BWC frontend) | Next.js + React | web-app | Aware | JSX-ready snippet export |
| **Evident** (AI pipeline) | Python | library | Prompt | AI prompt assembly |
| **Evident** (apps/*) | React 19 + TypeScript + Vite | web-app | Aware | JSX-ready snippet export |
| **Founder-Hub** | React 19 + TypeScript + Vite | web-app | Aware | JSX-ready snippet export |
| **Tillerstead** | Jekyll + Liquid + Tailwind | static-site | Aware | Front-matter snippet export |
| **tillerstead-toolkit** | Python + FastAPI | api | Prompt | AI prompt assembly |
| **Contractor Command Center** | React + TypeScript + Vite | pwa | Aware | JSX-ready snippet export |
| **Informed Consent Companion** | React + TypeScript + Vite | web-app | Aware | JSX-ready snippet export |
| **DOJ Document Library** | React + TypeScript + Vite | web-app | Aware | JSX-ready snippet export |
| **Essential Goods Ledger** | React + TypeScript + Vite | web-app | Aware | JSX-ready snippet export |
| **Geneva Bible Study** | React + TypeScript + Vite | pwa | Aware | JSX-ready snippet export |
| **Sweat Equity Insurance** | HTML + CSS + JS | static-site | Native | Full export, ready to use |
| **Web Builder** (itself) | HTML + CSS + JS | scripts | Native | Self-referential |

---

## 9. Implementation Priority

| Phase | What | Tier | Effort |
| --- | --- | --- | --- |
| **Now** | Add stack tier badges to registry display | UI | Low |
| **Now** | Add stack compatibility notice to export panel | UI | Low |
| **Now** | Add "Copy as JSX" mechanical transform | Aware | Low |
| **Now** | Add front-matter prepend for Jekyll/11ty targets | Aware | Low |
| **Next** | Add Stack Conversion prompt category to Copilot panel | Prompt | Medium |
| **Next** | Add Markdown export mode | Native | Low |
| **Next** | Add CSS token extraction export | Native | Low |
| **Next** | Add `stackTier` to manifest schema | Schema | Low |
| **Later** | `evident init` CLI scaffold tool | Future | High |
| **Later** | Component Sync (JSX parser) | Future | High |
| **Later** | Backend Scaffold Agent | Future | High |

---

## 10. Governance

### What Moves Between Tiers

A stack can be promoted from a lower tier to a higher tier when:

1. The builder can generate **correct, valid output** in that format.
2. The output has been tested against at least one real repo in the ecosystem.
3. The generation does not require loading external runtimes (bundlers, parsers,
   compilers) into the single-file builder.

A stack is demoted if:

1. The builder's output for that stack produces errors in target repos.
2. The stack's conventions change faster than the builder can track them.
3. Users report that the builder's output creates more work than manual creation.

### The Single-File Constraint

The web-builder is a single HTML file that runs from `file://`. This is a
feature, not a limitation. It means:

- No Node.js required to run.
- No server required.
- No build step required.
- Portable to any machine with Chrome or Edge.

Any stack support that would require violating this constraint belongs in a
**separate tool**, not in the builder. The builder's scope ends where the
bundler begins.

---

*This document defines the boundary between what the builder does, what it
assists with, and what it leaves to other tools. It does not expand the builder's
scope. It names the scope precisely.*
