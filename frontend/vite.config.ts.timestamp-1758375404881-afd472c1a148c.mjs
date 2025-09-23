// vite.config.ts
import { defineConfig } from "file:///mnt/e/Polymath%20Universata/Projects/Nimo/frontend/node_modules/vite/dist/node/index.js";
import react from "file:///mnt/e/Polymath%20Universata/Projects/Nimo/frontend/node_modules/@vitejs/plugin-react-swc/index.js";
import path from "path";
import { componentTagger } from "file:///mnt/e/Polymath%20Universata/Projects/Nimo/frontend/node_modules/lovable-tagger/dist/index.js";
var __vite_injected_original_dirname = "/mnt/e/Polymath Universata/Projects/Nimo/frontend";
var vite_config_default = defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 5173,
    // Enhanced hot reloading configuration
    hmr: {
      overlay: true,
      timeout: 5e3,
      port: 5173
    },
    // Ensure file watching works properly
    watch: {
      usePolling: true,
      interval: 100,
      // Include additional file types for watching
      include: [
        "src/**/*.{ts,tsx,js,jsx,json,css,scss,sass,html}",
        "public/**/*",
        "index.html"
      ],
      // Exclude node_modules and other unnecessary directories
      exclude: [
        "node_modules/**",
        "dist/**",
        ".git/**",
        "coverage/**"
      ]
    },
    // Enable CORS for better development experience
    cors: true,
    // Enable filesystem watching for better performance
    fs: {
      strict: true
    }
  },
  plugins: [
    react(),
    mode === "development" && componentTagger()
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "./src")
    }
  },
  // Optimize build and dev experience
  build: {
    sourcemap: mode === "development"
  },
  // Ensure CSS hot reloading works properly
  css: {
    devSourcemap: true
  },
  // Optimize dependencies for faster hot reloading
  optimizeDeps: {
    include: [
      "react",
      "react-dom",
      "react-router-dom",
      "@radix-ui/react-dialog",
      "lucide-react"
    ],
    // Force include for better hot reloading
    force: mode === "development"
  },
  // Define global constants for development
  define: {
    __DEV__: mode === "development"
  }
}));
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvbW50L2UvUG9seW1hdGggVW5pdmVyc2F0YS9Qcm9qZWN0cy9OaW1vL2Zyb250ZW5kXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvbW50L2UvUG9seW1hdGggVW5pdmVyc2F0YS9Qcm9qZWN0cy9OaW1vL2Zyb250ZW5kL3ZpdGUuY29uZmlnLnRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9tbnQvZS9Qb2x5bWF0aCUyMFVuaXZlcnNhdGEvUHJvamVjdHMvTmltby9mcm9udGVuZC92aXRlLmNvbmZpZy50c1wiO2ltcG9ydCB7IGRlZmluZUNvbmZpZyB9IGZyb20gXCJ2aXRlXCI7XG5pbXBvcnQgcmVhY3QgZnJvbSBcIkB2aXRlanMvcGx1Z2luLXJlYWN0LXN3Y1wiO1xuaW1wb3J0IHBhdGggZnJvbSBcInBhdGhcIjtcbmltcG9ydCB7IGNvbXBvbmVudFRhZ2dlciB9IGZyb20gXCJsb3ZhYmxlLXRhZ2dlclwiO1xuXG4vLyBodHRwczovL3ZpdGVqcy5kZXYvY29uZmlnL1xuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKCh7IG1vZGUgfSkgPT4gKHtcbiAgc2VydmVyOiB7XG4gICAgaG9zdDogXCI6OlwiLFxuICAgIHBvcnQ6IDUxNzMsXG4gICAgLy8gRW5oYW5jZWQgaG90IHJlbG9hZGluZyBjb25maWd1cmF0aW9uXG4gICAgaG1yOiB7XG4gICAgICBvdmVybGF5OiB0cnVlLFxuICAgICAgdGltZW91dDogNTAwMCxcbiAgICAgIHBvcnQ6IDUxNzNcbiAgICB9LFxuICAgIC8vIEVuc3VyZSBmaWxlIHdhdGNoaW5nIHdvcmtzIHByb3Blcmx5XG4gICAgd2F0Y2g6IHtcbiAgICAgIHVzZVBvbGxpbmc6IHRydWUsXG4gICAgICBpbnRlcnZhbDogMTAwLFxuICAgICAgLy8gSW5jbHVkZSBhZGRpdGlvbmFsIGZpbGUgdHlwZXMgZm9yIHdhdGNoaW5nXG4gICAgICBpbmNsdWRlOiBbXG4gICAgICAgICdzcmMvKiovKi57dHMsdHN4LGpzLGpzeCxqc29uLGNzcyxzY3NzLHNhc3MsaHRtbH0nLFxuICAgICAgICAncHVibGljLyoqLyonLFxuICAgICAgICAnaW5kZXguaHRtbCdcbiAgICAgIF0sXG4gICAgICAvLyBFeGNsdWRlIG5vZGVfbW9kdWxlcyBhbmQgb3RoZXIgdW5uZWNlc3NhcnkgZGlyZWN0b3JpZXNcbiAgICAgIGV4Y2x1ZGU6IFtcbiAgICAgICAgJ25vZGVfbW9kdWxlcy8qKicsXG4gICAgICAgICdkaXN0LyoqJyxcbiAgICAgICAgJy5naXQvKionLFxuICAgICAgICAnY292ZXJhZ2UvKionXG4gICAgICBdXG4gICAgfSxcbiAgICAvLyBFbmFibGUgQ09SUyBmb3IgYmV0dGVyIGRldmVsb3BtZW50IGV4cGVyaWVuY2VcbiAgICBjb3JzOiB0cnVlLFxuICAgIC8vIEVuYWJsZSBmaWxlc3lzdGVtIHdhdGNoaW5nIGZvciBiZXR0ZXIgcGVyZm9ybWFuY2VcbiAgICBmczoge1xuICAgICAgc3RyaWN0OiB0cnVlLFxuICAgIH0sXG4gIH0sXG4gIHBsdWdpbnM6IFtcbiAgICByZWFjdCgpLFxuICAgIG1vZGUgPT09ICdkZXZlbG9wbWVudCcgJiZcbiAgICBjb21wb25lbnRUYWdnZXIoKSxcbiAgXS5maWx0ZXIoQm9vbGVhbiksXG4gIHJlc29sdmU6IHtcbiAgICBhbGlhczoge1xuICAgICAgXCJAXCI6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsIFwiLi9zcmNcIiksXG4gICAgfSxcbiAgfSxcbiAgLy8gT3B0aW1pemUgYnVpbGQgYW5kIGRldiBleHBlcmllbmNlXG4gIGJ1aWxkOiB7XG4gICAgc291cmNlbWFwOiBtb2RlID09PSAnZGV2ZWxvcG1lbnQnLFxuICB9LFxuICAvLyBFbnN1cmUgQ1NTIGhvdCByZWxvYWRpbmcgd29ya3MgcHJvcGVybHlcbiAgY3NzOiB7XG4gICAgZGV2U291cmNlbWFwOiB0cnVlLFxuICB9LFxuICAvLyBPcHRpbWl6ZSBkZXBlbmRlbmNpZXMgZm9yIGZhc3RlciBob3QgcmVsb2FkaW5nXG4gIG9wdGltaXplRGVwczoge1xuICAgIGluY2x1ZGU6IFtcbiAgICAgICdyZWFjdCcsXG4gICAgICAncmVhY3QtZG9tJyxcbiAgICAgICdyZWFjdC1yb3V0ZXItZG9tJyxcbiAgICAgICdAcmFkaXgtdWkvcmVhY3QtZGlhbG9nJyxcbiAgICAgICdsdWNpZGUtcmVhY3QnXG4gICAgXSxcbiAgICAvLyBGb3JjZSBpbmNsdWRlIGZvciBiZXR0ZXIgaG90IHJlbG9hZGluZ1xuICAgIGZvcmNlOiBtb2RlID09PSAnZGV2ZWxvcG1lbnQnLFxuICB9LFxuICAvLyBEZWZpbmUgZ2xvYmFsIGNvbnN0YW50cyBmb3IgZGV2ZWxvcG1lbnRcbiAgZGVmaW5lOiB7XG4gICAgX19ERVZfXzogbW9kZSA9PT0gJ2RldmVsb3BtZW50JyxcbiAgfSxcbn0pKTtcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBdVUsU0FBUyxvQkFBb0I7QUFDcFcsT0FBTyxXQUFXO0FBQ2xCLE9BQU8sVUFBVTtBQUNqQixTQUFTLHVCQUF1QjtBQUhoQyxJQUFNLG1DQUFtQztBQU16QyxJQUFPLHNCQUFRLGFBQWEsQ0FBQyxFQUFFLEtBQUssT0FBTztBQUFBLEVBQ3pDLFFBQVE7QUFBQSxJQUNOLE1BQU07QUFBQSxJQUNOLE1BQU07QUFBQTtBQUFBLElBRU4sS0FBSztBQUFBLE1BQ0gsU0FBUztBQUFBLE1BQ1QsU0FBUztBQUFBLE1BQ1QsTUFBTTtBQUFBLElBQ1I7QUFBQTtBQUFBLElBRUEsT0FBTztBQUFBLE1BQ0wsWUFBWTtBQUFBLE1BQ1osVUFBVTtBQUFBO0FBQUEsTUFFVixTQUFTO0FBQUEsUUFDUDtBQUFBLFFBQ0E7QUFBQSxRQUNBO0FBQUEsTUFDRjtBQUFBO0FBQUEsTUFFQSxTQUFTO0FBQUEsUUFDUDtBQUFBLFFBQ0E7QUFBQSxRQUNBO0FBQUEsUUFDQTtBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUE7QUFBQSxJQUVBLE1BQU07QUFBQTtBQUFBLElBRU4sSUFBSTtBQUFBLE1BQ0YsUUFBUTtBQUFBLElBQ1Y7QUFBQSxFQUNGO0FBQUEsRUFDQSxTQUFTO0FBQUEsSUFDUCxNQUFNO0FBQUEsSUFDTixTQUFTLGlCQUNULGdCQUFnQjtBQUFBLEVBQ2xCLEVBQUUsT0FBTyxPQUFPO0FBQUEsRUFDaEIsU0FBUztBQUFBLElBQ1AsT0FBTztBQUFBLE1BQ0wsS0FBSyxLQUFLLFFBQVEsa0NBQVcsT0FBTztBQUFBLElBQ3RDO0FBQUEsRUFDRjtBQUFBO0FBQUEsRUFFQSxPQUFPO0FBQUEsSUFDTCxXQUFXLFNBQVM7QUFBQSxFQUN0QjtBQUFBO0FBQUEsRUFFQSxLQUFLO0FBQUEsSUFDSCxjQUFjO0FBQUEsRUFDaEI7QUFBQTtBQUFBLEVBRUEsY0FBYztBQUFBLElBQ1osU0FBUztBQUFBLE1BQ1A7QUFBQSxNQUNBO0FBQUEsTUFDQTtBQUFBLE1BQ0E7QUFBQSxNQUNBO0FBQUEsSUFDRjtBQUFBO0FBQUEsSUFFQSxPQUFPLFNBQVM7QUFBQSxFQUNsQjtBQUFBO0FBQUEsRUFFQSxRQUFRO0FBQUEsSUFDTixTQUFTLFNBQVM7QUFBQSxFQUNwQjtBQUNGLEVBQUU7IiwKICAibmFtZXMiOiBbXQp9Cg==
