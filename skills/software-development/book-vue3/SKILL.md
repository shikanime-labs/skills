---
name: book-vue3
description: "Vue 3 guide distilled: reactivity, components, composables."
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes.tags: [Vue, Frontend, JavaScript, Components]
  hermes.related_skills: [book-nix, devlib-rumdl-ci]
---

# Vue 3 Docs (Distilled)

Structured notes distilled from the official Vue 3 documentation (vuejs.org/guide).
Covers the core mental models and patterns an engineer needs to author and
review Vue 3 applications: reactivity, template syntax, components, the
Composition API, built-in components, scaling-up patterns, and best practices.

It does NOT reproduce the full API reference verbatim — use
`references/09-api-quick-reference.md` for the high-traffic surface and the live
docs for exhaustive signatures. Source is Vue 3 (Vue 2 reached EOL on 2023-12-31).

## When to Use

- "Build a Vue 3 component / SFC that does X"
- "Why isn't this reactive / why didn't the DOM update?"
- "How do props, emits, slots, or v-model work in Vue 3?"
- "Refactor this Options API code to `<script setup>` / Composition API"
- "Extract this stateful logic into a composable"
- "How do I route / manage state / lazy-load a component in Vue?"

## Prerequisites

- Node.js + a build tool (Vite is the recommended default for SFCs).
- For SFCs, a Vue-aware build step (Vite + `@vitejs/plugin-vue` or `vue-cli`).
- Official docs root: `https://vuejs.org/guide/`. API reference:
  `https://vuejs.org/api/`. Style guide: `https://vuejs.org/style-guide/`.
- No special env vars. Reference files are loaded on demand with `skill_view`.

## How to Run

1. Load this SKILL.md (always in context when the skill is active).
2. When a question matches a topic below, load the specific reference with:
   `skill_view(name="book-vue3", file_path="references/<file>")`.
3. Apply the patterns and verify against the live docs for exact signatures.

## Quick Reference

- Create app: `createApp(RootComponent).mount('#app')`
- Reactive primitive: `ref(0)` → access via `.value`; auto-unwrapped in templates.
- Object/array reactive state: `reactive(obj)` (deep proxy, no `.value`).
- Derived: `computed(() => ...)`, `watch(src, cb, opts)`, `watchEffect(fn)`.
- Template binding: `{{ }}` text, `:prop` / `v-bind`, `@event` / `v-on`,
  `v-if` / `v-else-if` / `v-else`, `v-for`, `v-model`, `v-show`.
- SFC script: `<script setup>` (compile-time macro scope).
- Props/emits in `<script setup>`: `defineProps()`, `defineEmits()`.
- Composable convention: function name starts with `use`.

## Procedure

1. Identify the topic (reactivity, component, lifecycle, routing, state...).
2. Load the matching `references/` file via `skill_view`.
3. Apply the pattern; prefer Composition API + `<script setup>` for apps.
4. For exact API shapes not in the reference, open the live docs URL noted.
5. Reconcile against the style guide for production code.

## Pitfalls

- Adding a property to `this` (Options API) or a plain object is NOT reactive;
  declare all reactive fields upfront, or use `reactive()` / `ref()`.
- `ref()` needs `.value` in JS but NOT in templates (except nested non-top-level).
- Mutating `props` is forbidden — emit an event or use `v-model`.
- `reactive()` proxies: the original object is NOT made reactive; always access
  state through the proxy, never the raw object.
- In-DOM templates must use `kebab-case` and explicit closing tags; SFCs allow
  `PascalCase` and self-closing.
- `v-for` with `v-if` on the same element: `v-if` no longer has priority over
  `v-for` in Vue 3 — avoid combining; use a computed or `<template v-for>`.

## Verification

- Load a reference and confirm the pattern matches the live docs section:
  `skill_view(name="book-vue3", file_path="references/02-reactivity.md")`
  returns the reactivity mental model without inventing APIs.

## Reference Index

Load on demand with `skill_view(name="book-vue3", file_path="references/<file>")`:

- `references/01-getting-started.md` — What Vue is, progressive adoption, SFC,
  Options vs Composition API. Load when starting a project or explaining Vue.
- `references/02-reactivity.md` — `ref`, `reactive`, `computed`, `watch`,
  `watchEffect`, reactivity caveats. Load on reactivity/state questions.
- `references/03-template-syntax.md` — Interpolation, bindings, conditionals,
  lists, events, forms, class/style. Load on template authoring.
- `references/04-components.md` — Props, events/emits, slots, fallthrough attrs,
  provide/inject, async components. Load on component design.
- `references/05-composition-api.md` — `<script setup>`, composables, lifecycle,
  template refs. Load when refactoring to Composition API.
- `references/06-built-in-components.md` — Transition, TransitionGroup,
  KeepAlive, Teleport, Suspense. Load on animation/portal/lazy UI.
- `references/07-scaling-up.md` — SFC deep dive, routing, Pinia state, testing,
  SSR. Load when structuring a full app.
- `references/08-best-practices.md` — Style guide priorities, performance,
  security, accessibility. Load on code review / hardening.
- `references/09-api-quick-reference.md` — High-traffic API surface: directives,
  special attributes, global/composition/options entry points. Load for signatures.
- `references/glossary.md` — Terms and chapter cross-refs. Load to disambiguate.
