# Components

Distilled from vuejs.org/guide/components/{basics,registration,props,events,slots,attrs,provide-inject,async,v-model}.

## Defining & Using

- Build-step: `.vue` SFC. No build: plain JS object with `template` string (or `template: '#id'` for in-DOM).
- Use a child: import + register. `<script setup>`: imported components are auto-available. Options: `components: { Child }`.
- Each usage creates a **new instance** (own isolated state). Reuse freely.
- Naming: `PascalCase` for tags in SFCs (differentiates from native elements); `kebab-case` required in in-DOM templates. Single-root recommended; self-closing `/>` allowed in SFCs only.
- Registration: **local** (scoped, tree-shakeable — preferred) vs **global** (`app.component()` — pollutes bundle, harder to trace). Global: `RouterView`/`RouterLink`, built-ins (`Transition`, `Teleport`, `KeepAlive`, `Suspense`) need no registration.

## Props

- Declare: `defineProps(['foo'])` / `<script setup>`; `props: ['foo']` or `props: { title: String, likes: Number }` (object form validates types, warns on mismatch). TS: `defineProps<{ title?: string }>()`.
- Reactivity: 3.5+ destructured props stay reactive (`const { foo } = defineProps(...)`); pre-3.5 destructure is a static snapshot. Passing a destructured prop into `watch`/`useComposable` must be a getter: `watch(() => foo, ...)` — not `watch(foo, ...)` (value, not source).
- Casing: declare camelCase; pass `kebab-case` in templates (convention). Vue auto-transforms.
- One-way data flow: parent→child only. **Never mutate a prop.** Emit an event, or use `v-model`/`defineModel`.
- Passing: static `title="x"`, dynamic `:title="post.title"`, typed `:likes="42"`, boolean shorthand `is-published` (=true), object spread `v-bind="post"`.
- Boolean casting: `disabled: Boolean` → presence means `true`. Order matters: `[Boolean, String]` casts, `[String, Boolean]` does not.
- Validation: type (native ctor, array, or custom class via `instanceof`), `required`, `default` (functions for objects/arrays), `validator`. `default`/`validator` run before instance creation — no `data`/`computed` access.
- Nullable required: `type: [String, null], required: true`.

## Events (Emits)

- Emit: `$emit('someEvent')` in template/`this.$emit()`. Declare: `defineEmits(['submit'])` / `emits: ['submit']`. Returns `emit` for `<script setup>`. Type/validate via object form: `submit: ({email,password}) => !!email && !!password`.
- Casing: emit camelCase, listen kebab-case (`@some-event`). `.once` supported on listeners.
- Extra args forwarded: `$emit('foo', 1, 2, 3)` → listener gets 3 args.
- Declaring a native event in `emits` makes listeners respond only to component-emitted events, not native ones.
- Component events do **not** bubble — only direct children. Siblings/deep: event bus or global state.

## v-model on Components (defineModel)

- 3.4+: `const model = defineModel()` (returns a ref, two-way bound to parent `v-model`). Mutating `model.value` updates parent. Under the hood: declares `modelValue` prop + `update:modelValue` event.
- Pre-3.4 equivalent: `defineProps(['modelValue'])`, `defineEmits(['update:modelValue'])` + `:value`/`@input` wiring.
- Named: `v-model:title` → `defineModel('title')`. Multiple: `v-model:first-name` + `v-model:last-name`.
- Options: `defineModel({ required: true })`, `defineModel({ default: 0 })` (note: default can desync with undefined parent). Modifiers via `[value, modifiers] = defineModel('title')`.
- WARNING: mutable default (array/object) in `defineModel`/`withDefaults` should be a factory function.

## Slots

- `<slot>` outlet; parent content rendered in child. Fallback: `<slot>Submit</slot>`.
- Render scope: slot content accesses **parent** scope only; child data not visible.
- Named slots: `<slot name="header">`; parent `<template #header>`. `#` = `v-slot:` shorthand. Unnamed = `default`. Top-level non-template nodes = default slot implicitly.
- Scoped slots: child passes data to slot via `<slot :user="user">`; parent `<template #default="slotProps">` (destructurable). Renderless components (logic only, visual delegated) — mostly superseded by composables.

## Fallthrough Attributes

- Attributes/events not declared as props/emits fall through to the single root element (`class`, `style`, `id`, `v-on` merge).
- Multi-root: no automatic fallthrough — bind explicitly `v-bind="$attrs"` on one node or get a warning.
- Disable: `inheritAttrs: false` (Options) or `defineOptions({ inheritAttrs: false })` (3.3+ `<script setup>`). Access via `$attrs` in template / `useAttrs()` in script (not reactive — use prop if you need reactivity).
- `v-on` listener inheritance: parent `@click` lands on child root; both fire if child also binds click.

## Provide / Inject

- Solve prop drilling: ancestor `provide(key, value)` → any descendant `inject(key)`. Key: string or `Symbol` (Symbol avoids collisions in large apps; export from a `keys.js`).
- Reactive: provide a `ref`/`reactive` so descendants stay linked. Keep mutations in the **provider**; or provide an updater function. Wrap with `readonly()` to forbid injector mutation.
- Options: `provide()` / `inject` array or object `{ localKey: { from: 'key', default } }`. `inject(key, 'default')`; factory default: `inject(key, () => new Expensive(), true)`.
- App-level: `app.provide(key, value)` (plugins).

## Async Components

- `defineAsyncComponent(() => import('./Foo.vue'))` — lazy-loaded on first render. Works with `app.component`/local registration.
- Loading/error: object form `defineAsyncComponent({ loader, loadingComponent, errorComponent, delay: 200, timeout: 3000 })`.
- SSR lazy hydration (3.5+): `hydrateOnIdle`, `hydrateOnVisible`, `hydrateOnMediaQuery`, `hydrateOnInteraction`. Pairs with `<Suspense>`.
