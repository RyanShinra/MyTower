/// <reference types="svelte" />
/// <reference types="vite/client" />

// Extend Vite's ImportMetaEnv interface to include our custom environment variables
interface ImportMetaEnv {
  readonly VITE_SERVER_HOST?: string
  readonly VITE_SERVER_PORT?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
