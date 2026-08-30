# Scaling Up

Distilled from vuejs.org/guide/scaling-up/{sfc,state-management,ssr}, guide/extras/web-components, plus Vue Router & Pinia primers.

## SFC Tooling

- SFCs compiled by `@vue/compiler-sfc` into ES modules; integrate with Vite (recommended) or Vue CLI/webpack.
- `<style>` injected as native tags in dev (HMR); extracted/merged into one CSS file in prod.
- IDE: Volar (VS Code) for `<script setup>` + template type-checking. Playground: play.vuejs.org.

## State Management

- Local state: each component manages its own via `ref`/`reactive`/`data`. One-way flow: state → view → actions → state.
- Shared state problem: multiple views depend on same state, or actions from many views mutate it. Lifting to ancestors = prop drilling.
- Minimal shared store (no library): create reactive state in module scope, import into components.

  ```js
  // store.js
  import { reactive } from 'vue'
  export const store = reactive({ count: 0, increment() { this.count++ } })
  ```

  Mutating from anywhere works but is hard to maintain — centralize mutations as methods. SSR caveat: module singletons leak across requests (cross-request state pollution).
- Can share `ref`/`computed` or return global state from a composable (`useCount()` returns both global and per-instance refs).
- **Pinia** (official, core-team maintained) — recommended for production. Simpler API than Vuex, Composition-style, solid TS inference, devtools timeline, HMR, SSR support. Vuex is maintenance-only.

  ```js
  // stores/counter.js
  import { defineStore } from 'pinia'
  export const useCounterStore = defineStore('counter', {
    state: () => ({ count: 0 }),
    actions: { increment() { this.count++ } },
  })
  // setup-style store also supported:
  // defineStore('counter', () => { const count = ref(0); return { count, increment } })
  ```

  Use: `const counter = useCounterStore()` → `counter.count++` / `counter.increment()`. Map helpers (`mapStores`/`mapState`/`mapActions`) for Options API. No mutations, no namespaced modules (flat by design, can nest stores).

## Server-Side Rendering (SSR)

- Render app to HTML string on server, send to client, then **hydrate** to interactive. Improves SEO + LCP (time-to-content).
- Higher-level frameworks (Nuxt, etc.) build on this. Cross-request state pollution: do NOT use module-singleton stores; create per-request state.
- Teleports in SSR: target must exist; see SSR teleport handling.

## Routing (Vue Router — official)

- Client-side routing for SPAs: URL ↔ route component.
- Create: `createRouter({ history: createWebHistory(), routes: [{ path:'/', component: HomeView }] })`.
  - History modes: `createWebHistory()` (clean URLs), `createWebHashHistory()` (hash, no server config), `createMemoryHistory()` (no URL, testing/SSR).
- Register: `createApp(App).use(router).mount('#app')` (before mount).
- Components: `<RouterLink to="/about">` (nav, no reload), `<RouterView />` (render slot for current route). Both globally registered (also importable).
- Access: Composition → `useRouter()` (navigate: `router.push`/`replace`) and `useRoute()` (current: `route.query`, `route.params`, `route.fullPath`); Options → `this.$router` / `this.$route`.
- Lazy loading: dynamic `import()` in routes (distinct from async components; won't trigger `<Suspense>`).
- Nesting ordering with Transition/KeepAlive/Suspense — see references/06-built-in-components.

## Web Components

- Vue can build standard Web Components embeddable in any HTML page (consumer-agnostic). See guide/extras/web-components.
