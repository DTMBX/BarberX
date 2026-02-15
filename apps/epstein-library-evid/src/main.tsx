// Evident shared design tokens
import '../../../packages/design-tokens/evident-design-tokens.css';

import { createRoot } from 'react-dom/client';
import { ErrorBoundary } from 'react-error-boundary';
import { installSparkShim } from '@/lib/local-storage-kv';

installSparkShim();

import App from './App.tsx';
import { ErrorFallback } from './ErrorFallback.tsx';
import { EngineProvider } from './hooks/use-engine.tsx';

import './main.css';
import './styles/theme.css';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <ErrorBoundary FallbackComponent={ErrorFallback}>
    <EngineProvider>
      <App />
    </EngineProvider>
  </ErrorBoundary>
);
