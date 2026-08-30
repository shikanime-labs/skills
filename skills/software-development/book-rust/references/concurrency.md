# Fearless Concurrency

Source: *The Rust Programming Language* Ch. 16 (Fearless Concurrency).

## Threading model

- Rust's standard library uses a **1:1 model**: one OS thread per language
  thread. (`async`/await, Ch. 17, is a different approach; other models exist
  in crates.)
- Thread risks: race conditions, deadlocks, hard-to-reproduce bugs. Rust
  mitigates via the type system + ownership, not by banning threads.

## Spawning threads

- `thread::spawn(closure)` → returns `JoinHandle<T>`.
- **Warning**: when the main thread ends, all spawned threads are shut down,
  finished or not. Save the handle and call `.join()` to block until the
  thread finishes. (`handle.join()` blocks the calling thread.)
- Use `move` closures with `thread::spawn`: the closure takes ownership of
  captured environment values, transferring them to the new thread. Without
  `move`, Rust infers a borrow and rejects it (it can't prove the reference
  outlives the thread). `move` overrides the conservative borrow default but
  still obeys ownership rules (you can't then use the moved value in the
  original thread).

## Message passing ("do not communicate by sharing memory")

- `use std::sync::mpsc;` → `let (tx, rx) = mpsc::channel();`
  - `mpsc` = **multiple producer, single consumer**.
  - `tx.send(value)` returns `Result` (errors if the receiver was dropped).
  - `rx.recv()` blocks until a value arrives; returns `Result`; errors when the
    transmitter is closed. `rx.try_recv()` returns immediately (`Ok`/`Err`).
  - `rx` is iterable: `for received in rx { ... }` ends when the channel closes.
  - `mpsc::Sender` is cloneable for multiple producers (`tx.clone()`).
- **Ownership transfer**: `send` takes ownership of its argument; the receiver
  takes ownership on receipt. You cannot use a value after sending it — the
  compiler rejects it (a concurrency bug caught at compile time).

## Shared-state concurrency

- Like multiple ownership (Ch. 15): multiple threads access the same memory.
- **`Mutex<T>`** (mutual exclusion): only one thread may access the data at a
  time. Rules enforced by the type system:
  1. Acquire the lock before using the data (`let mut num = m.lock().unwrap();`).
  2. The lock is released automatically when the `MutexGuard` goes out of scope
     (`MutexGuard` implements `Deref` + `Drop`). You can't forget to unlock.
  - `lock()` blocks the current thread; returns `LockResult<MutexGuard<T>>`. If
    the holder panicked, `lock()` fails (we `unwrap`/panic in that case).
- **`Rc<T>` is NOT thread-safe** — its ref-count updates aren't atomic. Using
  it across threads fails to compile: `` `Rc<Mutex<i32>>` cannot be sent between
  threads safely `` (no `Send`). Use `Arc<T>` instead.
- **`Arc<T>`** = atomically reference-counted; same API as `Rc<T>` but
  thread-safe. Wrap `Mutex<T>` in `Arc<T>` to share mutable state across threads:
  `Arc::clone(&counter)` into each thread.
- `Mutex<T>`/`Arc<T>` mirrors `RefCell<T>`/`Rc<T>` (interior mutability).
  `Mutex<T>` also risks **deadlocks** (two threads each hold one of two locks
  and wait on the other). `std::sync::atomic` offers simpler atomic primitives
  for plain counters.

## `Send` and `Sync` (the language-level concurrency traits)

- **`Send`**: ownership of a value of the type can be transferred between
  threads. Almost every type is `Send`; exceptions include `Rc<T>` (concurrent
  ref-count updates would race) and raw pointers. Any type composed entirely of
  `Send` types is automatically `Send`.
- **`Sync`**: it is safe to have a reference (`&T`) to the type from multiple
  threads. Formally, `T: Sync` iff `&T: Send`. Primitive types are `Sync`;
  `Rc<T>`, `RefCell<T>`, and the `Cell<T>` family are **not** `Sync` (runtime
  borrow-checking isn't thread-safe). `Mutex<T>` **is** `Sync`.
- Both are `std::marker` **marker traits** — auto-derived for types made of
  `Send`/`Sync` parts; they have no methods. The compiler uses them to forbid
  data races at compile time.
- **Manually implementing `Send`/`Sync` is `unsafe`** (requires upholding
  non-trivial guarantees; see *The Rustonomicon*).

## Key takeaways

- Prefer message passing (channels) by default; use `Arc<Mutex<T>>` for shared
  mutable state.
- If code compiles, it is free of data races and invalid references across
  threads — the borrow checker + `Send`/`Sync` guarantee it.
- Most concurrency tooling lives in crates (which evolve faster than std).

## Cross-links

- `move`, closures: `references/patterns-matching.md` (Ch. 13).
- `Rc`/`RefCell`/`Arc`: `references/smart-pointers.md`.
- `unsafe`: `references/unsafe-macros-advanced.md`.
