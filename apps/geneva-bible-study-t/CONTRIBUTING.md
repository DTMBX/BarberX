# Contributing to Geneva Bible Study Platform

Thank you for your interest in contributing to the Geneva Bible Study Platform! This document provides guidelines and instructions for developers.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Component Guidelines](#component-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## 🚀 Getting Started

### Prerequisites

- Node.js 20.x or higher
- npm 10.x or higher
- Git
- Code editor (VS Code recommended)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

### Project Structure

```
src/
├── components/
│   ├── ui/              # shadcn/ui components (don't modify)
│   ├── reader/          # Bible reader components
│   ├── social/          # Social features
│   ├── timeline/        # Timeline visualization
│   └── views/           # Main view components
├── hooks/               # Custom React hooks
├── lib/                 # Utilities and data
│   ├── bibleApi.ts     # Bible API integration
│   ├── data.ts         # Static data (books, translations)
│   ├── types.ts        # TypeScript types
│   └── utils.ts        # Utility functions
├── styles/              # CSS and themes
├── App.tsx              # Main application
├── index.css            # Global styles and theme
└── main.tsx             # Entry point (don't modify)
```

## 🔄 Development Workflow

### Branch Naming

- `feature/` - New features (e.g., `feature/audio-playback`)
- `fix/` - Bug fixes (e.g., `fix/search-results`)
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `style/` - UI/styling changes

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting, missing semicolons, etc.
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat(reader): add audio playback controls
fix(search): correct verse highlighting
docs: update API integration guide
refactor(hooks): simplify useBibleChapter logic
```

## 📝 Code Standards

### TypeScript

- Use TypeScript for all new files
- Define proper types/interfaces (see `src/lib/types.ts`)
- Avoid `any` type when possible
- Use type inference where appropriate

```typescript
// ✅ Good
interface VerseProps {
  text: string
  reference: string
  onSelect?: () => void
}

// ❌ Avoid
function VerseDisplay(props: any) {
  // ...
}
```

### React Components

- Use functional components with hooks
- Keep components focused and single-purpose
- Extract reusable logic into custom hooks
- Use proper prop typing

```typescript
// ✅ Good
interface ButtonProps {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary'
}

export function CustomButton({ label, onClick, variant = 'primary' }: ButtonProps) {
  return (
    <Button onClick={onClick} variant={variant}>
      {label}
    </Button>
  )
}
```

### State Management

- Use `useKV` for persistent data (reading progress, settings)
- Use `useState` for temporary UI state
- Always use functional updates with `useKV`

```typescript
// ✅ Good - Functional update
const [items, setItems] = useKV('items', [])
setItems(current => [...current, newItem])

// ❌ Bad - Closure reference (data loss risk)
setItems([...items, newItem])
```

### Styling

- Use Tailwind utility classes
- Follow theme variables (see `src/index.css`)
- Use shadcn/ui components when available
- Keep custom CSS minimal

```typescript
// ✅ Good
<div className="flex items-center gap-4 p-6 bg-card rounded-lg">
  <BookOpen className="text-primary" />
  <span className="text-foreground">Read Bible</span>
</div>

// ❌ Avoid inline styles
<div style={{ display: 'flex', padding: '24px' }}>
  {/* ... */}
</div>
```

### Imports

- Use absolute imports with `@/` alias
- Group imports logically
- Remove unused imports

```typescript
// ✅ Good
import { useState } from 'react'
import { useKV } from '@github/spark/hooks'
import { Button } from '@/components/ui/button'
import { BookOpen } from '@phosphor-icons/react'
import { useBibleChapter } from '@/hooks/use-bible-api'
import type { VerseUnit } from '@/lib/types'

// ❌ Avoid
import { useState } from 'react'
import { BookOpen } from '@phosphor-icons/react'
import { Button } from '@/components/ui/button'
import { useBibleChapter } from '@/hooks/use-bible-api'
import { useKV } from '@github/spark/hooks'
```

## 🧩 Component Guidelines

### Creating New Components

1. **Location:**
   - UI primitives → `components/ui/` (shadcn components only)
   - Feature components → `components/[feature]/`
   - Views → `components/views/`

2. **File naming:**
   - PascalCase for components: `VerseDisplay.tsx`
   - kebab-case for utilities: `bible-utils.ts`

3. **Component structure:**

```typescript
import { /* imports */ } from 'libraries'
import { /* imports */ } from '@/components'
import { /* imports */ } from '@/hooks'
import type { /* types */ } from '@/lib/types'

interface ComponentProps {
  // Props definition
}

export default function Component({ prop1, prop2 }: ComponentProps) {
  // Hooks
  const [state, setState] = useState()
  
  // Effects
  useEffect(() => {
    // ...
  }, [deps])
  
  // Handlers
  const handleClick = () => {
    // ...
  }
  
  // Render
  return (
    <div>
      {/* JSX */}
    </div>
  )
}
```

### Using shadcn/ui Components

- Import from `@/components/ui/[component]`
- Don't modify files in `components/ui/`
- Use composition for customization

```typescript
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Title</CardTitle>
      </CardHeader>
      <CardContent>
        <Button>Click me</Button>
      </CardContent>
    </Card>
  )
}
```

## 🎣 Custom Hooks

### Creating Custom Hooks

Place in `src/hooks/` directory:

```typescript
// hooks/use-bible-verse.ts
import { useState, useEffect } from 'react'
import { fetchVerse } from '@/lib/bibleApi'
import type { VerseUnit } from '@/lib/types'

export function useBibleVerse(bookId: string, chapter: number, verse: number) {
  const [data, setData] = useState<VerseUnit | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    async function loadVerse() {
      try {
        setLoading(true)
        const result = await fetchVerse(bookId, chapter, verse)
        setData(result)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    
    loadVerse()
  }, [bookId, chapter, verse])
  
  return { data, loading, error }
}
```

## 🔌 API Integration

### Using Bible API

The app uses Bolls Life API (public domain, no attribution required).

```typescript
import { useBibleChapter } from '@/hooks/use-bible-api'

function ChapterView() {
  const { verses, loading, error } = useBibleChapter({
    translationId: 'kjv',
    bookId: 'joh',
    chapter: 3
  })
  
  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage error={error} />
  
  return (
    <div>
      {verses.map(verse => (
        <VerseDisplay key={verse.id} verse={verse} />
      ))}
    </div>
  )
}
```

See [BIBLE_API_INTEGRATION.md](./BIBLE_API_INTEGRATION.md) for complete API documentation.

## 🧪 Testing

### Manual Testing Checklist

Before submitting:

- [ ] Feature works on desktop
- [ ] Feature works on mobile
- [ ] Dark mode displays correctly
- [ ] No console errors
- [ ] Proper loading states
- [ ] Error handling works
- [ ] Data persists across sessions (if applicable)

### Testing Persistence

```typescript
// Test KV persistence
const [data, setData] = useKV('test-key', [])

// Add data
setData(current => [...current, newItem])

// Reload page - data should persist
```

### Browser Testing

Test in:
- Chrome/Edge (Chromium)
- Firefox
- Safari (if possible)

## 📤 Submitting Changes

### Pull Request Process

1. **Create feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add my feature"
   ```

3. **Push to GitHub:**
   ```bash
   git push origin feature/my-feature
   ```

4. **Create Pull Request:**
   - Go to GitHub repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out PR template

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Screenshots (if applicable)
[Add screenshots]

## Checklist
- [ ] Code follows project standards
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] No new warnings in console
- [ ] Works on mobile and desktop
- [ ] Dark mode tested
```

## 🐛 Bug Reports

### Reporting Issues

Include:
1. **Description:** What happened vs. what should happen
2. **Steps to reproduce:** Detailed steps
3. **Environment:** Browser, OS, device
4. **Screenshots:** If applicable
5. **Console errors:** Open DevTools → Console

### Issue Template

```markdown
**Describe the bug**
A clear description

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen

**Screenshots**
If applicable

**Environment:**
- Browser: [e.g., Chrome 120]
- OS: [e.g., Windows 11]
- Device: [e.g., Desktop, iPhone 12]

**Console errors**
Paste any errors from browser console
```

## 📚 Additional Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [Radix UI](https://www.radix-ui.com/)
- [Phosphor Icons](https://phosphoricons.com/)

## 💬 Questions?

- Open a GitHub Discussion
- Check existing issues
- Review documentation files

---

Thank you for contributing! 🙏
