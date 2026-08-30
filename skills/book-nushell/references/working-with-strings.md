# Working with Strings (Nushell)

Source: `book/working_with_strings.html`.

## String formats

| Format | Example | Escapes | Notes |
| --- | --- | --- | --- |
| Single-quoted | `'[^\\n]+'` | None | no embedded `'` |
| Double-quoted | `"The\nEnd"` | C-style `\` | backslash must be escaped |
| Raw | `r#'Raw'#` | None | may contain `'`; extra `#` to nest `r###'...'###` |
| Bare word | `ozymandias` | None | word chars only; in command position => external cmd |
| Backtick | `` `ls` `` | None | bare w/ whitespace; in command position => command/path |
| Single interp | `$'Cap ($n)'` | None | no `'` or unmatched `()` |
| Double interp | `$"Cap ($n)"` | C-style | backslash + `()` must be escaped |

- Double-quote escapes: `\" \' \\ \/ \b \f \r \n \t \u{X...}` (1-6 hex). `\0` via `\u{0}` or `(char nul)`.
- Bare/backtick words in command position run as external (or path). `true`/`trueX` are special tokens, not strings. Prefer quotes when programming.
- `^` sigil forces external: `^'C:\Program Files\exiftool.exe'` or `^$foo`. Also `run-external`.

## Concatenation / joining

```nu
['foo','bar'] | each {|s| '~/' ++ $s}     # ~/foo, ~/bar  (++ concat)
['foo','bar'] | str replace -r '^' '~/'   # prepend via regex
"hello" | append "world!" | str join " "  # str join => hello world!
1..10 | reduce -f "" {|e,a| $a + ($e|into string) + " + "}  # prefer str join
```

## Interpolation

- `$\" \"` / `$' '`; wrap expressions in `()`. `$\"greetings, ($name)\"`.
- v0.61+: escape parens `\(` `\)` to print literal `()`: `$\"2+2 is (2+2) \(guessed!)\"`.
- `const x = $"(2kb)"` evaluates at parse time with default config (file sizes/datetimes use default units).

## Splitting

```nu
"red,green,blue" | split row ","      # list
"red,green,blue" | split column ","   # table w/ column1..
'aeiou' | split chars                 # list of chars
```

## `str` subcommands (full list: `help str`)

- `str contains "o wo"` (or `=~` operator, see below)
- `str trim` (flags `-r`/`-l`, `-c <char>`)
- `str index-of 'o'` => 4; `str substring 4..8` => `o Wor`
- `fill -a right -c '0' -w 10` (pad); `str reverse`
- `parse '{shell} {version}'` and `parse --regex '(?P<subject>\w+...) is (?P<adj>\w+)'`

## Comparison operators

```nu
'APL' =~ '^\w{0,3}$'      # regex match => true
'FORTRAN' !~ '^\w{0,3}$'  # regex no-match => true
'JavaScript' starts-with 'Java'   # => true
'OCaml' ends-with 'Caml'          # => true
# plus == and !=
```

## Convert

- To string: `123 | into string` or `$'(123)'`.
- From string: `'123' | into int` (family `into <type>`).
- Color: `$'(ansi purple_bold)text(ansi reset)'` (always end with `ansi reset`).
