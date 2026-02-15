import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vite";
import { resolve } from 'path'

const projectRoot = process.env.PROJECT_ROOT || import.meta.dirname

// https://vite.dev/config/
export default defineConfig({
  // Base path for deployment under evident.icu/apps/geneva-bible-study/
  base: '/apps/geneva-bible-study/',
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': resolve(projectRoot, 'src'),
      '@github/spark/hooks': resolve(projectRoot, 'src/lib/local-storage-kv.ts'),
      '@github/spark/spark': resolve(projectRoot, 'src/lib/local-storage-kv.ts'),
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['@radix-ui/react-dialog', '@radix-ui/react-popover', '@radix-ui/react-select'],
          'phosphor-icons': ['@phosphor-icons/react'],
        },
      },
    },
  },
});
