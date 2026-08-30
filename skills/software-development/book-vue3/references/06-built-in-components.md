# Built-in Components

Distilled from vuejs.org/guide/built-ins/{transition,transition-group,keep-alive,teleport,suspense}.

## `<Transition>`

- Apply enter/leave animations when content enters/leaves the DOM. Built-in (no registration). Single root element/component only (component must have one root).
- Triggers: `v-if`, `v-show`, dynamic `<component>` switch, changing `key`.
- Mechanism: sniffs CSS transition/animation; adds/removes 6 classes at timing points; calls JS hooks if provided; else waits one animation frame.
- Transition classes (prefix `v-`, or `name`-prefixed e.g. `fade-`):
  - `*-enter-from` (start state), `*-enter-active` (duration/easing), `*-enter-to` (end state)
  - `*-leave-from`, `*-leave-active`, `*-leave-to`
- Named: `<Transition name="fade">` → classes `fade-enter-active` etc.
- CSS transitions: declare under `*-enter-active`/`*-leave-active`. Different durations/easings per direction allowed.
- CSS animations: declared under `*-enter-active`; `*-enter-from` removed on `animationend`.
- Custom classes (override defaults, e.g. Animate.css): `enter-from-class`, `enter-active-class`, `enter-to-class`, `leave-*`.
- JS hooks: `@before-enter`, `@enter`, `@after-enter`, `@enter-cancelled`, and `leave` equivalents — for JS-driven animation (Velocity.js etc.).
- Dynamic: `:name` can be reactive to switch transitions by state.
- `key` attribute forcing re-render: changing `:key` makes `<Transition>` animate between two distinct elements.

## `<TransitionGroup>`

- For lists (`v-for`): animate insert/remove/**move** of items. Renders a real element (default `<span>`; set `tag` prop).
- Each item needs its own `key`. Adds move transitions via FLIP (transform) when list reorders — needs `*-move` class (e.g. `transition: all 0.3s`).
- Supports `v-move` class; respects `transform` for smooth repositioning.
- Same class system as `<Transition>`; `name` prop prefixes.

## `<KeepAlive>`

- Cache inactive component instances across dynamic `<component :is>` switches (preserve state instead of unmount).
- `include` / `exclude` (comma-string, RegExp, or array) match component `name`; `<script setup>` auto-infers name from filename (3.2.34+).
- `max` (LRU cache: evict least-recently-used when exceeded).
- Cached instances use `onActivated`/`onDeactivated` (Composition) or `activated`/`deactivated` (Options) instead of mount/unmount — these also fire on mount/unmount.

## `<Teleport>`

- Render a template fragment to a DOM node **outside** the component's hierarchy (e.g. modals to `body`). Logical component relationship unchanged (props/events/inject still work; DevTools nesting unchanged).
- `<Teleport to="body">` — `to` is a CSS selector or DOM node; target must exist when Teleport mounts (or use `defer` in 3.5+ for later-in-tree targets).
- `:disabled="isMobile"` toggles: render inline vs teleported (e.g. overlay on desktop, inline on mobile).
- Multiple Teleports to same target append in order.
- Pairs with `<Transition>` for animated modals.

## `<Suspense>` (experimental)

- Orchestrate async dependencies in a component tree; show top-level loading while nested async resolve.
- Two async dependency types it waits on: components with async `setup()` (incl. `<script setup>` top-level `await`), and async components.
- Slots: `#default` (main) and `#fallback` (loading) — one immediate child node each.
- On initial render, renders default in memory; if async deps found → `pending` → show fallback; when resolved → `resolved` → show default. Reverts to pending only if `#default` root node is replaced.
- `timeout` prop: switch to fallback if new default takes > N ms (0 = immediate).
- Events: `pending`, `resolve`, `fallback`. Error handling via `onErrorCaptured`/`errorCaptured` (Suspense has no built-in error UI).
- Nesting with Router/Transition/KeepAlive: order matters — typical:

  ```vue
  <RouterView v-slot="{ Component }">
    <template v-if="Component">
      <Transition mode="out-in">
        <KeepAlive>
          <Suspense>
            <component :is="Component" />
            <template #fallback>Loading...</template>
          </Suspense>
        </KeepAlive>
      </Transition>
    </template>
  </RouterView>
  ```

- Nested Suspense (3.3+): add `<Suspense suspensible>` inside to handle patching of a nested async component without empty nodes.
