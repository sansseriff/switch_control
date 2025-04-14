import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite';
import legacy from '@vitejs/plugin-legacy'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [tailwindcss(), svelte(), legacy({
    targets: ['chrome >= 64', 'safari >= 12'],
    modernPolyfills: true,}),
  ],
  define: {
    'import.meta.env.SKIP_LOADING': JSON.stringify(process.env.SKIP_LOADING || 'false')
  },
})