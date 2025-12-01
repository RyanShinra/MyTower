// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    host: '0.0.0.0',  // ✅ Allow external access for local network testing and maybe inside Docker?
    port: 5173,       // Explicitly set the port
    strictPort: true, // Fail if port is already in use
  }
})