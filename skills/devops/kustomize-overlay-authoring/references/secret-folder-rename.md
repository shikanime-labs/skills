# Secret folder rename + refactor session (2026-09-03, PR 2134)

Session-specific detail behind `kustomize-overlay-authoring` → "Secret folder
naming convention".

## What changed

21 app-level dotenv secrets moved from `<secret>/` to `<secret>-env/`
folders; file names (`*.enc.env`) and Secret names unchanged. Ref wired in 17
overlay kustomizations (27 paths). List: immich, lldap, metatube, honcho,
honcho-postgres, immich-postgres, hermes-agent (later reverted), vaultwarden,
qbittorrent-cleanup, gitea-mirror, sonarr/radarr/lidarr/whisparr, prowlarr,
prowlarr-oidc-client, jellyfin, inference-{z-ai,nous,openrouter,mistral}.

Excluded (user-scoped): longhorn-hetzner-backups, cloudflare-api-token ×2,
operator-oauth ×2, hetzner, discord-webhook ×2, receiver-token ×2,
ai-gateway-session-seed, inference-gateway-apikey, catbox-sops-key.

Post-review adjustments (same PR, two more commits):
- hermes-agent reverted to `hermes-agent/` — user decided it keeps its
  original folder (its folder carries config.yaml + SOUL.md for other
  generators).
- servarr `config.enc.xml` split OUT of `<app>-env/` into its own `<app>/`
  folder: `sonarr/config.enc.xml` → Secret `sonarr` (startup-config mount),
  `sonarr-env/.enc.env` → Secret `sonarr-pkcs12-password`.

## Gotchas hit

1. **Rewire ALL source paths, not just `envs:`** — `files:` entries pointing
   into the renamed folder (`config.xml=sonarr/config.enc.xml`,
   `hermes-agent/config.yaml`) fail at `kustomize build` with
   `evalsymlink failure`, discovered only when building. Grep the
   kustomization for the old folder name, not just the envs line.
2. **Component dirs fail standalone on ANY commit** — `apps/*/components/*`
   kustomizations (26 of them) error `no resource matches strategic merge
   patch ... [noNs]` because they need a parent overlay. Verified identical
   on a HEAD worktree. Baseline your fleet sweep, don't chase pre-existing
   failures.
3. **Sibling agent rewrote the shared worktree** — a parallel `jj new
   main@origin` snapshot dropped all uncommitted `git mv` renames from the
   working copy. Recovered from dangling commit `nmskyytn` (found via
   `jj log`; `git fsck --lost-found` also lists candidates). Commit early,
   commit often in shared worktrees.
4. **`jj describe` + global config trap** — global jj
   `templates.commit_trailers` appends `Signed-off-by` + `Change-Id` on
   every describe; `manifests` rejects them. Always pass
   `--config='templates.commit_trailers=""'`. `jj squash
   --use-destination-message` RE-INTRODUCES them (it re-describes) — strip
   again with `jj describe -r <rev> --config=... --stdin` after any
   use-destination-message squash.
5. **`jj squash` opens the editor (`hx`, exit 101)** in non-interactive
   shells. Use `JJ_EDITOR=cat` or `--use-destination-message`.
6. **git stash pop conflicts on encrypted files**: conflict markers land in
   `.enc.*` files; resolve by keeping one side, then for files identical to
   HEAD just `git checkout HEAD -- <file>`. `git add` to clear the UU/AA
   state.
7. **sops round-trip on dotenv needs explicit types**:
   `sops -d --input-type dotenv --output-type dotenv <file>` — without
   them, sops tries binary/tree parsing and errors `no binary data found in
   tree` on perfectly valid dotenv ciphertext.

## Verification that passed

- 20/20 decrypt round-trips byte-identical (sorted-sha compare old vs new).
- Fleet sweep: 248 kustomizations; branch failures == HEAD failures + 0.
- `kustomize build` per touched overlay after each follow-up commit.
- PR opened from bookmark `refactor/enc-env-folders`; MERGEABLE; `nix fmt`
  clean ("formatted 44 files (21 changed)" — the fmt re-run after push must
  show 0 changed or be squashed).
