# Error Handling

Source: *The Rust Programming Language* Ch. 9 (Error Handling).

## Two categories of error

- **Unrecoverable** → `panic!`. No way to recover; process unwinds (default)
  or aborts. Use for impossible/bad-state situations.
- **Recoverable** → `Result<T, E>`. The caller decides how to handle failure.

## `panic!`

- `panic!` prints a message, unwinds the stack (cleanup), and quits.
- Switch to abort-on-panic (smaller binary) via `Cargo.toml`:

  ```toml
  [profile.release]
  panic = 'abort'
  ```

- Out-of-bounds indexing panics (vs undefined behavior in C) — protects
  against buffer overreads/security vulnerabilities.
- `RUST_BACKTRACE=1` (any value except `0`) prints a backtrace; start from
  the first frame in code you wrote. `RUST_BACKTRACE=full` for verbose.
- `main` may return `Result<(), E>`; the process exits `0` on `Ok(())` and
  nonzero on `Err`. `main` may also return any `Termination` type.

## `Result<T, E>`

```rust
enum Result<T, E> { Ok(T), Err(E) }
```

- `Ok(T)` = success value; `Err(E)` = error value. Both variants are in the
  prelude (no `Result::` prefix needed).
- `File::open` returns `Result<std::fs::File, std::io::Error>`.
- `io::Error::kind()` returns `io::ErrorKind`; match on `ErrorKind::NotFound`
  etc. for typed handling.

## Helpers on `Result`

- `unwrap()` → returns inner `Ok` or calls `panic!` on `Err`.
- `expect(msg)` → like `unwrap` but with your panic message. Production code
  prefers `expect` with context over `unwrap`.
- `unwrap_or_else(closure)` → run a fallback on `Err` (Ch. 13 closures).
- `?` operator (see below).

## The `?` operator (propagation shortcut)

- On `Result`: if `Ok`, returns the inner value and continues; if `Err`,
  returns early from the function (like `return Err(e)`).
- Error types passed through `?` are run through `From::from`, converting into
  the function's declared return error type. Define `impl From<io::Error> for
  OurError` to auto-convert.
- On `Option`: returns `Some` inner or early-returns `None`.
- **Constraint**: `?` may only be used in functions returning `Result`,
  `Option`, or another `FromResidual` type. Cannot mix — `Result` `?` won't
  auto-convert to `Option`; use `.ok()` / `.ok_or(...)` explicitly.
- `main` can return `Result<(), Box<dyn Error>>` ("any kind of error") to use
  `?` at top level.

## When to `panic!` vs return `Result` (guidelines)

- **Default to `Result`** for functions that can fail — it gives the caller
  options.
- **Panic is appropriate** when the code could enter a **bad state**: a broken
  assumption/contract/invariant (invalid, contradictory, or missing values)
  where:
  - the bad state is *unexpected* (not an occasional, anticipated failure like
    malformed user input);
  - code after the point relies on not being in that state rather than checking
    each step;
  - there's no good way to encode the constraint in the type system.
- **Return `Result`** when failure is *expected* (parser given malformed data,
  HTTP rate-limit status). That signals the caller must decide.
- Use `panic!` for safety: operating on invalid data can expose vulnerabilities
  (e.g. out-of-bounds access). Contract violations indicate caller bugs, not
  recoverable conditions.
- Examples, prototype code, and tests: `unwrap`/`expect` are fine (tests fail
  the test via `panic!`, which is the intended signal).
- **More info than the compiler**: if other logic guarantees `Ok` but the
  compiler can't see it, `expect` with a documented reason is acceptable
  (e.g. `IpAddr::parse("127.0.0.1")` — hardcoded valid, but still `Result`).

## Custom types for validation

- Encode invariants in the type system: a `Guess::new(value: i32) -> Guess`
  that `panic!`s if `value` is outside 1..=100 makes callers unable to construct
  an invalid `Guess`. The private field + public `new` constructor guarantees all
  instances are validated. Functions then take `Guess` and skip runtime checks.

## Cross-links

- `From` trait conversion: `references/traits-generics-lifetimes.md`.
- `Box<dyn Error>` / trait objects: `references/concurrency.md` and Ch. 18.
- `unwrap_or_else` closures: `references/patterns-matching.md` (Ch. 13).
