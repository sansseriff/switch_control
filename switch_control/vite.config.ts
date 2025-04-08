import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [tailwindcss(), svelte()],
  define: {
    'import.meta.env.SKIP_LOADING': JSON.stringify(process.env.SKIP_LOADING || 'false')
  }
})
