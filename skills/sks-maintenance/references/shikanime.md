# Shikanime maintenance scope — sks-maintenance

- Orgs: `shikanime-labs` and `shikanime-studio`; checkouts at
  `~/Source/Repos/github.com/<org>/<repo>`. The catalog checkout is the live
  `~/.hermes/skills` mirror (jj, origin `shikanime-labs/skills`); per-unit
  workspaces are siblings of it (`../skills.<unit>`).
- Repos carrying maintenance work: `machines` (fleet hosts), `manifests`
  (in-cluster apps), `knix` (cluster runtime module), `nix-containers` and
  `niximgs` (images), `actions` (CI), plus every catalog and app repo.
- Runtime roster: `nixpkgs` pinned `nixos-unstable` in the `machines` flake;
  the cluster runtime is RKE2 behind `services.knix` (role `server`/`agent`,
  token `sops.secrets.rke2-token`); Flux runs the manifests layer and reads
  GitHub directly, so cluster changes land before host changes; `comin`
  deploys each NixOS host from `main` through its `github` remote (600s poll)
  and the org's Forgejo mirror.
- Hosts: `ashira`, `manash`, `nalsha` (x86 servers), `fushi`, `minish`,
  `nemishi` (ARM), `kushira`, `sashina` (Strix Halo inference), `nixtar`
  (workstation), `automata` (KubeVirt guest), `telsha` (nix-darwin).
- Landing: `gh pr merge --squash --admin` pinned to the verified head
  (`--match-head-commit`) after the human gate. The org "Landing protections"
  ruleset requires code-owner review, so a plain `--squash` fails on
  `machines`; that repo also has auto-merge disabled repo-wide.
- Boards (owner `shikanime`): `Skills` (9) for this catalog, `Shikanime
  Studio` (6) for `sks-*` ops units such as `machines`, `manifests`, `knix`.
- Commit envelope: `Signed-off-by: Shikanime Deva
  <william.phetsinorath@shikanime.studio>` (gitlint CC1 on `manifests` and
  `skills`) plus `Co-authored-by: Automata <automata@shikanime.studio>`.
- Post-merge validation, by layer:
  - host: `comin status` (Deployer sha == the merged commit),
    `readlink /run/current-system`, and
    `systemctl show <unit> -p MainPID,ExecMainStartTimestamp,ActiveState` for
    each touched unit.
  - cluster: `kubectl get nodes -o wide` (kubelet version),
    `kubectl rollout status`, `kubectl get kustomizations -A` Ready.
  - mirror lag: `git ls-remote` the host's remote vs
    `gh api repos/<org>/machines/commits/main --jq .sha`.
- Deeper diagnosis: when a first check fails, load the installed skill that
  owns the layer — the recipe is theirs, not this skill's:
  - host never picks up a merged commit → `comin-fleet-deploy`
  - node NotReady or offline → `k8s-node-offline-diagnosis`
  - Kustomization wedged or oscillating → `flux-convergence-triage`
  - rendered manifest drifts from live → `flux-manifest-drift-audit`,
    `helm-values-drift`
  - pinned dependency misbehaves → `upstream-pin-freshness`
  - vendored override hash breaks → `nixpkgs-vendored-override-drift`
  - image pin on the mixed-arch fleet → `oci-image-digest-pinning`
  - major image bump over an old data dir → `stateful-image-upgrades`
  - PVC full, storage must grow → `k8s-volume-expansion`
  - requests/limits sized from VPA → `vpa-resource-sizing`
  - NixOS eval proof before a switch → `nixos-config-verification`
  - Linux build falls back to local from macOS → `machines-remote-build`
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
