# Best Practices & Style Guide

Distilled from vuejs.org/style-guide and guide/extras (security, performance, accessibility notes).

## Rule Categories (Style Guide)

- **Priority A — Essential (error prevention):** obey at all costs.
- **Priority B — Strongly Recommended:** readability/DX; rare, justified deviations only.
- **Priority C — Recommended:** pick one option for consistency (community standard helps parsing/copy-paste).
- **Priority D — Use with Caution:** features for edge cases/migrations; overuse → bugs.

## Essential (Priority A) — key rules

- **Multi-word component names** (except root `App`, built-ins, `<svg>`/`<transition>`): avoids clashing with HTML elements.
- **Prop definitions:** specify types; required for clarity/validation.
- **Keyed `v-for`** (primitive `key`, e.g. `item.id`): correct DOM reuse/reorder.
- **No `v-if` with `v-for` on same element** (precedence ambiguity); use computed or `<template v-for>`.
- **Component `data` must be a function** returning fresh object (per-instance state).
- **No mutating props** — emit events / use `v-model` / `defineModel`.
- **Use of `v-for` index as key** is discouraged when list can reorder.
- **Scoped styles** for component CSS (`scoped` or CSS modules) to avoid leaks.
- **Private/non-reactive instance properties** prefixed `_` / `$` avoided for user props.

## Strongly Recommended (Priority B)

- **Single-file components** for everything non-trivial.
- **Filename casing:** PascalCase or kebab-case consistently; SFCs use PascalCase or kebab.
- **Base component (presentational) prefix** `Base`/`App`/`V` for UI primitives.
- **Tightly coupled component names** share a prefix.
- **Ordering** within `<script>`: tags (top) → options (template, script, style) consistently. Options API option order: `data` → `computed` → `methods` → `watch` → lifecycle.
- **Quoted attribute values** when they contain spaces; **directive shorthands** `:` and `@` consistently.
- **Simple computed** over complex inline template expressions.

## Use with Caution (Priority D)

- **`v-if`/`v-for` together** — avoid (see above).
- **`scoped` + element selectors** are costly; prefer class selectors.
- **Implicit parent-child communication** via `$parent`/`$children` / mutating props — use props/emits/`provide-inject`/`Pinia`.
- **Non-flux state management** / global mutable state — prefer Pinia.
- **`this.$refs` in templates** and **`watch` over computed** for derived state.
- **`v-html`** — XSS risk; only with trusted content.

## Performance

- Use `v-once` for static content that never changes (render once, skip patching).
- Use `v-memo` to memoize part of a template by dependency array (expensive lists).
- `computed` over `methods` to avoid re-running on every render.
- Functional components only when genuinely stateless (rare in Vue 3).
- Lazy-load routes (dynamic import) and async components; `<KeepAlive>` for preserved state.
- Avoid deep `watch` on large objects; prefer targeted getters.

## Security

- **Never use `v-html` with untrusted/user input** — XSS. Sanitize server-side or use a vetted library; prefer template interpolation `{{ }}` (auto-escaped).
- Never build URLs from unsanitized input; validate/encode route params and `src`/`:href` bindings.
- SSR: avoid module-singleton shared state (cross-request pollution) — create per-request.
- Keep `app.config.globalProperties` minimal; don't expose secrets to client bundles.

## Accessibility

- Use semantic HTML; bind `:aria-*` and `role` via `v-bind` like any attribute.
- Associate form inputs with `<label for>`; manage focus on route change / modal open (Teleport + focus trap).
- Respect `prefers-reduced-motion` when using `<Transition>`/animations.
- Color contrast in scoped styles; don't rely on color alone.
