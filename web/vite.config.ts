import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    host: '0.0.0.0',  // ✅ Allow external access
    port: 5173,       // Explicitly set the port
    strictPort: true, // Fail if port is already in use
  }
})