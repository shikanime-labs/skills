# Generics, Traits, and Lifetimes

Source: *The Rust Programming Language* Ch. 10; Reference: `trait-bounds.md`,
`lifetime-elision.md`, `subtyping.md`.

## Generics

- Parameterize functions, structs, enums, and methods with `<T, U, ...>`.
  Convention: one-letter `UpperCamelCase` names (`T` default).
- Type parameters go in `<>` after the item name. For methods, declare `T`
  after `impl` so the compiler knows it's generic:
  `impl<T> Point<T> { fn x(&self) -> &T { &self.x } }`.
- A `Point<T>` with one `T` forces `x` and `y` same type; use `Point<T, U>` for
  different types. Methods may add their own generic params independent of the
  struct's.
- Constrain methods to specific concrete types: `impl Point<f32> { ... }`.
- **No runtime cost**: Rust performs *monomorphization* — generic code is
  expanded into concrete types at compile time. `Option<i32>` and `Option<f64>`
  become distinct definitions. Performance identical to hand-written duplicates.

## Traits

- A **trait** defines shared behavior via a set of method signatures. "Like
  interfaces in other languages, with differences." Types implement the trait
  with `impl Trait for Type { ... }`.
- **Orphan rule (coherence)**: you may implement a trait for a type only if
  *either* the trait *or* the type is local to your crate. Cannot implement an
  external trait (e.g. `Display`) on an external type (e.g. `Vec<T>`).
- `pub trait Summary { fn summarize(&self) -> String; }`. Default
  implementations allowed: `fn summarize(&self) -> String { "...".into() }`
  — implementors can keep or override. Default methods may call other trait
  methods (required ones). You cannot call a default from an overriding method.
- **Traits as parameters** (`impl Trait` sugar):
  - `fn notify(item: &impl Summary)` = `fn notify<T: Summary>(item: &T)`.
  - To force both params to share the same type, use a single `<T: Summary>`.
  - Multiple bounds: `impl Summary + Display` or `<T: Summary + Display>`.
  - `where` clauses for readability: `fn f<T, U>(t: &T, u: &U) where T:
    Display + Clone, U: Clone + Debug`.
- **Returning `impl Trait`**: `fn returns_summarizable() -> impl Summary` —
  returns *one* concrete type that implements the trait (useful for closures,
  iterators, trait objects avoided). Cannot return different types branching
  (e.g. `NewsArticle` or `SocialPost`) — use trait objects (`dyn`) for that.
- **Conditional impls**: `impl<T: Display + PartialOrd> Pair<T> { ... }`
  adds methods only when bounds hold. *Blanket impls*: `impl<T: Display>
  ToString for T` implement a trait for all types meeting a bound (used heavily
  in std; see a trait's "Implementors" docs).

## Lifetimes

- Every reference has a lifetime (scope of validity). Usually inferred, like
  types. Annotate only when relationships are ambiguous and the borrow checker
  can't prove validity.
- **Purpose**: prevent dangling references. The *borrow checker* compares
  scopes; if a reference outlives its referent, it's rejected.
- **Syntax**: parameters start with `'` and are usually lowercase (`'a`).
  Placed after `&`: `&'a i32`, `&'a mut i32`. Annotations describe
  relationships; they don't change how long anything lives.
- In function signatures: `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str`.
  The returned reference is valid for the *smaller* of `x` and `y`'s
  lifetimes. Annotations go in the signature, not the body (part of the
  contract).
- Rule of thumb: a returned reference's lifetime must match one of the
  parameters' lifetimes.
- **`'static`**: the reference lives for the whole program (string literals
  are `'static`). Error messages suggesting `'static` usually indicate a
  dangling reference or lifetime mismatch — fix the root cause, don't slap
  `'static` on.

## Lifetime elision rules (functions, fn pointers, closures)

1. Each elided lifetime in parameters becomes a distinct lifetime parameter.
2. If exactly one lifetime appears in parameters, it's assigned to all elided
   output lifetimes.
3. (Methods) if the receiver is `&Self` / `&mut Self`, its lifetime is assigned
   to all elided output lifetimes.

- `'_` is the placeholder that triggers inference (preferred in paths).
- Illegal to elide when uninferable: `fn get_str() -> &str` (no params) or
  `fn frob(s: &str, t: &str) -> &str` (ambiguous which param the output borrows).

## Variance & subtyping (Reference)

- Subtyping exists mainly for lifetimes: `'static` outlives `'a`, so
  `&'static str` is a subtype of `&'a str`.
- **Covariant**: `F<T>` subtype of `F<U>` when `T` subtype of `U`.
  **Contravariant**: reverses. **Invariant**: no subtyping derived.
- Built-in variance table (key rows):
  - `&'a T`: covariant in `'a` and `T`.
  - `&'a mut T`: covariant in `'a`, **invariant** in `T`.
  - `*const T`: covariant in `T`; `*mut T`: **invariant** in `T`.
  - `[T]`, `[T; n]`: covariant in `T`. `fn() -> T`: covariant in `T`;
    `fn(T) -> ()`: **contravariant** in `T`.
  - `UnsafeCell<T>`: **invariant** in `T`. `dyn Trait<T> + 'a`: covariant in
    `'a`, **invariant** in `T`.
- A composite `struct`/`enum`/`union` is invariant in a param if that param
  appears in positions with differing variance.

## Cross-links

- `Send`/`Sync` + lifetimes in concurrency: `references/concurrency.md`.
- `Deref`, `Drop`, `Rc`, `RefCell`: `references/smart-pointers.md`.
- `&str`/`&[T]` slices: `references/ownership-borrowing.md`.
- Trait objects (`dyn`): Ch. 18 (out of this skill's core scope; see Book).
