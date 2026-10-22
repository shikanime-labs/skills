---
name: sks-maintenance
description:
  "Use when maintaining the org's repos, fleet, and runtimes: renovate and
  language dependency bumps, nixpkgs/runtime upgrades, and the issue → PR →
  land → post-merge validation loop."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - maintenance
      - renovate
      - upgrade
      - nix
      - validation
    related_skills:
      - sks-renovate-sweep
      - sks-issue
      - sks-pr
      - sks-land
      - sks-project
      - sks-audit
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Maintenance

Keeping what already exists current: dependency updates, runtime and pin
upgrades, and the drift they leave behind. This is not feature work
(`sks-dev`) — a maintenance change ships no new behavior, and its merge is a
claim until the running system is re-read.

Two references load on demand: `references/shikanime.md` before the first
pass (repo paths, runtime roster, boards, landing mechanics, validation
commands, deeper-diagnosis routing) and `references/renovate.md` when landing
dependency PRs (the renovate pass, ecosystem by ecosystem).

## When to Use

- Renovate (or Dependabot) PRs to land, per language ecosystem.
- A runtime, pin, or digest to bump: a flake input or nixpkgs pin, a cluster
  runtime (knix/RKE2, kernel, containerd), an OCI image, a vendored source.
- A pinned dependency misbehaving — read its released changelog before
  touching the repo.
- After any maintenance merge: validate the running state, then close
  tracking.

## Two lanes

| Lane            | Change                                  | Proof                               |
| --------------- | --------------------------------------- | ----------------------------------- |
| A — dependency  | manifest + lockfile bump inside a repo  | the repo's CI on the exact head     |
| B — runtime     | a version a running system consumes     | post-merge validation of the system |

A one-line diff is lane B whenever a host, node, workload, or agent consumes
the version: no CI run can prove that.

## First checks

The symptom says which layer is lying; read it before editing anything:

| Symptom                                | Check                                            |
| -------------------------------------- | ------------------------------------------------ |
| Host missed a merged `machines` commit | `comin status` on the host; its Deployer sha vs `gh api repos/<org>/machines/commits/main --jq .sha` |
| Node NotReady or offline               | `kubectl get nodes -o wide`; `kubectl describe node <n>` |
| Flux Kustomization not Ready           | `kubectl get kustomizations -A -o json` → the Ready condition message |
| Rendered manifest ≠ live cluster       | diff the overlay against `kubectl get <kind> <name> -o yaml` |
| Deployed component lags a values key   | `helm get values <rel> -n <ns>` vs the manifest  |
| Vendored source hash breaks            | rebuild the fixed-output derivation, compare the hash |
| PVC full, storage must grow            | `kubectl get pvc -A`; `df -h` inside the pod     |
| NixOS config before a switch           | `nix flake check --accept-flake-config --no-pure-eval` |
| Trivial fix, no runtime impact         | land it; no post-merge validation loop needed    |

## Upgrade procedure

Ordered; each phase's gate holds before the next. One component per train,
applied in an isolated workspace (`sks-delegate`).

1. **Classify the lane** and pick exactly one component. Two versions in one
   PR make a failed validation unattributable.

2. **Fix the target.** Resolve the exact version, tag, or digest — never a
   moving ref (a branch URL). Read the released changelog and list the
   breaking changes that touch this fleet's consumers. A moving ref pins to
   its tag dereference, with the rev ≡ tag equivalence recorded.

3. **Open the tracking issue** (`sks-issue`): title `<component> <from> →
   <to>`; body is the problem statement; the `- [ ]` ledger is the
   command-decidable acceptance list and includes the post-merge
   running-state checks, not only build/eval ones. Triage it
   (`sks-issue-triage`), then board it with Status ready (`sks-project`).

4. **Record the rollback target** before applying anything: the previous
   version/digest/commit/pin and the command that returns to it. An upgrade
   with no named rollback is not ready. Post it as an issue comment
   (`sks-issue-refine`), never in the body.

5. **Apply in isolation.** A `sks-delegate` workspace off `main@origin`, the
   bump, then the repo's own gate: `nix fmt` plus the eval/build of the
   affected outputs (NixOS), tests and lint (code), a render diff
   (manifests). Commit per `sks-commit`.

6. **Open the PR** (`sks-pr`): `# Why` / `## What` / `## Verification` /
   `## References`, where Verification names the post-merge checks step 8
   will run. Link the issue as Development metadata; review it
   (`sks-pr-review`) before requesting the human gate.

7. **Land** (`sks-land`): squash pinned to the verified head, then confirm
   `main` advanced. Merge is a claim — nothing downstream follows from it
   yet.

8. **Validate the running state.** Deploy or converge first, then read the
   system, never the manifest:
   - NixOS fleet: the host's own comin poll delivers it, so `comin status`
     must show the merged sha and every touched unit must carry an
     `ExecMainStartTimestamp` after the merge — a switch restarts only units
     whose definition changed.
   - Cluster: node kubelet version, `kubectl rollout status` on the affected
     workloads, every replica on the new version, Flux Kustomizations Ready.
   - Service: the version the runtime reports (endpoint, CLI, the digest on
     the live object), never the declared value.
   - Agent and skill repos: the local mirror resync is the deploy — a merged
     skill or profile is not loaded until the checkout is rebased onto the
     new `main`.
   - Soak one full reconcile or poll cycle before declaring it done.

9. **Track and close.** Board card: ready, then in progress once the
   workspace exists, in review once the PR is open, and done only after step
   8 passed (`sks-project`). The issue closes N of N with the validation
   evidence quoted; merge alone closes nothing (`sks-land` post-merge).

10. **Record the outcome** on the issue: from and to, the evidence lines, and
    the rollback target that is now the previous good state. A failed
    validation reopens the card, leaves its ledger item unchecked, and lands
    the evidence as a comment.

## Rollback

- Rollback is a change, not a rescue: revert the commit or pin back to the
  recorded target through this same loop. Never edit a running host by hand
  and never leave the fleet half-applied — finish the rollout or return to
  the previous version, never both.
- Record the rejected version on the issue so the next pass does not retry it
  blind; re-target only once the blocker is fixed.

## Cadence

- Dependency sweeps run under standing authorization (green, and
  `references/renovate.md`); runtime upgrades are deliberate, sequential, and
  one component per train, issue, and ledger.
- Priority by blast radius: control plane > data > workloads > tooling.

## Pitfalls

- "Merged" is not "upgraded": hosts and workloads still run the old closure.
  Compare full store paths and live digests, not version tails.
- A config-only deploy keeps the same nixpkgs version tail while the store
  hash changes, so a watcher comparing tails never observes the deploy.
- Upgrading a moving ref breaks the hash on the next fetch; pin the tag
  dereference instead.
- Closing the issue on merge leaves its running-state items unproven.
- A fleet-wide pin bump puts every host on the same closure at once: a slow
  host is contention, not a broken config.

## Verification

```bash
gh pr checks <M> --repo <org>/<repo>              # green on the exact head
comin status && readlink /run/current-system      # on the host, after merge
kubectl get nodes -o wide && kubectl rollout status deploy/<name> -n <ns>
```

Report states: component, lane, issue and PR links, the validated
running-state evidence, rollback target, board card state.

## See also

- `sks-renovate-sweep` — the dependency pass, detailed in
  `references/renovate.md`.
- `sks-issue`, `sks-pr`, `sks-land` — the train each phase delegates to.
- `sks-project` — the tracking surface the phases mirror.
- `sks-audit` — the surface that finds maintenance work.
- `sks-fastlane` — trivial fixes that skip the train.
- `sks-gc` — retire the workspace and bookmark after landing.
