# Reactivity Fundamentals

Distilled from vuejs.org/guide/essentials/{reactivity-fundamentals,computed,watchers}.

## Core Model

- Vue 3 reactivity is built on JavaScript `Proxy`. State mutations are tracked (getter) and trigger re-render (setter).
- A component renders once; Vue **tracks** every reactive value read during render, then **triggers** re-render for components tracking a mutated ref.

## ref() — primitives & single values

- `const count = ref(0)` → wraps value in `{ value }`. Read/write via `.value` in JS.
- Auto-unwrapped in templates: `{{ count }}` (no `.value`). Also unwrapped in `setup()` return and `<script setup>` top-level bindings.
- Can be passed into functions while keeping reactivity (unlike plain variables).
- Mutate in event handlers: `@click="count++"` works in template; in JS use `count.value++`.

## reactive() — objects & arrays

- `const obj = reactive({ count: 0 })` → deep proxy. Access/mutate directly: `obj.count++`. No `.value`.
- The **original** object is NOT made reactive: `this.someObject = newObject` then `this.someObject !== newObject` — always access state through the proxy.
- Do not destructure reactive objects (loses reactivity) unless using 3.5+ reactive props destructure.

## reactive() vs ref() unwrapping

- `ref` nested in `reactive` is auto-unwrapped: `reactive({ count: ref(0) })` → `obj.count` is `0` (the number).
- `ref` inside a **reactive array or Map** is NOT unwrapped: `books[0].value`, `map.get('count').value`.

## Template unwrapping caveat

- Unwrapping only applies to **top-level** template bindings. `const object = { id: ref(1) }` → `{{ object.id }}` renders `[object Object]` (ref not unwrapped). Fix: destructure `const { id } = object`.
- A ref IS unwrapped when it is the final value of a text interpolation: `{{ object.id }}` renders `1` (convenience only).

## computed()

- `const fullName = computed(() => firstName.value + ' ' + lastName.value)` → returns a computed ref, auto-unwrapped in templates.
- **Cached** based on reactive dependencies; only re-evaluates when a dependency changes. Use instead of a method when value is reused.
- Getter-only by default. Writable via `{ get(), set(v) }`.
- 3.4+: getter receives previous value as first arg: `computed((previous) => ...)`.
- Best practice: getters are **pure** — no side effects, no async, no DOM mutation. Derive only; mutate source state instead.

## watch(source, cb, options)

- Side effects in reaction to state change (DOM mutation, async, cross-state updates).
- Source types: a ref, a reactive object (implicitly deep), a getter `() => x.value + y.value`, or an array of sources.
- Callback: `(newValue, oldValue)`. For reactive object sources, `newValue === oldValue` (same proxy).
- To watch a reactive object's nested prop: use getter `() => obj.count` (watching `obj.count` directly won't work — passes a number).
- Options: `deep: true` (or `deep: N` in 3.5+ for max traversal depth), `immediate: true` (eager, runs before `created`), `once: true` (3.4+), `flush: 'pre'|'post'|'sync'`.
- `watchEffect(fn)` auto-tracks reactive deps used inside; no explicit source. `watchPostEffect` (post-flush), `watchSyncEffect` (sync).

## Pitfalls

- Adding a property to `this` or a plain object after creation is NOT reactive — declare all fields upfront (use `null`/`undefined` placeholders) or use `reactive()`/`ref()`.
- `Date.now()` / `Math.random()` in computed are not reactive deps → computed won't update.
- Do not mutate a computed return value (treat as read-only snapshot).
- Deep watchers on large structures are expensive — use sparingly.
- Async/sync-created watchers: create **synchronously** inside `setup()`/`<script setup>` so they bind to the component and auto-stop on unmount. Async-created watchers leak. Stop manually via the returned `unwatch()`.
