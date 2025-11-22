// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

import { mount } from 'svelte'
import './app.css'
import App from './App.svelte'

const app = mount(App, {
  target: document.getElementById('app')!,
})

export default app
