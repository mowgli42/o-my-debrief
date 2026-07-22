import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss(), svelte()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.DEBRIEF_API_PROXY || 'http://127.0.0.1:8020',
        changeOrigin: true,
      },
    },
  },
})
