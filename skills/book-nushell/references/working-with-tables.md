# Working with Tables (Nushell)

Source: `book/working_with_tables.html`. Tables are lists of records; commands return NEW tables (functional, no in-place edit).

## Sort / select rows

```nu
ls | sort-by size
ls | select name size          # keep named columns => new table
ls | sort-by size | first 5    # first N rows
ls | sort-by size | first 5 | skip 2
ls | sort-by name | select 5   # row by number => one-row table
```

## `get` vs `select` (again, table context)

- `ls | get name` => list of filenames.
- `ls | select name` => table with only `name` column.
- Args are cell-paths (see `navigating-data.md`).

## Changing data (all return new tables)

```nu
$first | append $second              # concat rows (++ also works)
$first | merge $second               # add columns side-by-side (align rows)
[$first $second $third] | reduce {|e,a| $a | merge $e}  # dynamic merge
open rustfmt.toml | insert next_edition 2021   # add column
open rustfmt.toml | update edition 2021        # change column
open rustfmt.toml | upsert next_edition 2021   # insert OR update
ls | move name --after size          # reorder column
ls | rename filename filetype filesize date
ls -l / | reject readonly num_links inode created accessed modified
```

- Functional: original file unchanged unless `save`. `open x | insert c v | save x2`.

## The `#` index column

Two modes:

1. **Internal `#`** (default): 0-based consecutive; matches cell-path row number (`select 0` = first). Display-only — NOT accessible by name (`get #` fails).
2. **"Index"-Renamed `#`**: once a column named `index` exists, header shows `#` but column name is `index` (accessible via `select`/`get`).
   - `ls | each { insert index { 1000 } }` makes `#` show 1000.
   - Mixed rows with/without `index` => result becomes `list<any>` (not a table).

Useful: `ls | enumerate | flatten` decouples internal `#` into a real `index` column that sorts with the row.

## The `table` command (rendering)

- Renders tables/lists/records/ranges to a **string** (e.g. `[..] | table | describe` => `string (stream)`).
- Other types pass through unchanged.
- Options: `-e` expand collapsed; `-i false` hide index; `-a 5` abbreviate to first/last 5.
- Strip color: `ls | table | ansi strip`.
