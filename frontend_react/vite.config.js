import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Dev proxy: mọi request /api/... được chuyển sang Spring Boot (cổng 3000)
      // theo rule QODER.md — frontend không hard-code URL backend.
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
})