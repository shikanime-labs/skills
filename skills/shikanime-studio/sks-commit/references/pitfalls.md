# sks-commit — Pitfalls

- Assuming cpn conventional style — shikanime code repos use plain English.
- Ignoring a repo hook → local commit rejected; detect first.
- Pushing a branch to the wrong remote — `origin` is the single push target.
- Forgetting `jj bookmark track <branch> --remote=origin` → push fails.
- Trailing period / lowercase start in subject — imperative, capitalized.
- Leaving jj `*` / `---------` artifacts or a self `Co-authored-by:` in a
  squashed message.
