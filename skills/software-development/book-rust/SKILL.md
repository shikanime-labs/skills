---
name: book-rust
description: Distilled Rust Book and Reference knowledge base.
version: 0.1.0
author: Hermes
license: Apache-2.0
metadata:
  hermes:
    tags:
      - Rust
      - LanguageReference
      - SystemsProgramming
---

# Rust Docs (Distilled)

A distilled knowledge base of the two flagship Rust language documents:
**The Rust Programming Language** (the Book, edition 2024, assumes Rust
1.90.0+) and **The Rust Reference** (stable language spec). It captures the
central mental models and decision rules worth having in every Rust session.

This skill does NOT replace the standard library docs (`std`), Cargo internals,
`rustc` details, or nightly/unstable features. Those are out of scope and are
linked to their canonical URLs in [Pitfalls](#pitfalls). It also does not
contain copy-paste source text — it is structured notes *about* the docs.

No code execution is required. Live doc lookups use `web_extract` against
`doc.rust-lang.org`; local installs can serve docs offline via `terminal`
(`rustup doc --book`).

## When to Use

- "How does Rust ownership / borrowing / a move work?"
- "What's the rule for mutable vs immutable references?"
- "Explain `Send`, `Sync`, lifetimes, variance, or type coercions."
- "How do `Box`, `Rc`, `RefCell`, `Arc`, `Mutex` differ?"
- "When should I use `Result` vs `panic!`?"
- "How do slices, patterns, traits, or generics behave?"
- "What does `unsafe` permit / not permit?"
- "How do modules, `use`, crates, and Cargo workspaces work?"

## Prerequisites

- Network access for `web_extract` (to fetch live docs when a reference file
  does not already cover the question).
- Optional: a Rust toolchain via `rustup` for offline docs
  (`rustup doc --book`, `rustup doc --std`).

## How to Run

1. Load the relevant chapter on demand with `skill_view`
   (file_path="references/<file>.md") — see the Index below. Each file is
   self-contained; only load what the question needs.
2. If the question spans an area not yet covered, fetch the source chapter with
   `web_extract` from `https://doc.rust-lang.org/book/<path>.html` or
   `https://doc.rust-lang.org/reference/<path>.html`, then synthesize.
3. For std/Cargo/rustc specifics, go straight to the canonical URLs in
   [Pitfalls](#pitfalls) — do not guess from memory.

## Quick Reference

- Book TOC: `https://doc.rust-lang.org/stable/book/` (offline: `rustup doc --book`)
- Reference TOC: `https://doc.rust-lang.org/reference/`
- std docs: `https://doc.rust-lang.org/std/`
- Cargo book: `https://doc.rust-lang.org/cargo/`
- rustc book: `https://doc.rust-lang.org/rustc/`
- Unstable book (nightly only): `https://doc.rust-lang.org/nightly/unstable-book/`
- Edition in effect: **2024** (`edition = "2024"` in `Cargo.toml`).

## Core Mental Models

**Ownership (the foundation).** Every value has exactly one owner; the owner
drops the value when it goes out of scope. Heap-allocating types (`String`,
`Vec`, `Box`, etc.) move on assignment/argument-pass; stack-only `Copy` types
(`i32`, `bool`, `f64`, `char`, `(i32,i32)`, …) are copied instead. Rust never
deep-copies automatically (`clone()` is the explicit, visible deep copy).

**Borrowing.** `&T` borrows immutably, `&mut T` borrows mutably. At any instant
you may hold *either* one mutable borrow *or* any number of immutable borrows,
never both. References must always be valid (no dangling) — the compiler
enforces this via lifetimes.

**Slices.** `&str` / `&[T]` are non-owning views of a contiguous range. Prefer
`&str` over `&String` (and `&[T]` over `&Vec<T>`) as function parameters for
generality.

**Send / Sync (concurrency safety).** `Send` = safe to move to another thread;
`Sync` = safe to share a reference (`&T`) across threads. The compiler uses
these traits to forbid data races at compile time.

**Trait vs type.** Traits define shared behavior (like interfaces); types
implement them. `impl Trait` / trait objects (`dyn Trait`) are the two
abstraction paths. Derive `#[derive(...)]` for common built-ins
(`Debug`, `Clone`, `Copy`, `Default`, …).

## Procedure

1. Identify the question's area (ownership, types, traits, concurrency, …).
2. Load the matching `references/` file via `skill_view`.
3. If uncovered, fetch the precise Book/Reference chapter via `web_extract`
   and answer from the source.
4. For library APIs (std), link/quote `std` docs, not the Reference
   (the Reference deliberately excludes std).

## Pitfalls

- **Edition matters.** Current docs assume **Edition 2024**. `let...else`,
  `if let` chains, and other newer syntax may not exist in 2015/2018/2021
  editions. Check `Cargo.toml` `edition`.
- **Reference ≠ std.** The Rust Reference does *not* document the standard
  library; many "features" are library features (`Vec`, `Rc`, `Mutex`, …).
  Use `https://doc.rust-lang.org/std/` for those.
- **Book ≠ Reference scope.** The Book is a tutorial (background assumed for
  the Reference). Don't cite the Book as a normative language spec.
- **Stable only.** The Reference covers stable Rust. Unstable features live in
  the Unstable Book and require nightly.
- **`Copy` and `Drop` are mutually exclusive.** A type cannot be both.
- **Mutable XOR shared.** A `&mut T` excludes all other live borrows for its
  lifetime; this is what prevents data races, not a quirk to workaround.
- **Slice indices must be valid UTF-8 boundaries** for `&str`; mid-character
  slicing panics.

## Verification

Load a reference file and confirm it renders: run
`skill_view(name="book-rust", file_path="references/ownership-borrowing.md")`
and expect structured notes (not raw source) about the ownership rules.

## Index (load on demand)

- `references/ownership-borrowing.md` — ownership rules, move vs copy,
  references, borrowing rules, slices, dangling refs, drop. Load when: "what
  is a move / borrow / slice?", lifetime-of-scope questions.
- `references/traits-generics-lifetimes.md` — generics, trait definitions,
  trait bounds, trait objects, lifetime elision, variance/coercions basics.
  Load when: "how do traits / generics / lifetimes work?".
- `references/types-coercions.md` — value categories, `Copy`, `Sized`/DST
  (`?Sized`), `String` vs `&str`, numeric/char types, type coercions,
  subtyping. Load when: "why is this type unsized / what coerces to what?".
- `references/smart-pointers.md` — `Box`, `Rc`/`Arc`, `RefCell`, `Cell`,
  `Drop`, interior mutability, reference cycles. Load when: "which smart
  pointer do I use?".
- `references/concurrency.md` — threads, message passing, shared state,
  `Mutex`/`Arc`, `Send`/`Sync`. Load when: "how do I do X concurrently / safe
  across threads?".
- `references/error-handling.md` — `panic!` vs `Result`, `?`, `unwrap`/`expect`,
  when to panic. Load when: "recoverable vs unrecoverable error?".
- `references/patterns-matching.md` — `match`, `if let`, refutability, pattern
  syntax, places patterns are used. Load when: "pattern matching / exhaustiveness?".
- `references/unsafe-macros-advanced.md` — `unsafe` rules, undefined behavior,
  `unsafe fn`/`unsafe trait`, declarative & procedural macros. Load when:
  "what does unsafe allow / how do macros work?".
- `references/modules-cargo.md` — packages/crates/modules, `use`, paths,
  privacy, Cargo workspaces, profiles, publishing. Load when: "module
  visibility / Cargo project structure?".
- `references/appendices-glossary.md` — keywords, operators/symbols, derivable
  traits, editions. Load when: "what does this keyword / operator mean?".
