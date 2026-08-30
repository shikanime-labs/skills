# Composition API & `<script setup>`

Distilled from vuejs.org/api/sfc-script-setup, guide/essentials/{lifecycle,template-refs}, guide/reusability/composables.

## `<script setup>` — the recommended SFC form

- Compile-time syntactic sugar for Composition API in SFCs. Better: less boilerplate, TS for props/emits, better runtime perf (no intermediate proxy), better IDE type inference.
- Opt-in: `<script setup>` attribute. Code runs **per instance** (unlike normal `<script>`, which runs once on import).
- Top-level bindings (vars, functions, imports) are directly usable in template — no `return`. Imports work as template helpers. Components used as variables: `<MyComponent />` or dynamic `<component :is="Foo" />`.
- Recursive: file refers to itself by filename (`FooBar.vue` → `<FooBar/>`); imported name wins on conflict (alias via `import { FooBar as Child }`).
- Namespaced: `import * as Form from './form-components'` → `<Form.Input>`.
- Custom directives: local must be named `vNameOfDirective`.

## Macros (no import needed, compiled away)

- `defineProps()` / `defineEmits()` — must be called at top level of `<script setup>` (not inside a function). Options cannot reference local setup vars (only module-scope/imports).
- Type-only decl: `defineProps<{ foo: string }>()`, `defineEmits<{ change: [id: number] }>()`. Use runtime OR type, not both. Runtime generated from types in dev (e.g. `foo: string` → `foo: String`).
- Reactive props destructure (3.5+): `const { msg = 'hi' } = defineProps<Props>()` is reactive. Pre-3.5: `withDefaults(defineProps<Props>(), { msg: 'hi' })`. Default for mutable ref types in `withDefaults` must be a function.
- `defineModel()` (3.4+): two-way binding prop — see references/04-components.
- `defineExpose({ a, b })`: expose internals to parent template refs (otherwise `<script setup>` is private by default). Must be called before any `await`.
- `defineOptions({ inheritAttrs: false })` (3.3+): set component options like `inheritAttrs`, `name` from inside `<script setup>`.
- Top-level `await` → compiled to `async setup()`, requires `<Suspense>`.

## Lifecycle Hooks (Composition)

- Imported functions, registered synchronously during setup. All hooks bind `this` to the instance (avoid arrow functions in Options form).
- Most used: `onMounted`, `onUpdated`, `onUnmounted`. Plus `onBeforeMount`, `onBeforeUpdate`, `onBeforeUnmount`, `onActivated`/`onDeactivated` (KeepAlive), `onErrorCaptured`, `onRenderTracked`/`onRenderTriggered`, `onServerPrefetch`.
- Must register **synchronously** in setup; a `setTimeout(() => onMounted(...))` will not bind. Calling from an external function is fine if the call stack originates synchronously in setup.

## Composables

- A function that uses Composition API to encapsulate & reuse **stateful** logic (vs stateless helpers like lodash/date-fns). Each caller gets its own state.
- Convention: name starts with `use` (e.g. `useMouse`, `useFetch`).
- Pattern: extract `ref`/`reactive` state + lifecycle hooks (`onMounted`/`onUnmounted`) into `useXxx()`; return the state. Composables **nest** (call one from another) — basis for the "Composition" name.
- `useFetch(url)` with reactive source:

  ```js
  import { ref, watchEffect, toValue } from 'vue'
  export function useFetch(url) {
    const data = ref(null), error = ref(null)
    watchEffect(() => {
      data.value = null; error.value = null
      fetch(toValue(url)).then(r => r.json()).then(j => data.value = j).catch(e => error.value = e)
    })
    return { data, error }
  }
  ```

  `toValue()` accepts refs, getters, or plain values — pass `url` as ref or `() => \`/posts/${props.id}\`` to re-fetch on change.
- vs mixins: composables avoid implicit cross-mixin coupling, namespace collisions (rename on destructure), and invisible communication. Mixins deprecated in Vue 3.
- vs renderless components: composables have no extra component-instance overhead. Use composable for logic-only reuse; component when reusing logic + layout.
- vs React Hooks: Vue calls setup once (no stale closures, order-independent, conditional OK); reactivity auto-collects deps (no dep arrays); fine-grained updates (no manual `useCallback`/`useMemo`).
- Library: VueUse (collection of composables).

## Template Refs (in Composition API)

- 3.5+: `const input = useTemplateRef('my-input')` (arg matches template `ref="my-input"`). Pre-3.5: `const input = ref(null)` with matching name.
- Available after mount only. On component → instance; `<script setup>` child private unless `defineExpose`. `v-for` → array. Function refs: `:ref="el => ..."`.
