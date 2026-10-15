import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    // 開發時把 API 與 WebSocket 轉給後端；後端要用 WLASL_DEV=1 啟動才會放行 5173 這個來源
    proxy: {
      '/api': { target: 'http://127.0.0.1:8766', changeOrigin: true },
      '/ws': { target: 'ws://127.0.0.1:8766', ws: true, changeOrigin: true },
    },
  },
})
