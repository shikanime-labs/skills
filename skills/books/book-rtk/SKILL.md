---
name: book-rtk
description: Use when auditing or wiring the rtk-rewrite Hermes plugin.
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - rtk
      - hermes
      - cli
      - output-compression
      - hooks
    related_skills:
      - hermes-host-config
      - book-nix
      - sks-dev-workflow
      - sks-investigate
---

# RTK Reference

Distilled knowledge of rtk-ai/rtk: a Rust CLI that rewrites LLM-facing shell
commands into token-compact equivalents. Covers the `rewrite` contract, the
Hermes `rtk-rewrite` plugin, its Nix wiring in shikanime-labs/machines, and
the audit method proven in the 2026-09-09 keep-evaluation. Verified against
rtk 0.45.0 (plugin source tags v0.44.0 → v0.45.0).

## When to Use

- Auditing whether the rtk-rewrite Hermes plugin earns its place (gains vs
  losses) or diagnosing unexpected command-output changes.
- Writing tooling that shells out to `rtk rewrite` (hook authors).
- Bumping the plugin source pin in machines, or explaining why it must track
  the rtk binary version.
- Debugging "my command output looks different than expected" on fleet hosts.

## Quick Reference

```bash
rtk rewrite "git status"       # exit 0 OR 3 = rewritten (stdout = new cmd)
                               # exit 1 = no equivalent -> passthrough
rtk --version                  # deployed binary version (compare to pin)
rtk git status                 # direct compact invocation (no rewrite)
rtk read FILE                  # file content with "intelligent filtering"
```

- Rewrite contract: `{0,3}` accept output as rewrite; `{1,2}` passthrough;
  anything else is an error worth surfacing. **Exit 3 is success** — code
  that treats nonzero as failure misreads every rewritten command.
- Pipelines (`grep -rn x | head -20`, `find . | head`) return rc 1 — the
  rewriter does not decompose pipelines; whole command passes through.
- Machine-readable formats are preserved (measured byte-identical):
  `git status --porcelain`, `git log --pretty=format:%H`, and kubectl `-o
  json` (empty-items result verified; non-empty JSON untested). rtk is
  format-aware at runtime, not by flag-stripping.
- Compression measured on machines repo: `kubectl get pods -A` 50,688 → 98
  bytes (99%, plus a failure-only summary that surfaces broken pods raw
  output buries), `git status` −83%, `ls -la` −72%, `git log --oneline`
  parity. Rewrite latency ~0.02s.
- No `rtk stats` or usage counter exists — production fire-rate cannot be
  measured; audit via probe commands + journal absence of `rtk:` warnings.

## Hermes plugin (hooks/hermes/rtk-rewrite)

Mechanism, from source (`__init__.py`, ~90 lines):

- Registers `pre_tool_call`; acts ONLY on `tool_name == "terminal"` with a
  non-empty string `args["command"]`.
- Runs `rtk rewrite <command>` (shell=False, 2s timeout, capture). On
  timeout/exception/unexpected rc: warns once to stderr and fails OPEN —
  the original command executes unchanged.
- Mutates `args["command"]` in place when output differs from input.
- Missing binary → hook never registers, one warning.

## Fleet wiring (machines)

- `pkgs/hermes-plugin-rtk-rewrite/default.nix`: symlinkJoin over
  `fetchFromGitHub` tag `<X>/hooks/hermes/rtk-rewrite` — plugin SOURCE pin.
- The rtk BINARY comes from nixpkgs separately (`environment.systemPackages`,
  `extraPackages`). Two version sources → pin drift is the recurring defect.
  Rule: `rev` in the derivation should track the deployed `rtk --version`.
- Enabled on: NixOS fleet profile (`modules/nixos/profiles/ai.nix` —
  `extraPlugins` + `plugins.enabled`), darwin workstation
  (`modules/home/workstation.nix`, + `rtk-rewrite.allow_tool_override`).
- Hook source has been byte-identical across tags (v0.44.0 vs v0.45.0
  verified by diff) — pin bumps are often zero-behavior hygiene.

## Procedure — keep/remove audit (proven method)

1. Inventory the surface: grep the repo for the tool name (derivation, both
   OS profiles, enable lists, overrides) — know the blast radius first.
2. Read the hook/plugin source at the pinned tag, not docs — define the
   exact success/failure contract before measuring.
3. Black-box probe: run representative commands through `rtk rewrite`,
   classify by EXIT CODE (remember {0,3} = rewritten). Include pipelines,
   machine-readable forms, and unsupported tools.
4. Measure both columns: byte-size raw vs rewritten on real repos/clusters;
   spot-check retention (does compressed output keep the failure signal?);
   byte-diff porcelain/pretty/json outputs; time the rewrite.
5. Field telemetry: grep local agent log + fleet `journalctl -u
   hermes-agent` for `rtk:` warnings over the deployment window.
6. Drift check: deployed `rtk --version` vs derivation `rev`; diff the hook
   source across the two tags to separate behavior risk from hygiene.
7. Decide. If keep + defect, fix in a fresh jj workspace (`sks-stack`),
   verify with `nix build .#hermes-plugin-rtk-rewrite` + byte-diff output
   vs the deployed store path, then land per dev loop.

## Pitfalls

- Exit 3: nonzero but success. Scripts and tests misclassifying rc 3 report
  every rewritten command as passthrough (the 2026-09-09 audit's own first
  measurement script had this bug).
- `rtk read` applies filtering — file content fetched through a rewritten
  `cat`/`read` may drop bytes. Agents needing exact content should use the
  native `read_file` tool, which bypasses the rewrite (different tool name).
- Empty-cluster `-o json` parity does not prove non-empty parity; re-verify
  against a populated namespace before trusting JSON passthrough broadly.
- A silent plugin is the healthy state; any `rtk: hermes plugin warning:`
  line in stderr/journal is the failure signal to chase.

## Verification

Audit conclusions hold when: probe classification matches the {0,3}/{1,2}
contract, machine-readable diffs are empty, warning greps are empty over the
window, and pin == binary version. After a pin bump: `nix build
.#hermes-plugin-rtk-rewrite` succeeds and the new store path's files diff
clean against the currently deployed plugin path.
