import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import ui from '@nuxt/ui/vite'

const base = process.env.VITE_BASE_PATH || '/'

export default defineConfig({
  base,
  plugins: [vue(), ui()],
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
