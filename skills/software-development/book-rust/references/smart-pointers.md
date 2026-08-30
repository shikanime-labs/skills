# Smart Pointers

Source: *The Rust Programming Language* Ch. 15 (Smart Pointers).

## What makes a type a "smart pointer"

- Implements `Deref` (so `*` works like a reference) and `Drop` (cleanup on
  scope exit). Enables RAII-style resource management without manual frees.

## `Box<T>`

- `Box<T>` allocates on the heap; the stack holds only the pointer. No extra
  capabilities, no overhead beyond heap storage.
- Use cases:
  1. **Recursive types**: a value whose size isn't known at compile time. Boxes
     have a known size (a pointer), breaking infinite-recursion. Classic example
     is a cons list: `enum List { Cons(i32, Box<List>), Nil }`. Without the
     box you get "has infinite size".
  2. **Large data, move without copy**: moving ownership copies only the small
     pointer, not the heap data.
  3. **Trait objects**: own a value that implements a trait without naming the
     concrete type (`Box<dyn Trait>`, Ch. 18).
- `Box<T>` derefs to its inner value; on drop, frees both the box and the heap
  data.

## `Deref` trait

- Customizes the `*` (dereference) operator. Required method:
  `fn deref(&self) -> &Self::Target;` (with associated type `Target`).
- When you write `*y`, Rust expands to `*(y.deref())`. `deref` returns a
  reference (not the value) to avoid moving out of `self`.
- **Deref coercion**: converts `&T` → `&U` automatically when
  `T: Deref<Target=U>`, at function/method call sites, with no runtime cost
  (resolved at compile time). Allows `&String`/`&Box<String>` to be passed
  where `&str` is expected. Chainable (e.g. `&MyBox<String>` → `&String` →
  `&str`).
- `DerefMut` for `&mut T` → `&mut U`. Three coercion cases:
  1. `&T` → `&U` (`T: Deref<Target=U>`)
  2. `&mut T` → `&mut U` (`T: DerefMut<Target=U>`)
  3. `&mut T` → `&U` (`T: Deref<Target=U>`)
  Mutable → immutable is allowed; immutable → mutable is **not** (borrow rules).

## `Drop` trait

- `fn drop(&mut self)` runs when a value goes out of scope. In the prelude; no
  `use` needed. Variables drop in **reverse** order of creation.
- Used for releasing files, sockets, locks, heap memory, etc. The ownership
  system guarantees `drop` runs exactly once.
- **You cannot call `drop` manually** (would double-free with the automatic
  call). To drop *early*, use `std::mem::drop(value)` (in the prelude).

## `Rc<T>` (reference counting) — single-threaded

- Enables **multiple ownership** of the same heap data via a reference count.
  `Rc::clone(&a)` increments the count (cheap — only the count, not a deep
  copy); `Drop` decrements automatically. When count hits 0, the value is
  freed.
- Convention: use `Rc::clone(&a)` (not `a.clone()`) to distinguish ref-count
  increments from expensive deep clones.
- Inspect count with `Rc::strong_count(&a)`. (Also `weak_count` via `Weak<T>`
  to break reference cycles.)
- **Single-threaded only.** Not `Send`/`Sync` — its non-atomic count updates
  would race. For threads use `Arc<T>`.

## `RefCell<T>` (interior mutability) — single-threaded

- **Interior mutability**: mutate data even through an immutable reference.
  Uses `unsafe` internally but exposes a safe API; borrow rules enforced at
  **runtime** instead of compile time.
- With `Box<T>`/`&`: borrow rules checked at **compile time** (error or
  fine). With `RefCell<T>`: checked at **runtime** — violation **panics** with
  `BorrowMutError` instead of a compile error.
- APIs: `borrow()` → `Ref<T>`, `borrow_mut()` → `RefMut<T>` (both `Deref`).
  Tracks active borrows; many immutable OR one mutable, never both — enforced
  live.
- **Single-threaded only.** The multithreaded analog is `Mutex<T>`.
- Trade-off: catches borrow bugs later (maybe in production) and pays a small
  runtime cost, in exchange for flexibility the compiler can't prove.

## Choosing among them (recap)

| Type        | Ownership        | Borrows allowed        | Borrow checked |
|-------------|------------------|------------------------|----------------|
| `Box<T>`    | single           | imm/mut, compile-time  | compile        |
| `Rc<T>`     | multiple         | immutable, compile-time| compile        |
| `RefCell<T>`| single           | imm/mut, runtime       | runtime        |
| `Arc<T>`    | multiple (thread)| immutable, compile-time| compile        |
| `Mutex<T>`  | shared (thread)  | imm/mut, runtime (lock)| runtime        |

- **`Rc<RefCell<T>>`** = multiple owners *and* mutability (single-threaded).
  **`Arc<Mutex<T>>`** = same, thread-safe (Ch. 16).

## Cross-links

- `Mutex`/`Arc`/`Send`/`Sync`: `references/concurrency.md`.
- Recursive types + `Box`: `references/types-coercions.md`.
- `Deref` coercion tying `&String` to `&str`: `references/ownership-borrowing.md`.
