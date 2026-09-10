# Patterns and Matching

Source: *The Rust Programming Language* Ch. 6 (match, if let, let...else),
Ch. 19 (Patterns); *The Rust Reference* `patterns.md`.

## `match`

- Compares a value against a series of **patterns**, runs the first arm whose
  pattern fits. Each arm: `pattern => expression`, arms separated by commas.
- The matched expression can be **any type** (unlike `if`, which needs `bool`).
- Arm bodies are expressions; the matching arm's value is the whole `match`'s
  value. Use `{ ... }` for multi-line arms (trailing comma then optional).
- **Patterns bind values**: `Coin::Quarter(state)` extracts the inner value
  into `state` for use in the arm.
- **Exhaustiveness**: arms must cover *all* possibilities or it won't compile.
  For `Option<T>` you cannot skip the `None` case — this is what makes the
  "billion-dollar null mistake" impossible.
- **Catch-alls**: a variable (`other`) or `_` (matches anything, no binding,
  no unused-variable warning). Catch-all **must be last** (patterns tried in
  order); arms after it trigger a warning. `_ => ()` ignores everything.
- Use `match` when you need exhaustiveness guarantees; that's its main
  advantage over `if let`.

## `if let` and `let...else`

- `if let Some(x) = opt { ... }` — sugar for a `match` that runs code on one
  pattern and ignores the rest. Less typing/indentation, but **loses
  exhaustive checking**.
- Can add `else { ... }` (equivalent to the `_` arm of the same `match`).
- **`let...else`** (Edition 2021+): `let pattern = expr else { return ...; };`
  binds on match and **requires the `else` arm to diverge** (return/break/
  panic) on mismatch. Keeps the "happy path" in the function body instead of
  nesting. The `else` block MUST return from the enclosing function.

## Pattern kinds (Reference)

- **Literal**: `1`, `"hi"`, `-1` (optional minus). Always refutable.
- **Identifier**: `x` binds the value (copy or move depending on `Copy`).
  `mut x` binds mutably. `x @ subpat` binds to `x` while also matching a
  subpattern (e.g. `e @ 1..=5`). `ref x` / `ref mut x` bind by reference
  (needed inside destructuring where `&` can't apply).
- **Wildcard** `_`: matches one field/value, no binding.
- **Rest** `..`: matches *all remaining* fields/variants (struct/enum/tuple).
- **Reference** `&pat`: matches a reference and dereferences.
- **Struct / TupleStruct / Tuple**: destructure by name or position; `..`
  ignores the rest. Named-field shorthand: `fieldname` = `fieldname: fieldname`.
- **Slice** `[a, b, rest @ ..]`: destructures slices.
- **Path**: constants/enums (e.g. `Coin::Penny`, `None`). Single-segment
  identifiers are ambiguous between identifier and path until name resolution.
- **Or-patterns** `A | B`: matches either; both sides must bind the same names
  with unifiable types. Lowest precedence.

## Refutability

- **Irrefutable** patterns always match: `let (x, y) = ...`, bare identifier,
  `&T` refs in bindings. Allowed in `let`, function params, `for`.
- **Refutable** patterns might not match: literal, `Some(x)`, `(a, 3)`. Only
  allowed in `match`, `if let`, `while let` — not in plain `let`.
- Binding modes: matching a non-reference pattern against a reference value
  auto-applies `ref`/`ref mut` (e.g. `if let Some(y) = &opt` binds `y: &i32`).

## Places patterns are used

- `let` declarations, function/closure params, `match`, `if let`, `while let`,
  `for`, and argument destructuring.

## Cross-links

- `Option<T>`/`Result<T,E>` enums: `references/error-handling.md`.
- Destructuring with `ref`/`Copy`: `references/ownership-borrowing.md`.
- `let...else` edition requirement: `references/appendices-glossary.md`.
