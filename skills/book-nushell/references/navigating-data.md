# Navigating & Accessing Structured Data (Nushell)

Source: `book/navigating_structured_data.html`. Cell-paths are Nu's query language.

## Definitions

- List: ordered values, any type (0 = empty list).
- Record: key(string)->value pairs (0 = empty record).
- Table: **a list of records**. So anything valid on a list is valid on a table; not vice-versa.
- Nested: list/record/table values can themselves be structured.

## Cell-path syntax

Dot-separated row(int)/col(string) ids. 0-based.

```nu
$my_record.b + 5                       # record key
$scoobies_list.2                       # list index => Daphne
$data.1                               # table row => record
$data.condition                       # table column => list
$data.condition.3                     # single cell => value
$data.temps.2.1                       # nested: day 3, station 2
```

## `get` vs `select` (critical distinction)

- `get <cell-path>`: returns the **value** at the path. `get 1` on a table => record (same as `$data.1`).
- `select <cell-paths>`: returns the **same structure** (table/list/record) possibly smaller. `select 1` on a table => a new one-row table with fresh 0-based indices.
- `select` accepts multiple cols/rows: `$data | select date condition 0 1`.
- `select` result indices are NOT original; use `enumerate` then `select` to preserve original index.

## Missing data

- `?` optional operator: `$data | get a?` => `null` if missing instead of error. Also in cell-path literals: `$.temps?.1`.
- `default <val> <col>`: fills missing/null in a column:
  `[{a:1,b:2},{b:1}] | default 'n/a' a` => second row `a` becomes `n/a`.

## Quoted keys / spaces

```nu
$record_example."key x"      # key with spaces
$record_example | get "key x"
$record_example."1"          # key named "1" (string) vs row index 0
```

## Other navigation commands

- `reject` — opposite of `select` (drop rows/cols).
- `slice <range>` — select rows by range type.
- `enumerate` — add `index`+`item` to each element (used with `reduce`/`each`).
