# Manifests repo: git commit and PR pitfalls

The `manifests` repo uses plain `git` (not jj). The `sks-dev-workflow` skill's
jj recipes don't apply — use these git-specific rules.

## Detached HEAD → create branch before push

```bash
git checkout -b <branch-name> && git push -u origin <branch-name>
```

On the first push, omit the `-u` on the initial `git push` and use
`git push -u origin <branch>` on the second call.

## Commit convention (verified 2026-09-07)

**MANDATORY:** `Co-authored-by: Automata <automata@shikanime.studio>` AND
`Signed-off-by: Shikanime Deva <william.phetsinorath@shikanime.studio>`.

gitlint CC1 REJECTS commits without a `Signed-off-by` line — the hook is
enforced by `.gitlint` in the repo root. Match this exact shape:

```bash
git commit -m "Rename OIDC SecurityPolicy metadata names to xxx-oidc-client

Align SecurityPolicy metadata.name with the Secret name (xxx-oidc-client)
across prowlarr, radarr, whisparr, sonarr, and copyparty overlays.

Co-authored-by: Automata <automata@shikanime.studio>
Signed-off-by: Shikanime Deva <william.phetsinorath@shikanime.studio>"
```

## Push + PR envelope (verified 2026-09-07)

```bash
# Stage only your intended files — never git add -A after a formatter
git add apps/prowlarr/overlays/nishir/securitypolicy.yaml ...

# Commit with the full trailer set
git commit -m "..."  # (see above)
git push -u origin feat/oidc-client-securitypolicy-name

# Open PR — body via file, NEVER inline
gh pr create --repo shikanime-labs/manifests \
  --base main \
  --head shikanime-labs:feat/oidc-client-securitypolicy-name \
  --title "Rename OIDC SecurityPolicy metadata names to xxx-oidc-client" \
  --body-file /tmp/pr-body.md

# NEVER use --label without knowing it exists — labels may be restricted
# (gh pr create --label oidc → "could not add label: 'oidc' not found")

# Verify the PR landed with real content — the success line proves nothing
gh pr view 2177 --repo shikanime-labs/manifests --json body,headRefOid,state \
  --jq '.body | length, .headRefOid, .state'
```

**Critical:** the `gh pr create` return line shows a URL but NOT the PR
number. You MUST extract the number via:

```bash
gh pr list --repo shikanime-labs/manifests --head <branch> --json number,url,state
```

or by reading the URL directly (`https://github.com/shikanime-labs/manifests/pull/2177`).

## Anti-patterns to avoid

- **NEVER `git commit --amend` on a tree touched by `nix fmt`** — nix fmt
dirts ~64 unrelated files; amending collapses the PR into base and GitHub
auto-closes it. Recipe: whole-tree `nix fmt`, then `git checkout --` everything
outside your scope before staging.
- **NEVER inline `--body "..."` in gh pr create** — shell expansion silently
executes backticks/`$` as commands. Write body to file, pass `--body-file`.

### OIDC SecurityPolicy naming convention (verified 2026-09-07)

The `SecurityPolicy` `metadata.name` field MUST match the `clientSecret.name`
field in the same resource (e.g. both `sonarr-oidc-client`). Having
`metadata.name: sonarr-oidc` while `clientSecret.name: sonarr-oidc-client` is
an inconsistency that causes auth failures — the Envoy Gateway cannot resolve
the Secret by the mismatched name.

Pattern across all shikanime apps (prowlarr, radarr, whisparr, sonarr,
copyparty):

```yaml
apiVersion: gateway.envoyproxy.io/v1alpha1
kind: SecurityPolicy
metadata:
  name: <app>-oidc-client    # MUST match clientSecret.name below
  namespace: shikanime
spec:
  targetRefs:
    - name: <app>
      kind: HTTPRoute
      group: gateway.networking.k8s.io
  oidc:
    provider:
      issuer: https://accounts.i.shikanime.studio
    clientID: <app>
    clientSecret:
      name: <app>-oidc-client  # matches metadata.name
    redirectURL: https://<app>.i.shikanime.studio/oauth2/callback
```

- **NEVER push a branch without verifying the remote ref actually moved** —
  `git ls-remote origin refs/heads/<branch>` must equal local HEAD. A force-push
  landing `origin/main`'s SHA collapses the diff and auto-closes the PR.
