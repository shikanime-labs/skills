# Types of Data (Nushell)

Source: `book/types_of_data.html`. Nushell commands pass typed values (not just text) through pipelines.

## Type table (verbatim-ish annotations)

| Type | Annotation | Literal example |
| --- | --- | --- |
| Integer | `int` | `-100`, `0xff`, `0o234`, `0b10101` |
| Float | `float` | `1.5`, `2.0` (approximate; `10.2 * 5.1` => `52.0199...`) |
| String | `string` | `"a"`, `'a'`, `` `a` ``, `r#'a'#` |
| Boolean | `bool` | `true` / `false` |
| Date | `datetime` | `2000-01-01` |
| Duration | `duration` | `2min + 12sec`, `3.14day`, `30day / 1sec` => `2592000` |
| Filesize | `filesize` | `64mb`, `0.5kB` => `500 B`, `1GiB / 1B` => `1073741824` |
| Range | `range` | `0..4`, `0..<5`, `0..`, `..4`, `2..4..20` (stride) |
| Binary | `binary` | `0x[FE FF]`, `0o[1234567]`, `0b[101010]` |
| List | `list` | `[0 1 'two' 3]` |
| Record | `record` | `{name:"Nushell", lang:"Rust"}` |
| Table | `table` | `[{x:12,y:15},{x:8,y:9}]` or `[[x,y];[12,15],[8,9]]` |
| Closure | `closure` | `{|e| $e + 1}` |
| Cell-path | `cell-path` | `$.name.0` |
| Block | — | `if true { print "hi" }` |
| Nothing | `nothing` | `null` |
| Any | `any` | `let p: any = 5` |

## Key facts

- `describe` returns a value's type: `42 | describe` => `int`.
- Floats are approximate (IEEE-754); expect trailing precision errors.
- **Tables are internally lists of records.** `get 0` on a table yields a `record`; on a list yields the first element.
- Dates/durations/filesizes compute: `30day / 1sec`, `1GiB / 1B == 2 ** 30`.
- Ranges render as tables; `seq char` / `seq date` build char/date sequences.
- Cell-path: dot-separated row(int)/col(string) ids; leading `$.` disambiguates assignment to a var. `let cp = $.2` then `[foo bar goo] | get $cp`.
- Closure literal `{|args| expr}`; used by filters (`where`, `each`) and closes over outer scope.
- **Optional `?`** on a cell-path returns `null` if missing: `{a:5} | get a?` => `5`; `get c?` => `nothing`. `== null` true.

## Type mismatch behavior

Operators are not universal; Nu errors on type mismatch (`can't convert list<string> to string`). Check a command's accepted types with `help <cmd>` -> Input/output types.
