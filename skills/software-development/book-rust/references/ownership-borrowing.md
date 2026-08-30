# Ownership, Borrowing, and Slices

Source: *The Rust Programming Language* Ch. 4 (Understanding Ownership).
Reference: `memory-model.md`, `memory-allocation-and-lifetime.md`,
`variables.md`, `expressions.md#temporaries`.

## Ownership rules (the three axioms)

- Each value in Rust has exactly one **owner**.
- There can be only one owner at a time.
- When the owner goes out of scope, the value is **dropped** (freed).

Ownership is enforced at compile time; it imposes zero runtime cost.

## Why ownership exists: stack vs heap

- **Stack**: fixed-size, known-at-compile-time values; LIFO push/pop; very fast.
- **Heap**: allocator finds a free block, returns a pointer; access is slower
  (pointer chase) and allocation is more work.
- Ownership's primary job is tracking and cleaning up **heap** data.

## Move vs Copy (the central distinction)

- **Move** (heap-owning types: `String`, `Vec`, `Box`, etc.): assignment or
  argument-passing copies only the stack "bookkeeping" (pointer, length,
  capacity) — *not* the heap data — then **invalidates the source**. This
  prevents a double-free.
  - `let s2 = s1;` moves `s1` into `s2`; using `s1` afterward is a compile error.
- **Copy** (stack-only `Copy` types: `i32`, `bool`, `f64`, `char`, tuples of
  `Copy` such as `(i32, i32)`): value is trivially copied; source stays valid.
  - `Copy` is a trait. A type may **not** be `Copy` if it (or any part)
    implements `Drop`. (The two are mutually exclusive.)
- `clone()`: the explicit, **visible** deep copy of heap data. Presence is a
  signal that arbitrary (possibly expensive) code runs.
- Reassigning a variable drops the old value immediately.

## Ownership and functions

- Passing a value to a function moves or copies it exactly like assignment.
- Returning a value transfers ownership back to the caller.
- The pre-reference workaround was returning tuples `(value, other)` to keep
  using inputs — verbose, and replaced by references.

## References = borrowing

- `&T`: immutable borrow — refer without owning; no `drop` when the borrow ends.
- `&mut T`: mutable borrow.
- Unlike raw pointers, a reference is **guaranteed valid** for its lifetime.
- References are immutable by default, like variables.

## The borrowing rules (core invariant)

- At any instant you may hold **either** one mutable reference **or** any number
  of immutable references — **never both**.
- References must always be valid (no dangling).
- A reference's scope runs from where it is introduced to its **last use**
  (NLL-style), so non-overlapping borrows compile even in the same block.

## Why the mutable-borrow restriction exists

It prevents **data races** at compile time. A data race requires all three:

- two or more pointers to the same data at the same time,
- at least one writing,
- no synchronization.
Curly-brace scopes permit multiple mutable borrows as long as they are not
live simultaneously.

## Dangling references

The compiler forbids dangling refs. Returning a reference to a local that is
dropped on return → compile error ("borrowed value … no value to borrow from").
Fix: return the owned value (move it out) rather than a reference.

## Slices (`&str`, `&[T]`)

- A slice is a non-owning view of a contiguous range of a collection.
- `&str` (string slice): `&s[start..end]` where end is exclusive.
  Shorthands: `..2`, `3..`, `..` (whole). Range must fall on valid UTF-8
  character boundaries, else panic.
- String literals `"..."` are `&str` (immutable reference into the binary).
- Prefer `&str` over `&String` as a parameter: it accepts both literals and
  `String` (via deref coercion, Ch. 15).
- Array slice `&[i32]` uses the same mechanism; `Vec` slices (`&[T]`) follow in
  Ch. 8.
- Slices tie the reference lifetime to the underlying data, so the compiler
  rejects use-after-mutation bugs at compile time.

## Drop / cleanup

- `drop` runs automatically at the end of scope (analogous to C++ RAII).
- Assigning a fresh value to a variable drops the previous value immediately.

## Cross-links

- Deref coercions: Ch. 15 (`Deref` trait) → `references/smart-pointers.md`.
- Lifetime syntax: Ch. 10-03 → `references/traits-generics-lifetimes.md`.
- Deriving `Copy`: Appendix C → `references/appendices-glossary.md`.
