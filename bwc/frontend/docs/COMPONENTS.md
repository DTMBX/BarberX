# Evident BWC — Component Library Reference

> Canonical list of UI components, usage rules, and implementation patterns.
> Every page must use these components — no raw unstyled HTML elements.

---

## 1. Design Tokens

### Color Palette (Dark Theme)

| Token              | Tailwind           | Usage                    |
| ------------------ | ------------------ | ------------------------ |
| `bg-primary`       | `bg-slate-900`     | Page background          |
| `bg-surface`       | `bg-slate-800`     | Cards, panels, modals    |
| `bg-surface-hover` | `bg-slate-700`     | Hover states on surfaces |
| `border-default`   | `border-slate-700` | Card/table borders       |
| `border-focus`     | `ring-blue-500`    | Focus rings (2px)        |
| `text-primary`     | `text-white`       | Headings                 |
| `text-secondary`   | `text-slate-300`   | Body text                |
| `text-muted`       | `text-slate-400`   | Labels, helper text      |
| `text-dim`         | `text-slate-500`   | Timestamps, metadata     |

### Status Colors

| State    | Badge Class                          | Usage                       |
| -------- | ------------------------------------ | --------------------------- |
| Verified | `bg-emerald-900/30 text-emerald-400` | SHA-256 verified evidence   |
| Pending  | `bg-yellow-900/30 text-yellow-400`   | Awaiting verification       |
| Tampered | `bg-red-900/30 text-red-400`         | HMAC invalid, hash mismatch |
| Success  | `bg-emerald-900/30 text-emerald-400` | Action completed            |
| Warning  | `bg-yellow-900/30 text-yellow-400`   | Non-critical issues         |
| Error    | `bg-red-900/30 text-red-400`         | Failures                    |
| Info     | `bg-blue-900/30 text-blue-400`       | Informational               |

### Typography Scale

| Element         | Classes                              |
| --------------- | ------------------------------------ |
| Page title      | `text-2xl font-bold`                 |
| Section heading | `text-xl font-semibold`              |
| Card title      | `text-sm font-semibold`              |
| Body            | `text-sm text-slate-300`             |
| Label           | `text-sm font-medium text-slate-400` |
| Helper text     | `text-xs text-slate-500`             |
| Monospace       | `font-mono text-xs`                  |

### Spacing Rhythm

- Page sections: `space-y-8`
- Card content: `p-4` or `p-6`
- Form fields: `space-y-4`
- Inline gaps: `gap-2` (tight), `gap-4` (default), `gap-6` (loose)

---

## 2. Component Catalog

### Button (`components/ui/button.tsx`)

Variants: `primary` | `secondary` | `destructive` | `ghost` | `link` Sizes: `sm`
| `md` | `lg`

```tsx
<Button variant="primary" size="md" loading={saving}>Save Case</Button>
<Button variant="destructive" size="sm" icon={<Trash2 />}>Delete</Button>
<Button variant="ghost" size="sm">Cancel</Button>
```

Rules:

- Every clickable action must use `<Button>`, never raw `<button>`
- Primary actions: 1 per visible section max
- Destructive actions require confirmation via `<ConfirmDialog>`
- `loading` prop disables button and shows spinner
- All buttons have `focus-visible:ring-2` for keyboard users

### Input (`components/ui/input.tsx`)

```tsx
<Input
  label="Case Title"
  required
  error="Title is required"
  placeholder="Enter case title"
/>
```

Rules:

- Every input has a visible `<label>` (not placeholder-only)
- Error text rendered below with `text-red-400 text-xs`
- Helper text below label with `text-slate-500 text-xs`

### Textarea (`components/ui/textarea.tsx`)

Same pattern as Input, with `rows` prop. Used for narratives, descriptions.

### Select (`components/ui/select.tsx`)

Native `<select>` with consistent dark styling. For complex selections, use a
custom dropdown.

### Badge (`components/ui/badge.tsx`)

```tsx
<Badge variant="verified">Verified</Badge>
<Badge variant="pending">Pending</Badge>
<Badge variant="error">Tampered</Badge>
<Badge variant="info">OCR</Badge>
```

Rules:

- Use for status indicators, tags, and labels
- Never clickable (use Button for actions)
- Variants map to the status color tokens above

### Card (`components/ui/card.tsx`)

```tsx
<Card>
  <CardHeader
    title="Evidence Files"
    action={<Button size="sm">Upload</Button>}
  />
  <CardContent>...</CardContent>
</Card>
```

Rules:

- All content sections wrapped in Card
- `CardHeader` includes optional action slot

### EmptyState (`components/ui/empty-state.tsx`)

```tsx
<EmptyState
  icon={<FileSearch />}
  title="No evidence yet"
  description="Upload files to get started"
  action={<Button>Upload Evidence</Button>}
/>
```

Rules:

- Every list/table must show an EmptyState when data is empty
- Icon + title + description + optional action button

### DataTable (`components/ui/data-table.tsx`)

```tsx
<DataTable
  columns={columns}
  data={evidence}
  loading={isLoading}
  emptyMessage="No evidence files"
/>
```

Rules:

- All tables use `<DataTable>` wrapper
- Built-in loading skeleton, empty state, and error state
- Sortable columns via header click
- Responsive: horizontal scroll on mobile

### PageHeader (`components/ui/page-header.tsx`)

```tsx
<PageHeader
  title="Case Detail"
  breadcrumbs={[
    { label: 'Cases', href: '/cases' },
    { label: 'Smith v. State' },
  ]}
  actions={<Button>Export</Button>}
/>
```

Rules:

- Every page starts with `<PageHeader>`
- Breadcrumbs for navigation context
- Optional actions slot (right-aligned)

### Tabs (`components/ui/tabs.tsx`)

```tsx
<Tabs value={activeTab} onChange={setActiveTab} tabs={[{ id: 'evidence', label: 'Evidence', count: 5 }, ...]} />
```

Rules:

- Keyboard navigable (arrow keys)
- Active tab has bottom border indicator
- Optional count badge per tab

### ConfirmDialog (`components/ui/confirm-dialog.tsx`)

```tsx
<ConfirmDialog
  open={showDelete}
  title="Delete Issue"
  description="This action cannot be undone."
  confirmLabel="Delete"
  variant="destructive"
  onConfirm={handleDelete}
  onCancel={() => setShowDelete(false)}
/>
```

Rules:

- All destructive actions must be confirmed
- Focus trap when open
- Escape key dismisses

### Skeleton loaders (`components/ui/loading.tsx`)

Pre-existing: `Skeleton`, `SkeletonText`, `SkeletonCard`, `SkeletonTable`

Rules:

- Every page transition shows skeletons, not blank content
- Match layout shape of real content

### Toast (`components/ui/toast.tsx`)

Pre-existing with types: `success` | `error` | `warning` | `info`

Rules:

- Success/info: auto-dismiss 5s
- Error: auto-dismiss 8s
- Warning (forensic): NEVER auto-dismiss — user must dismiss

### ErrorBoundary (`components/ui/error-boundary.tsx`)

Pre-existing. Wraps entire app via `<Providers>`.

---

## 3. Data Fetching Pattern

### Architecture

```
lib/api.ts          → Raw fetch wrapper (typed request/response)
lib/queryKeys.ts    → Centralized cache key factory
lib/hooks/*.ts      → React Query hooks (useCase, useEvidence, etc.)
components/         → Consume hooks, show loading/error/data states
```

### Rules

1. All API calls go through `lib/api.ts` — never raw `fetch()` in components
2. All React Query keys defined in `lib/queryKeys.ts`
3. Hooks wrap `useQuery` / `useMutation` with proper error handling
4. Mutations invalidate related queries on success
5. Upload operations do NOT use React Query (custom state machine)
6. CourtListener searches use React Query with 5-minute stale time

---

## 4. Accessibility Checklist

- [ ] Every form input has a visible label
- [ ] All interactive elements reachable by keyboard (Tab / Shift+Tab)
- [ ] Focus ring visible on all focusable elements
      (`focus-visible:ring-2 ring-blue-500`)
- [ ] Color is not the only indicator (icons/text accompany status colors)
- [ ] Modal/dialog has focus trap and Escape dismiss
- [ ] Tables have `<th scope="col">` headers
- [ ] Buttons have descriptive text (not just icons — use `aria-label` for
      icon-only)
- [ ] Toast announcements use `role="alert"` or `aria-live="polite"`
- [ ] Tab navigation uses `role="tablist"` / `role="tab"` / `role="tabpanel"`
