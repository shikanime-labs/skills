# Loading Data (Nushell)

Source: `book/loading_data.html`. `open` auto-detects format by extension and parses to structured data.

## `open` supported formats

csv, eml, ics, ini, json, nuon, ods, sqlite, ssv, toml, tsv, url, vcf, xlsx/xls, xml, yaml/yml.

```nu
open editors/vscode/package.json | get version      # => 1.0.0
open Cargo.toml --raw                             # raw text, no parse
```

- `open` resolves a `from <ext>` subcommand in scope; define your own `from ...` to extend supported types.
- Unknown extension => one big string.
- `--raw` returns underlying text.

## NUON (Nushell Object Notation)

- Valid Nushell code describing data; **superset of JSON** (any JSON is valid NUON).
- Comments allowed; commas not required.
- Limitation: cannot serialize blocks.

## `from` for explicit parsing

```nu
open Cargo.lock | from toml        # parse non-.toml by format
open foo.db                        # SQLite auto-detected
open foo.db | get some_table
open foo.db | query db "select * from some_table"
```

(Old Nu: `into db | query`.)

## Parsing ad-hoc text (pipe-delimited example)

```nu
open people.txt
| lines                              # split into list of lines
| split column "|" first_name last_name job   # name columns
| str trim                           # trim whitespace
| sort-by first_name
| get first_name
```

- `split column <delim> [colnames...]` assigns default `column1..` if names omitted.
- `lines`, `str` families for string work.

## Fetching URLs

```nu
http get https://blog.rust-lang.org/feed.xml     # returns parsed record/table
```

## Gotcha: feeding external commands

Raw text only. Nushell renders tables with border glyphs before piping to an external, which breaks tools like `^grep`. Convert explicitly:

```nu
ls /share | get name | to text | ^grep tutor
# or
ls /share | get name | find tutor | ansi strip | ^ls -al ...$in
```
