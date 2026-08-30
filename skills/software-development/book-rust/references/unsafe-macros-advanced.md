# Unsafe Rust and Macros

Source: *The Rust Programming Language* Ch. 20 (Unsafe Rust, Macros);
*The Rust Reference* `unsafety.md`.

## Unsafe Rust

- "A second language hidden inside Rust" — does **not** enforce memory-safety
  guarantees at compile time. Used for operations the static analyzer can't
  prove safe (conservative by nature) and for low-level/HW interaction.
- `unsafe { ... }` block (or `unsafe fn`) — only grants access to five
  **superpowers**; it does NOT disable the borrow checker or other safety
  checks on references. Keep `unsafe` blocks small and infrequent.
- Best practice: wrap unsafe code in a **safe abstraction** with a safe API
  (much of std is a safe wrapper over audited unsafe code). Callers use the
  safe API; any memory-safety bug must be inside an `unsafe` block.

### The five unsafe superpowers

1. **Dereference a raw pointer** (`*const T`, `*mut T`).
2. **Call an unsafe function or method**.
3. **Access or modify a mutable `static` variable**.
4. **Implement an `unsafe trait`**.
5. **Access fields of a `union`**.

(The Reference also lists: reading/writing a mutable or unsafe external
`static`; calling a safe fn lacking a matching `target_feature`; declaring an
`extern` block — which requires `unsafe` since Edition 2024; applying an
unsafe attribute.)

### Raw pointers

- `*const T` (immutable) / `*mut T` (mutable). The `*` is part of the type
  name, not the dereference operator.
- Unlike references: may ignore borrowing rules (multiple mutable to one
  location), aren't guaranteed valid, may be null, have no auto-cleanup.
- Create with raw borrow operators `&raw const x` / `&raw mut x` (preferred
  over `as` casts). You can build raw pointers in **safe** code, but
  **dereferencing** requires `unsafe`.
- Casting integers to pointers and dereferencing is undefined behavior.

### Unsafe functions

- Declared `unsafe fn name(...) { ... }`. Callers must invoke within an
  `unsafe` block, asserting they've read the docs and uphold the contract.
- Inside an `unsafe fn`, you still need `unsafe { }` blocks for the actual
  superpower operations (compiler warns if forgotten) — keeps unsafe minimal.

### Verification tooling

- **Miri** (dynamic UB detector): `rustup +nightly component add miri`, then
  `cargo +nightly miri run` / `cargo +nightly miri test`. Catches many (not
  all) UB cases at runtime. If Miri flags a bug, it's real; if it doesn't,
  that doesn't prove safety.
- Deep reference: *The Rustonomicon*.

## Macros

- Rust's metaprogramming family: code that writes code (expands at compile
  time). Two big kinds: **declarative** (`macro_rules!`) and **procedural**
  (three subtypes).
- Differences from functions: variable arity (`println!("{}", a)` vs
  `println!("hi")`); expanded *before* the compiler interprets meaning, so can
  implement traits/derive; must be defined/brought into scope **before** use
  (unlike functions).

### Declarative macros (`macro_rules!`)

- Pattern-match against **code structure** (like `match` on syntax).
- `#[macro_export]` makes it reachable when the crate is in scope.
- Syntax: `macro_rules! name { ( $($x:expr),* ) => { /* $x replaced per match */ } }`.
  - `$x:expr` matches any expression, binds it to `$x`.
  - `$( ... ),*` = comma-separated zero-or-more repetition.
- `vec![1,2,3]` expands to `{ let mut v = Vec::new(); v.push(1); v.push(2);
  v.push(3); v }`.

### Procedural macros (attribute, derive, function-like)

- Accept a `TokenStream` (from `proc_macro` crate) and return a `TokenStream`.
  Must live in their own crate with crate-type `proc-macro`.
- **Custom `#[derive]`**: `#[proc_macro_derive(Name)]` — generates
  trait impls for structs/enums; e.g. `#[derive(HelloMacro)]`.
- **Attribute-like**: `#[proc_macro_attribute]` — arbitrary new attributes
  (e.g. `#[route(GET, "/")]`), applicable to more items than derive (incl.
  functions).
- **Function-like**: `#[proc_macro]` — look like function calls
  (e.g. `sql!(SELECT ...)`), take unknown arg count.
- Building them usually uses `syn` + `quote` crates for parsing/codegen.

## Cross-links

- `unsafe` + `Send`/`Sync` manual impl (concurrency traits):
  `references/concurrency.md`.
- `derive` attribute and derivable traits:
  `references/appendices-glossary.md`.
- Edition 2024 extern-block `unsafe` requirement:
  `references/appendices-glossary.md`.
