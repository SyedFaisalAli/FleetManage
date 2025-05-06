import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../netmcp/static',
    emptyOutDir: true,
  },
  server: {
    host: "0.0.0.0",
    proxy: {
      '/api': 'http://localhost:8000',
      '/mcp_bridge/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        rewriteWsOrigin: true
      }
    },
  }
})
