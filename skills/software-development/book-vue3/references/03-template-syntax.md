# Template Syntax

Distilled from vuejs.org/guide/essentials/{application,class-and-style,conditional,list,event-handling,forms,template-refs}.

## Text & Bindings

- Interpolation: `{{ expression }}` (declarative, JS-expression scope of the instance).
- `v-bind` / `:` — bind an attribute to JS expression. `:href="url"`. Without arg, `v-bind="obj"` binds all object props (last value wins; events merge via `onX` keys; class/style merge).
- `v-on` / `@` — attach event listener. `@click="handler"`.

## Conditional Rendering

- `v-if` / `v-else-if` / `v-else` — real conditional; block not rendered if false. Lazily renders on first truthy.
- `v-if` on `<template>` wraps multiple elements invisibly (result has no `<template>`).
- `v-show` — always renders; toggles `display` CSS only. No `<template>` support, no `v-else`.
- Choice: `v-if` higher toggle cost, `v-show` higher initial cost. Toggle often → `v-show`; rarely changes → `v-if`.
- `v-if` + `v-for` on same element is **not recommended** (precedence differs by version). Use a computed or `<template v-for>` wrapper.

## List Rendering

- `v-for="item in items"` (or `of`). Second alias for index: `(item, index) in items`. Destructuring works: `{ message } in items`.
- Object iteration: `(value, key)`, `(value, key, index)`. Order = `Object.values()`.
- Range: `v-for="n in 10"` (n starts at 1).
- **Always use `:key`** for `v-for` (primitive value, e.g. item id) so Vue can track identity, reorder/reuse DOM. Without key, in-place patch is efficient but wrong when child state matters.
- With component: `v-for` does NOT auto-pass data — also bind props: `:item="item" :key="item.id"`.
- Array mutation: `push/pop/shift/unshift/splice/sort/reverse` are detected. Non-mutating `filter/concat/slice` return new arrays — reassign: `items.value = items.value.filter(...)`.
- Filtered/sorted in computed; for `reverse()/sort()` in computed, copy first: `[...arr].sort()`.
- In-DOM templates: `v-for` with `v-if` precedence — avoid combining.

## Class & Style Bindings (special `v-bind` enhancements)

- `:class` accepts string, object `{ active: isActive }`, or array `['static', errorClass]`. Coexists with plain `class` (merged). Binding to a computed returning an object is a common pattern.
- Components: class on a single-root component merges into root; multi-root needs `$attrs.class` target.
- `:style` accepts object `{ color: activeColor, fontSize: size+'px' }` (camelCase or kebab-case keys) or array of objects. Coexists with plain `style`. Auto-prefixes vendor CSS. Arrays of values: `display: ['-webkit-box','flex']` (last supported wins).
- In-DOM templates must use `kebab-case` tags and explicit closing tags; SFCs allow `PascalCase` and self-closing.

## Event Handling

- Inline handler: `@click="count++"`. Method handler: `@click="greet"` (method receives native event as first arg).
- Call with args inline: `@click="say('hi')"`. Access native event via `$event` or arrow `@click="(e) => warn('x', e)"`.
- Compiler distinguishes method vs inline by whether the value is a valid identifier/path (`foo`, `foo.bar`) vs call/expression (`foo()`, `count++`).
- **Event modifiers** (dot postfix): `.stop`, `.prevent`, `.self`, `.capture`, `.once`, `.passive`. Order matters: `@click.prevent.self` vs `@click.self.prevent`.
- **Key modifiers**: `.enter`, `.tab`, `.delete`, `.esc`, `.space`, `.up/down/left/right`, plus any `KeyboardEvent.key` in kebab-case. **System modifiers**: `.ctrl .alt .shift .meta`. `.exact` for exact combo. Mouse: `.left .right .middle`.
- `.passive` + `.prevent` together is invalid (browser warning).

## Form Input Bindings (v-model)

- `v-model="text"` = `:value` + `@input` sugar. Auto-expands per element type.
- Text/textarea: `value` + `input`. Checkbox/radio: `checked` + `change`. Select: `value` + `change`.
- v-model ignores initial `value/checked/selected` HTML attrs — JS state is source of truth.
- Multiple checkboxes → bind array or `Set`. Select multiple → array.
- Modifiers: `.lazy` (sync on `change` not `input`), `.number` (parseFloat; auto on `type=number`), `.trim`.
- IME composition (CJK) doesn't update v-model mid-composition; handle raw input if needed.
- Component v-model: see references/04-components (defineModel).

## Template Refs

- `ref="myInput"` on element/component → access underlying DOM/instance after mount.
- Composition API (3.5+): `const input = useTemplateRef('my-input')`; before 3.5 declare `const input = ref(null)` matching name.
- Only available after mount; `undefined/null` on first render. Guard `watchEffect`: `if (input.value) ...`.
- On component: returns instance. `<script setup>` children are **private** — expose via `defineExpose({ a, b })`. `expose` option limits access for Options API.
- `v-for` + ref → array of elements (order not guaranteed). 3.5+ `useTemplateRef` or declare `ref([])`.
- Function refs: `:ref="(el) => {...}"` (null on unmount).
