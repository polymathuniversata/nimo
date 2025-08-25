import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      'src': resolve(__dirname, './src'),
      'components': resolve(__dirname, './src/components'),
      'pages': resolve(__dirname, './src/pages'),
      'stores': resolve(__dirname, './src/stores'),
      'router': resolve(__dirname, './src/router'),
      'services': resolve(__dirname, './src/services'),
      'composables': resolve(__dirname, './src/composables')
    }
  },
  server: {
    port: 9000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "quasar/src/css/variables.sass";`
      }
    }
  }
})