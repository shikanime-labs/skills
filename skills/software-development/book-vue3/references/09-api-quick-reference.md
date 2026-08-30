# API Quick Reference (high-traffic surface)

Synthesized from vuejs.org/api. For exhaustive signatures, open the live API reference. This is the daily-use surface, not a full enumeration.

## Global / App

- `createApp(rootComponent, rootProps?)` → app instance.
- `app.mount(selector|el)` → returns root instance (call AFTER config).
- `app.component(name, comp)`, `app.directive`, `app.provide(key, val)`.
- `app.config.errorHandler`, `app.config.warnHandler`, `app.config.globalProperties`.
- `app.use(plugin, options?)` — register a plugin (before mount).

## Reactivity Core (`vue`)

- `ref(initialValue)` → `{ value }` (`.value` in JS, unwrapped in template). `isRef`, `unref`, `toRef`, `toRefs`, `toValue`.
- `reactive(obj)` → deep proxy. `isReactive`, `shallowReactive`.
- `readonly(obj)` / `shallowReadonly` — guarded proxy. `isReadonly`.
- `computed(getter, options?)` → ref; writable via `{ get, set }`.
- `watch(source, cb, options?)` — `deep`, `immediate`, `once` (3.4+), `flush`. `watchEffect`, `watchPostEffect`, `watchSyncEffect`.
- `triggerRef`, `customRef`, `markRaw` (exclude from reactivity), `toRaw`.

## Lifecycle (Composition) — register synchronously in setup

- `onBeforeMount`, `onMounted`, `onBeforeUpdate`, `onUpdated`, `onBeforeUnmount`, `onUnmounted`, `onActivated`, `onDeactivated`, `onErrorCaptured`, `onRenderTracked`, `onRenderTriggered`, `onServerPrefetch`.

## Dependency Injection

- `provide(key, value)`, `inject(key, default?)`, `inject(key, default, true)` (factory default).

## Template Refs & Helpers

- `useTemplateRef(key)` (3.5+) / `ref(null)` bound to `ref="key"`.
- `useAttrs()` (fallthrough attrs, non-reactive), `useSlots()`, `useCssModule()`, `useModel` (alias of defineModel), `useId` (3.5+ stable unique id).

## `<script setup>` Compiler Macros

- `defineProps`, `defineEmits`, `defineExpose`, `defineOptions` (3.3+), `defineModel` (3.4+), `defineSlots` (3.3+).
- Type-only: `defineProps<{}>()`, `defineEmits<{}>()`. `withDefaults()` for defaults. Cannot use both runtime and type form.

## Directives

- `v-text`, `v-html` (XSS risk, trusted only), `v-show`, `v-if/else-if/else`, `v-for`, `v-on`/`@` (+ `.stop .prevent .self .capture .once .passive`, key/sys modifiers, `.exact`), `v-bind`/`:` (+ `.prop .attr .camel`, `v-bind="obj"`), `v-model` (+ `.lazy .number .trim`, `v-model:arg`, modifiers), `v-slot`/`#`, `v-pre`, `v-once`, `v-memo` (3.2+), `v-cloak`.

## Special Attributes

- `key` (v-for / transition identity), `ref` (template ref), `is` (treat element as component, prefix `vue:` for native in-DOM).

## Built-in Components

- `<Transition>`, `<TransitionGroup>`, `<KeepAlive>`, `<Teleport>`, `<Suspense>`, `<RouterView>`/`<RouterLink>` (Vue Router), `<component :is>`.

## Options API (selected)

- Data: `data()`, `props`, `computed`, `methods`, `watch`, `emits`, `expose`, `provide`.
- Lifecycle: `beforeCreate`, `created`, `beforeMount`, `mounted`, `beforeUpdate`, `updated`, `beforeUnmount`, `unmounted`, `activated`, `deactivated`, `errorCaptured`, `serverPrefetch`.
- Misc: `name`, `components`, `directives`, `inheritAttrs`, `mixins` (deprecated), `extends`.

## Common Gotchas (signature-level)

- `watch` object source is deep; to watch nested prop use getter `() => obj.x`.
- `v-model` on component = `:modelValue` + `@update:modelValue` (3.4+ use `defineModel`).
- `reactive()` original object stays raw; arrays/Maps don't unwrap nested refs.
- `defineProps`/`defineEmits`/`defineModel` are macros — top-level only, no import.
