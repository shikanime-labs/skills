# Cloud-pi-native conventions

cloud-pi-native repos do NOT track the nixpkgs release calendar, even where
a repo roots a `flake.nix`:

- Work tracks the org-owned "Socle" project (project 2, owner
  `cloud-pi-native`) — card mechanics belong to `sks-project`.
- Milestones are semver per repo: bug → highest open patch on the current
  minor (max `Z`); enhancement → next minor/major. The patch milestone is
  the backport unit (`cpn-release-patch`).
- Release alignment is a shikanime-org concern only; a request to
  release-align a cloud-pi-native repo is redirected here, not executed.
