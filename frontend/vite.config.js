import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
   server: {
    proxy: {
      '/search':   'http://localhost:7860',
      '/like':     'http://localhost:7860',
      '/likes':    'http://localhost:7860',
      '/random':   'http://localhost:7860',
      '/posts':    'http://localhost:7860',
      '/rag':      'http://localhost:7860',
      '/stats':    'http://localhost:7860',
      '/similar':  'http://localhost:7860',
      '/health':   'http://localhost:7860',
      '/debug':    'http://localhost:7860',
    }
  }
})
