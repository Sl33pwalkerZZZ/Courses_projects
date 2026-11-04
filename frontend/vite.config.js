import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Native protected-video requests need same-origin cookies, not CORS JWT URLs.
  // Production must route /api to Django on the frontend's HTTPS origin too.
  server: {
    proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true } },
  },
})
