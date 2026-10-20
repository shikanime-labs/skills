# Shikanime org conventions

Load when operating in a shikanime org (shikanime-labs / shikanime-studio):
local checkout layout and push signing.

## Local checkouts

Org repos are cloned under `~/Source/Repos/github.com/<org>/<repo>`; jj
workspaces for a repo sit next to it as siblings
(`<repo>.<workspace>`).

## Push signing

This host pushes with `--config signing.behavior=drop --config
git.sign-on-push=false` (key in no agent); GitHub squash-merge re-signs
server-side.
