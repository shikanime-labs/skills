# cloud-pi-native specifics for parallel fan-out

Load when working in the cloud-pi-native/console repository.

## Org identity

- Default repo: `cloud-pi-native/console`; push to `origin` only (the org
  remote), PRs opened with `--head cloud-pi-native:<branch>`.
- Commit attribution trailer on every commit (operator instruction):
  `Co-authored-by: Automata <automata@shikanime.studio>`.
- Artifact language: issues, discussions, and PR bodies in **French**;
  commits in English (conventional, per the commitlint config — see
  `sks-commit` → `references/cloud-pi-native.md`).

## Fan-out deltas vs the generic procedure

- Landing uses **draft PRs**; before opening each PR run the duplicate/stack
  check (`cpn-pr` step 1b): an open PR already covering the unit means push to
  it or stack on it — never a second PR for the same change.
- PR↔issue linkage: `Refs #N` by default (not `Related:`).
- Dispatch example (one task per leaf, French goal, trailer in the contract):

```python
delegate_task(tasks=[
    {"goal": "Implémenter <repo>.<unit>: <contrat>. Workspace: "
             "../<repo>.<unit>. Gates: <N>. Commit conventionnel + "
             "trailer Automata.",
     "context": "dépôt cloud-pi-native/<repo> ; racine trunk ; un workspace "
                "par unité.",
     "toolsets": ["terminal", "file"]},
])
```

- The parent re-verifies each leaf's gate via `terminal` in its workspace
  before declaring done; retire with `jj workspace forget`.
