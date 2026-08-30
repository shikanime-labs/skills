# Aliases, Operators, Variables (Nushell)

Source: `book/aliases.html`, `book/operators.html`, `book/variables.html`.

## Aliases (`book/aliases.html`)

```nu
alias ll = ls -l
ll -a                       # flags/args append after expansion
scope aliases / help aliases
```

- Persist by adding to `config.nu` (then restart).
- **No pipelines in aliases**: `alias uuidgen = uuidgen | tr A-F a-f` fails. Use `def` instead.
- Replacing a builtin: alias the original FIRST (`alias ls-builtin = ls`), then `def ls [...] {...}`; else recursion error. Call original via `%ls`.

## Operators (`book/operators.html`)

| Op | Meaning |
| --- | --- |
| `+ - * / // mod **` | add sub mul div floor-div modulo power |
| `== != < <= > >=` | comparison |
| `=~` / `like` | regex match / contains |
| `!~` / `not-like` | inverse |
| `in` / `not-in` | value in list |
| `has` / `not-has` | list has value |
| `not and or xor` | logic (and/or short-circuit) |
| `bit-or xor and shl shr` | bitwise |
| `starts-with` / `ends-with` | string |
| `++` | append lists |

Precedence (high→low): `()` > `**` > `* / // mod` > `+ -` > `bit-shl/shr` > comparisons/`in`/`starts-with`/`=~`/`++` > `bit-and` > `bit-xor` > `bit-or` > `and` > `xor` > `or` > assignment > `not`. Check live: `help operators | sort-by precedence -r`.

- Type mismatch => parser error (`"spam" - 1`).
- `=~` uses Rust `regex::is_match`. Case-sensitive; case-insensitive via `(?i)` flag, `str contains --ignore-case`, or `str downcase`.
- **Spread `...`**: unpack lists/records where multiple values expected. In list/record literals before `$var`/`(subexpr)`/`[lit]`/`{lit}`, NO whitespace. In command calls only if command has rest param or is external. Minor perf win over chained `append`.

## Variables (`book/variables.html`)

- `let` immutable (reassign => error). `const` parse-time constant (for `source`/`use`/`plugin use`). `mut` mutable.
- Shadowing allowed: `let val = 42; let val = $val + 1`.
- Mutable ops: `= += -= *= /= ++=` (`++=` needs var OR arg a list).
- Closures/nested `def` cannot capture `mut` from outer scope; use loops or functional style.
- Prefer immutable + filters (`each`, `reduce`, `par-each`) — far faster (50k randoms: `for`=64s vs `each`=19ms) and stream/parallelize.
- Var names exclude `. [ ( { + - * ^ / = ! < > & |`. Leading `$` optional/ignored: `let $var = 42` == `let var = 42`.
