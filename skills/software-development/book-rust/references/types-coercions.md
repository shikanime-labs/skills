# Types, Coercions, and Dynamically Sized Types

Source: *The Rust Reference* — `types.md`, `type-coercions.md`,
`dynamically-sized-types.md`, `subtyping.md`, plus Book Ch. 3 (Data Types).

## Type taxonomy (Reference)

- **Primitive**: `bool`; numeric (integer + float); `char`; `str`; never `!`.
- **Sequence**: tuple; array `[T; n]`; slice `[T]`.
- **User-defined**: struct; enum; union.
- **Function**: function item; closure.
- **Pointer**: reference `&T`/`&mut T`; raw pointer `*const T`/`*mut T`;
  function pointer `fn(...) -> ...`.
- **Trait**: trait object `dyn Trait`; `impl Trait`.

## Key primitive facts

- **`str`**: a string slice — an unsized sequence of UTF-8 bytes. Always used
  behind a reference: `&str`. String literals are `&'static str`.
- **`char`**: a Unicode scalar value, 4 bytes, written in single quotes
  (`'a'`, `'🚀'`). Distinct from a single-byte `u8`.
- **Numeric**: signed/unsigned integers `i8..i128`, `u8..u128`, `isize`/
  `usize`; floats `f32`/`f64`. Integer literals can have type suffixes
  (`42u8`). `usize` for indices/sizes.
- **Never `!`**: a type with no values; the type of `panic!`, `loop`, diverging
  expressions. Coerces to any `T`.
- **`bool`**: `true`/`false`.

## `Sized` / Dynamically Sized Types (DSTs)

- Most types have a compile-time-known size and implement `Sized`. A type whose
  size is known only at runtime is a **DST (unsized type)**: `str`, slices
  `[T]`, and trait objects `dyn Trait`.
- Constraints:
  - **Variables, function parameters, `const`, and `static` items must be
    `Sized`.** You cannot have a bare `str` or `[i32]` as a local/param.
  - **Pointers to DSTs are sized** but store *metadata* (twice a normal
    pointer): slice/str pointers store length; trait-object pointers store a
    vtable pointer; structs/tuples with an unsized tail store that tail's
    metadata.
  - DSTs are allowed as the **last field** of a struct (making the struct
    itself a DST), and as generic args/associated types when the param has the
    **`?Sized`** bound. By default every type param is `Sized`; relax with
    `T: ?Sized` (e.g. `fn foo<T: ?Sized>(x: &T)`).
  - Traits default to `Self: ?Sized` (can be implemented for DSTs).

## Type coercions (implicit, restricted)

- Coercions change a value's type automatically only at specific **coercion
  sites**; anything allowed by coercion can also be done explicitly with `as`.
- **Coercion sites**: `let`/`static`/`const` with explicit type; function-call
  arguments (to the param type); struct/enum/union field initializers; function
  results (final block expr / `return`); assignment RHS. Propagating
  expressions (array literals, tuples, parenthesized, blocks) make their
  sub-expressions sites too.
- **Allowed coercion kinds**:
  - Subtype (reflexive) / transitive.
  - `&mut T` → `&T`; `*mut T` → `*const T`.
  - `&T` → `*const T`; `&mut T` → `*mut T`.
  - `&T` → `&U` / `&mut T` → `&mut U` when `T: Deref<Target=U>` (deref
    coercion).
  - **Unsized coercions** (built-in, via `Unsize`/`CoerceUnsized`):
    - `[T; n]` → `[T]`
    - `T` → `dyn U` when `T: U + Sized` and `U` is dyn-compatible
    - `dyn T` → `dyn U` for supertraits (incl. dropping/adding auto traits)
    - `&T`, `&mut T`, `*const T`, `*mut T`, `Box<T>` → the `U` tail via
      unsizing (e.g. `Box<[T; n]>` → `Box<[T]>`)
  - Function item types → `fn` pointers; **non-capturing** closures → `fn`
    pointers.
  - `!` → any `T`.
- **Least Upper Bound (LUB) coercion**: when multiple branches/arms/elements
  must unify to one type (if/else, match arms, array elements, labeled-block
  `break` values, loop `break` values, multi-return closures/functions), the
  compiler coerces to the most general common type iteratively (`T0` then
  extend/ unify with each `Ti`).

## Subtyping & variance (see also `traits-generics-lifetimes.md`)

- Subtyping is mostly limited to lifetimes: `'static` outlives `'a`, so
  `&'static str <: &'a str` (subtype), which is why `'static` values can be
  used where a shorter lifetime is expected.
- Variance of built-in types (in `'a` / in `T`):
  - `&'a T`: covariant / covariant
  - `&'a mut T`: covariant / **invariant**
  - `*const T`: covariant; `*mut T`: **invariant**
  - `[T]`, `[T; n]`: covariant; `fn() -> T`: covariant; `fn(T) -> ()`:
    **contravariant**
  - `UnsafeCell<T>`: **invariant**; `dyn Trait<T> + 'a`: covariant in `'a`,
    **invariant** in `T`
- Composite types: variance is the join over their fields; a param used in
  both covariant and invariant (or contra-) positions becomes **invariant**.

## Cross-links

- `Box`, `Rc`, `RefCell` for recursive/unsized-backed data:
  `references/smart-pointers.md`.
- `&str`/`&[T]` slices and borrowing: `references/ownership-borrowing.md`.
- Lifetimes/variance in function signatures: `references/traits-generics-lifetimes.md`.
