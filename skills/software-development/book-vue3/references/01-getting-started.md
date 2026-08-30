# Getting Started with Vue 3

Distilled from vuejs.org/guide/introduction, quick-start, extras/ways-of-using-vue.

## What Vue Is

- Progressive JavaScript framework for building UIs. Declarative, component-based, built on HTML/CSS/JS.
- Two core features: **Declarative Rendering** (template syntax describing HTML output from JS state) and **Reactivity** (auto-tracks state changes, efficiently patches the DOM).
- Vue 2 reached EOL on 2023-12-31. This skill covers Vue 3 only.

## Ways of Using Vue (progressive adoption)

- **Standalone script** (CDN, no build): treat Vue like a declarative jQuery for sprinkling interactivity on server-rendered HTML. `petite-vue` is unmaintained (last at Vue 3.2.27).
- **Embedded Web Components**: build standards-compliant custom elements embeddable anywhere.
- **SPA**: Vue controls the whole page, client-side navigation, no full reloads. Use Vite + Vue Router.
- **SSR / Fullstack**: render to HTML strings on the server, hydrate on client. Best for SEO / time-to-content (improves LCP).
- **SSG / JAMStack**: pre-render to static HTML. Single-page SSG hydrates into an SPA; multi-page SSG ships minimal/no JS (Astro partial hydration). VitePress is the team's own SSG.
- **Beyond web**: Electron, Wails, Ionic Vue, Quasar, Tauri (desktop/mobile), TresJS (WebGL), custom renderer API (e.g. terminal).

## Single-File Components (SFC)

- `*.vue` file: `<script>`, `<template>`, `<style>` blocks colocated per component.
- Requires a build step (`@vue/compiler-sfc` → standard ES module). Vite is the recommended tool.
- Benefits: familiar syntax, colocation, pre-compiled templates (no runtime compile cost), scoped CSS, better Composition API ergonomics, compile-time optimizations, IDE support, HMR.
- "Separation of concerns ≠ separation of file types." Components group inherently coupled logic/view/style — more cohesive than 3 giant layers.
- Can split JS/CSS into separate files via `src` imports if preferred.

## API Styles

- **Options API**: component logic via option object (`data`, `methods`, `mounted`). Properties exposed on `this`. Beginner-friendly; enforces organization by option group.
- **Composition API**: logic via imported functions (`ref`, `onMounted`). Typically used with `<script setup>`. More free-form; powerful for organizing/reusing logic. Built on fine-grained mutable reactivity (NOT functional programming).
- Options API is implemented *on top of* Composition API. Fundamental concepts are shared.
- Recommendation: learning → whichever is clearer; production → Options API only for no-build / low-complexity enhancement, Composition API + SFC for full apps.
- API preference toggle on the docs sidebar switches code samples between the two styles.

## Minimal App

```js
import { createApp, ref } from 'vue'
createApp({
  setup() {
    return { count: ref(0) }
  }
}).mount('#app')
```

SFC equivalent uses `<script setup>` with `const count = ref(0)`.
