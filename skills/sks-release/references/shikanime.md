# shikanime release facts

Org-specific values for `sks-release` when cutting releases in the
shikanime orgs (`shikanime-labs`, `shikanime-studio`):

- Release repo: `shikanime-labs/skills` — the catalog itself is the
  release unit; checkouts at `~/Source/Repos/github.com/<org>/<repo>`.
- The signed-tag plain-git rule is recorded in the repo's `AGENTS.md`
  Version Control section: jj trips `pre_receive` on signed annotated
  tags — `git tag -s` + `git push origin vX.Y.Z` from the main checkout.
- Manifest version fields: `skills.json` and `package.json` both carry a
  top-level `version` equal to the last tag — bump both in one commit.
- Previous cuts: `v2.0.0` (2026-08-25, signed annotated tag, empty release
  body — the defect the mandatory-notes gate exists to prevent).
- `machines` cuts releases the same way (`v1.0.0`); `manifests` and
  `cloud-pi-native-core` ship no releases — do not cut there.
