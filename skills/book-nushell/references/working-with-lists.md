# Working with Lists (Nushell)

Source: `book/working_with_lists.html`. Lists == single (unnamed) table column; commands on columns also work on lists.

## Create

`[foo bar baz]` or `[foo, bar, baz]` (JSON-array compatible). Items split by spaces/commas/linebreaks.

## Update / insert

```nu
[1,2,3,4] | insert 2 10     # [1,2,10,3,4]
[1,2,3,4] | update 1 10     # [1,10,3,4]
```

## Add / remove

```nu
[$colors | prepend red]    # front
[$colors | append purple]  # end
[$colors ++ ["blue"]]      # ++ operator
[["black"] ++ $colors]
$colors | skip 1           # drop first N
$colors | drop 2           # drop last N
$colors | first 2          # take from front
$colors | last 3           # take from end
```

Spread operator `...`: `[...$x 3 ...(4..7 | take 2)]`.

## Iterate

```nu
$names | each { |elt| $"Hello, ($elt)!" }
$names | enumerate | each { |elt| $"($elt.index + 1) - ($elt.item)" }
$scores | where $it > 7                 # [10 8]
$scores | reduce { |elt, acc| $acc + $elt }   # sum; -f for fold init
$scores | math sum                      # easier sum
```

## Access / query

```nu
$names.1                    # index access
$names | get $index         # var index
[red green blue] | length   # count
[] | is-empty               # true
'blue' in $colors           # membership
'gold' not-in $colors
$colors | any {|e| $e | str ends-with "e"}   # true if any
$colors | all {|e| ($e|str length) >= 3}    # true if all
```

## Convert

```nu
[1 [2 3] 4 [5 6]] | flatten          # one level; chain for depth
$zones | wrap 'Zone'                  # list -> table (single column)
```
