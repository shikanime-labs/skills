# Appendices: Keywords, Operators, Derivable Traits, Editions

Source: *The Rust Programming Language* Appendix A (Keywords), B (Operators
and Symbols), C (Derivable Traits), E (Editions).

## Keywords currently in use (with meaning)

- `as` — primitive cast, trait disambiguation, rename in `use`.
- `async` / `await` — return a `Future` / suspend until ready.
- `break` / `continue` / `loop` — loop control.
- `const` — constant items / constant raw pointers.
- `crate` — refers to the crate root in paths.
- `dyn` — dynamic dispatch to a trait object.
- `else` — fallback for `if`/`if let`.
- `enum` / `struct` / `union` / `trait` — type definitions.
- `extern` — link external fn/var (and, since Edition 2024, `extern` blocks
  require `unsafe`).
- `false` / `true` — boolean literals.
- `fn` — define a function or the fn-pointer type.
- `for` — iterate, implement a trait, or higher-ranked lifetime.
- `if` / `while` / `match` — control flow / pattern matching.
- `impl` — inherent or trait impl.
- `in` — part of `for` loop syntax.
- `let` — bind a variable.
- `mod` — define a module.
- `move` — force a closure to take ownership of all captures.
- `mut` — mutability marker.
- `pub` — public visibility.
- `ref` — bind by reference in patterns.
- `return` — return from function.
- `Self` — type alias for the type being defined/impl'd; `self` — method
  subject or current module.
- `static` — global variable or program-lifetime.
- `type` — type alias / associated type.
- `unsafe` — unsafe code/fn/trait/impl.
- `use` — bring symbols into scope.
- `where` — type constraint clauses.

**Reserved (future use)**: `abstract`, `become`, `box`, `do`, `final`, `gen`,
`macro`, `override`, `priv`, `try`, `typeof`, `unsized`, `virtual`, `yield`.

**Raw identifiers**: prefix a keyword with `r#` to use it as an identifier,
e.g. `r#match`. Also lets a newer-edition crate call a dependency's item that
is a keyword in the newer edition (e.g. `r#try` for a 2015-edition dep).

## Operators and symbols (quick reference)

- `!` — macro invocation (`mac!()`) or bitwise/logical NOT (`!expr`, trait `Not`).
- `!=` equality (trait `PartialEq`); `==` equality.
- `%`/`%`= rem (trait `Rem`/`RemAssign`); `&`/`&=` AND (`BitAnd`); `|`/`|=` OR
  (`BitOr`); `^`/`^=` XOR (`BitXor`); `<<`/`>>` shifts (`Shl`/`Shr`).
- `&` — borrow (`&x`, `&mut x`) or borrowed-pointer type (`&T`, `&mut T`,
  `&'a T`). `&&` short-circuit logical AND.
- `*` — multiplication (`Mul`), dereference (`*expr`, trait `Deref`), or raw
  pointer (`*const T`, `*mut T`).
- `+` — addition (`Add`) or trait/type constraint (`T: A + B`).
- `-` — negation (`Neg`) or subtraction (`Sub`). `/` division (`Div`).
- `->` — function/closure return type. `.` — field/method access, tuple index.
- `..` — range (`a..b` exclusive), rest pattern (`..`, `x, ..`), or struct
  update (`..Default::default()`). `..=` — inclusive range (`a..=b`).
- `=` assignment; `+= -= *=` etc. assignment-ops.
- `<` `>` `<=` `>=` ordering (trait `PartialOrd`).
- `=>` match-arm separator; `@` pattern binding (`x @ 1..=5`).
- `|` — pattern alternatives (`A | B`) or bitwise OR.
- `:` — type/constraint (`pat: type`), field init (`x: expr`), loop label
  (`'a: loop`).
- `;` — statement/item terminator; `[T; N]` array syntax.
- `::` — path separator. `?` — `?Sized` / `Result` propagation operator.
- `()` — unit (empty tuple), both literal and type. `[]` arrays/indexing
  (`Index`/`IndexMut`). `{}` blocks / struct literals.
- Doc comments: `///` outer line, `//!` inner line, `/** */` block, `/*! */`
  inner block.

## Derivable traits (std, via `#[derive(...)]`)

- `Debug` — `{:?}` debug formatting; required by `assert_eq!`.
- `PartialEq` / `Eq` — `==`/`!=`. Derived `PartialEq`: all fields equal (or
  enum variant equals only itself). `Eq` (no methods) marks a type equal to
  itself; needed for `HashMap` keys. Floats implement `PartialEq` but not `Eq`
  (NaN ≠ NaN).
- `PartialOrd` / `Ord` — `< > <= >=` and sorting. `PartialOrd` needs
  `PartialEq`; returns `Option<Ordering>` (None for incomparable, e.g. NaN).
  `Ord` needs `PartialOrd + Eq`, always returns `Ordering`; needed for
  `BTreeSet`.
- `Clone` / `Copy` — `Clone` = explicit deep copy (`clone()`, may run code /
  copy heap). `Copy` = stack-only bit copy, no code, very fast; implies
  `Clone`. A type can't be `Copy` if any part implements `Drop`.
- `Hash` — map to fixed size for `HashMap` keys; derived by hashing each field.
- `Default` — `Default::default()`; pairs with `..Default::default()` struct
  update; required by `Option::unwrap_or_default`.
- Note: `Display` is NOT derivable (no sensible default for end-user
  formatting) — implement manually. Libraries may provide `derive` for their
  own traits (procedural macros).

## Editions

- Rust has a 6-week release cycle; every ~3 years a new **edition** bundles
  accumulated features with updated docs/tooling. Available: 2015, 2018, 2021,
  2024. This book uses **2024** idioms.
- The `edition` key in `Cargo.toml` selects the edition; absent → `2015` for
  backward compatibility.
- Editions may carry incompatible changes (e.g. new keywords). You must **opt
  in**; otherwise code keeps compiling across compiler upgrades. Crates of
  different editions link together fine — edition only affects initial parsing.
- Most features work on all editions; some (mainly new keywords) are later-
  edition only. Upgrade via `cargo fix` / the Edition Guide.

## Cross-links

- `Copy` vs `Drop` exclusion, move semantics: `references/ownership-borrowing.md`.
- `?Sized` in trait/generic params: `references/types-coercions.md` and
  `references/traits-generics-lifetimes.md`.
- `derive` procedural macros: `references/unsafe-macros-advanced.md`.
- `dyn` trait objects: Ch. 18 (out of core scope; see Book).
