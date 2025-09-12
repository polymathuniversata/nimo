import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    // Enhanced hot reloading configuration
    hmr: {
      overlay: true,
    },
    // Ensure file watching works properly
    watch: {
      usePolling: false,
      interval: 100,
      // Include additional file types for watching
      include: [
        'src/**/*.{ts,tsx,js,jsx,json,css,scss,sass,html}',
        'public/**/*',
        'index.html'
      ],
      // Exclude node_modules and other unnecessary directories
      exclude: [
        'node_modules/**',
        'dist/**',
        '.git/**',
        'coverage/**'
      ]
    },
    // Enable CORS for better development experience
    cors: true,
    // Enable filesystem watching for better performance
    fs: {
      strict: true,
    },
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Optimize build and dev experience
  build: {
    sourcemap: mode === 'development',
  },
  // Ensure CSS hot reloading works properly
  css: {
    devSourcemap: true,
  },
  // Optimize dependencies for faster hot reloading
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@radix-ui/react-dialog',
      'lucide-react'
    ],
    // Force include for better hot reloading
    force: mode === 'development',
  },
  // Define global constants for development
  define: {
    __DEV__: mode === 'development',
  },
}));
