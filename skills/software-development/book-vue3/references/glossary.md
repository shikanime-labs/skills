# Glossary & Cross-References

Terms from the Vue 3 documentation with pointers to the reference file that covers them. Load the referenced file via `skill_view(name="book-vue3", file_path="references/<file>")`.

- **SFC (Single-File Component)**: `*.vue` file. → 01-getting-started, 07-scaling-up, 05-composition-api.
- **Options API**: option-object component style (`data`, `methods`, `mounted`). → 01, 05.
- **Composition API**: function-import style (`ref`, `onMounted`). Built on fine-grained mutable reactivity, NOT functional programming. → 05, 02, 01.
- **`<script setup>`**: compile-time sugar for Composition API in SFCs. → 05.
- **ref**: reactive primitive wrapper `{ value }`. → 02, 09.
- **reactive**: deep proxy for objects/arrays. → 02.
- **computed**: cached derived value (getter); writable via set. → 02.
- **watch / watchEffect**: side effects on state change. → 02.
- **Proxy (reactivity)**: JS `Proxy` underpins Vue 3 reactivity. → 02.
- **One-way data flow**: props parent→child only; never mutate props. → 04.
- **defineProps / defineEmits**: declare props/events (macros). → 05, 04, 09.
- **defineModel**: two-way binding prop (3.4+); sugar over `modelValue` + `update:modelValue`. → 04, 05, 09.
- **defineExpose**: expose `<script setup>` internals to parent refs. → 05, 04.
- **Slots**: parent-provided template content; named + scoped. → 04.
- **Fallthrough attributes**: undeclared attrs/events merge to root; `$attrs`, `inheritAttrs`. → 04.
- **Provide / Inject**: dependency injection across the tree; solves prop drilling. → 04.
- **Composable**: `use*` function encapsulating reusable stateful logic. → 05.
- **Props drilling**: passing props through many layers; use provide/inject or Pinia. → 04.
- **Mixin**: legacy logic-reuse (deprecated); composables replace it. → 05.
- **v-bind / v-on / v-model / v-if / v-for / v-show**: core directives. → 03, 09.
- **key (attribute)**: identity for v-for / transition. → 03, 09.
- **Transition / TransitionGroup / KeepAlive / Teleport / Suspense**: built-ins. → 06.
- **Pinia**: official state-management library (replaces Vuex). → 07.
- **Vue Router**: official client-side router; `createRouter`, `RouterView`, `RouterLink`. → 07.
- **SSR / Hydration**: server render → client hydrate. → 07, 08.
- **SFC Tooling**: Vite, `@vue/compiler-sfc`, Volar. → 07.
- **Style Guide priorities A–D**: essential / strongly recommended / recommended / caution. → 08.
- **v-html**: XSS risk — trusted content only. → 08.
- **v-once / v-memo**: render-once / memoize for perf. → 08.
- **LRU cache**: `KeepAlive max` evicts least-recently-used. → 06.
- **FLIP**: TransitionGroup move animations use transform. → 06.
