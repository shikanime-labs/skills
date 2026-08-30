# Cross-Language Maps & Thinking in Nu (Nushell)

Source: `book/nushell_map.html`, `book/nushell_operator_map.html`, `book/thinking_in_nu.html`.

## Command map (Nu -> SQL / Python / C# LINQ / PowerShell / Bash)

Key equivalents: `each`~ForEach-Object/`for`; `where`~Where-Object/`where`; `select`~Select-Object; `get`~ForEach-Object <name>; `reduce`~Aggregate; `first`/`last`~head/tail; `str join`~join; `from`/`to`~Import/Convert*; `transpose`~pivot; `group-by`~group by; `math sum/avg`~sum/avg; `uniq`~distinct; `sort-by`~order by; `skip`~Select-Object -Skip; `slice`~limit offset; `take`~top/limit; `http`~Invoke-WebRequest/curl; `sys *`~uname/lsblk/free; `help`~Get-Help/man. (Full table in source `nushell_map.html`.)

## Operator map (Nu -> other langs)

`==`=`, `!=`=`<>`/`!=`, `< <= > >=` standard, `=~`~like/re/contains, `!~`~not like, `+ - * /` standard, `**`~pow/`**`, `in`/`not-in`~in/contains, `and`/`or`~&&/`||` (also `-And`/`-Or` in PS, `-a`/`-o` in Bash).

## Thinking in Nu (mental models)

- **Not Bash**: `>` is the greater-than OPERATOR (like C/Python), not redirection. Redirect via `| save` / `out>`. `4 > 10` => false.
- **Implicit return**: the value of the last subexpression is the return value. `echo` RETURNS a value (not prints); `"Hello" == (echo "Hello")` => true. Just write `<value>` instead of `echo <value>`. `def f [] { ls | sort-by modified | last }` returns the file.
- **Single return value per expression**: only the LAST value is returned; earlier ones are discarded (use `print` to display side-output). Semicolon == newline.
- **Every command returns a value** (even `null`). `let`/`print` return `null`; know command output types via `help <cmd>`.
- **Static parsing (think compiled)**: Parse entire source, THEN evaluate. No `eval`. `source`/`use`/`overlay use`/`hide`/`plugin use` are PARSER keywords — their targets must exist at parse time. So:
  - Can't `save` then `source` in one expression (file absent during parse) — works only as separate REPL lines.
  - `source $"($my_path)/x.nu"` fails (var not constant). Use `const my_path = ...` or literal. `const` is parse-time resolved.
  - `cd spam; source-env foo.nu` fails (cd is eval-time; source resolves at parse). Use the full path `source-env spam/foo.nu`.
- **Immutable by default**: prefer functional style + `par-each` for parallelism; mutable vars (`mut`) can't be captured by closures.
- **Scoped environment**: env/cd changes die at block end. `ls | each { cd $row.name; make }` starts each iter from cwd. `def --env` is the exception (persists to caller).
