# Modules, Crates, and Cargo

Source: *The Rust Programming Language* Ch. 7 (Packages, Crates, Modules,
Paths, `use`, `pub`) and Ch. 14 (More about Cargo).

## Crates and packages

- **Crate**: the smallest unit the compiler considers at once. Two forms:
  - *Binary crate*: has `main`, compiles to an executable.
  - *Library crate*: no `main`, shares functionality (`rand`, `std`, ...). When
    Rustaceans say "crate" they usually mean a library crate.
- **Crate root**: the file the compiler starts from — `src/main.rs` (binary)
  or `src/lib.rs` (library). It forms the root module named `crate`.
- **Package**: a bundle of ≥1 crates with a `Cargo.toml`. At most **one**
  library crate; any number of binary crates. `cargo new` creates a binary by
  default; add `src/lib.rs` for a library; `src/bin/*.rs` are extra binaries.

## Modules — the cheat sheet

- **Start from the crate root**: compiler reads `src/lib.rs` or `src/main.rs`.
- **Declare a module**: `mod garden;` in the crate root. Compiler looks for:
  inline `{ ... }`, `src/garden.rs`, or `src/garden/mod.rs`.
- **Declare a submodule**: `mod vegetables;` inside `src/garden.rs`. Looks in
  `src/garden/vegetables.rs` or `src/garden/vegetables/mod.rs`.
- **Paths**: once a module is in the crate, refer to items via path, e.g.
  `crate::garden::vegetables::Asparagus` (privacy permitting).
- **Private vs public**: items are **private to their parent module by
  default**. `pub mod` makes the module public; `pub` on inner items makes
  those public. Making a module public does NOT make its contents public.
- **`use`**: creates a shortcut to a path within a scope to avoid repetition.

## Privacy rules (key)

- Parent modules cannot use private items of child modules; children CAN use
  ancestors' items. Privacy is the default; `pub` opts in.
- `pub struct Foo` makes the struct public but **fields stay private** unless
  individually `pub`. `pub enum` makes **all variants public** (enums are
  rarely useful otherwise).
- A binary+library package should keep the module tree in `src/lib.rs`; the
  binary crate uses the library via the package name as an external user would.

## Paths

- **Absolute**: from crate root; `crate::...` for local, or the crate name for
  external (e.g. `std::collections::HashMap`).
- **Relative**: from current module using `self`, `super`, or an identifier.
  `super` = parent module (useful when items move together).
- Book recommends **absolute paths** generally (survive moving item calls
  independently of definitions).

## `use` keyword

- `use crate::garden::vegetables::Asparagus;` then refer to `Asparagus`.
  Scoped to where it appears (won't apply in sibling modules).
- **Idiom**: for functions, bring the *parent module* into scope
  (`use crate::front_of_house::hosting;` then `hosting::add_to_waitlist()`) so
  calls read as non-local. For structs/enums/other items, bring the full path
  (`use std::collections::HashMap;`).
- **`as`**: rename on import to resolve name clashes
  (`use std::io::Result as IoResult;`).
- **`pub use`** = re-export: makes an item available to outside scopes as if
  defined there (reshapes the public API independently of internal layout).
- **Nested paths**: `use std::io::{self, Write};` reduces vertical space.
- **Glob** `use std::collections::*;` imports all public items — use
  sparingly (obscures where names come from; breaks on dependency changes).

## External packages

- Add to `Cargo.toml` `[dependencies]` (e.g. `rand = "0.8"`). `cargo` fetches
  from crates.io. Then `use rand::prelude::*;` etc.
- `std` is also a crate: no `Cargo.toml` entry, but you still `use` it.

## Cargo project management (Ch. 14 highlights)

- **Release profiles** (`[profile.release]`, `[profile.dev]`): tune
  `opt-level`, `debug`, `lto`, `codegen-units`, `panic = "abort"`.
- **Publishing**: `cargo publish` to crates.io; needs `Cargo.toml`
  metadata (name, version, edition, description, license, authors).
- **Workspaces**: a `Cargo.toml` with `[workspace]` and `members = [...]`
  sharing one `Cargo.lock` and target dir across multiple crates.
- **`cargo install`**: installs binary crates globally.
- **Custom commands**: `cargo-<name>` on PATH is invokable as `cargo name`.
- **`cargo new --lib` / `cargo new <name>`**; `cargo build`, `cargo run`,
  `cargo test`, `cargo doc`, `cargo publish`.

## Cross-links

- `pub` + privacy interacts with trait impls: `references/traits-generics-lifetimes.md`.
- `mod`/`pub` keywords: `references/appendices-glossary.md`.
