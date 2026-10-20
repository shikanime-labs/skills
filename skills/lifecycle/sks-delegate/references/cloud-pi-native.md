# cloud-pi-native isolation specifics

Load when working in the cloud-pi-native/console repository.

## Org identity

- Default checkout: `~/Source/Repos/github.com/cloud-pi-native/console`; the
  isolation workspace becomes the sibling `../console.<unite>`.
- Artifact language (issues, PRs) is **French**; commits in English
  (conventional, SSH-signed — see `sks-commit` →
  `references/cloud-pi-native.md`).
- Reviewer requested at PR opening: `yorha-operator` (Automata account),
  subject to access.
- Push to `origin` only; PRs with `--head cloud-pi-native:<branch>`, base
  `main`, body `Refs #N` (not `Related:`).
