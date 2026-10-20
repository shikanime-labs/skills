# Shikanime org identities

- Operator identity and default active account: `shikanime`.
- Agent identity for automation, pushes, and PR posts: `yorha-automata`.
- `sks-land` Gate 2 posts the approval as `yorha-operator`; locally that is
  the `yorha-automata` account — switch to it, confirm, post, restore
  `shikanime` immediately after.
- Both accounts authenticate on `github.com` on the workstations running the
  dev loop; `gh auth status --hostname github.com` lists them.
