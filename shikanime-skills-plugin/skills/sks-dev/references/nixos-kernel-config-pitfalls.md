# NixOS kernel option/patch pitfalls (nixos-hardware RPi kernels)

Verified 2026-09-02 on `shikanime-labs/machines` (fushi/minish RPi4,
kernel `linux-rpi-6.18.34-stable_20260609`, nixos-hardware `raspberry-pi-4`).
Companion to the `boot.kernelPatches` entry in the `nix-flake-authoring` skill.

## Comin deploy path vs bootstrap deploy path are independent

- **comin** (in-cluster puller) polls the remote configured in its
  `comin.yaml` — on these hosts `https://forgejo.i.shikanime.studio/...`,
  a cluster-internal Forgejo. If the public `*.i.shikanime.studio` DNS
  records are missing/conflicting (external-dns logs
  "conflicting record type candidates; discarding CNAME"), comin logs
  `repository not found` every poll and deploys NEVER land — regardless
  of what was pushed to GitHub.
- **sync2.sh** (bootstrap) clones from `https://github.com/shikanime-labs/...`
  directly over Tailscale SSH, bypassing Forgejo/DNS entirely.

When a pushed fix "isn't picking up" on a node, first identify which path
that node actually uses (`systemctl cat comin` / `jj` log on the node) —
a GitHub push alone does not reach comin-managed hosts.

## Diagnosing "kernel option didn't apply" end to end

1. Eval the option (`config.boot.kernelPatches`) — proves nothing, see
   `nix-flake-authoring` for why. Then check the real artifacts:
2. `nix eval
.#nixosConfigurations.<host>.config.boot.kernelPackages.kernel.patches --json`
   — is your patch/override even in the kernel package?
3. `nix build .#nixosConfigurations.<host>.config.boot.kernelPackages.kernel.configfile`
   then grep the CONFIG key — the only trustworthy build-side proof.
4. SSH the node: `readlink /run/current-system/kernel` — if the store path
   equals the eval'd drv path, the host is simply not updated yet (deploy
   path problem, not build problem).
5. Node connectivity: `ping <tailscale-ip>` works but SSH banner times out
   under load ≥ 40 (RPi4 building a kernel). Retry later; don't kill the
   remote builder session.

## Kernel-config builds on the aarch64 remote builder are SLOW

Building an `aarch64-linux` kernel configfile from the macOS host dispatches
to the aarch64 remote builder (see `/etc/nix/machines`) — which IS the RPi
node itself for `fushi`. Observed ~50 min under load (source `cp -r` phase
alone ran ~10 min). Run `nix build -L ...` with `background=true` +
`notify_on_complete=true` and continue other work; poll
`ps aux | grep cp -r` on the builder via a second SSH session if you need
progress signal.

## `gh pr checks --watch` blocks the terminal tool

`gh pr checks <n> --watch` exceeds the 580s foreground terminal cap and the
420s tool timeout on repos with heavy CI (system-closure builds). Run it with
`background=true, notify=true`, or poll with plain `gh pr checks <n> | grep
-E "pending|fail"` in a sleep loop instead of repeating the identical call —
the runtime flags 3+ identical foreground calls.

## Fix-verification options evaluated for the VA_BITS fix (2026-09-02)

All tested against `nixos-hardware` `raspberry-pi/common/kernel.nix`
(`buildLinux (args // {literals} // (args.argsOverride or {})).overrideAttrs`):

| Approach | Result |
| --- | --- |
| `boot.kernelPatches` | silently dropped (overrideAttrs detaches `.override`) |
| `.override { structuredExtraConfig }` on the NixOS config kernel | dropped same way |
| `.override { structuredExtraConfig }` on the flake-exposed `rpi4-kernel` | shadowed by kernel.nix's literal attrset; lands nowhere |
| `.override { argsOverride.structuredExtraConfig }` | lands, but REPLACES the whole attrset — vendor tweaks (`NR_CPUS=4`, `CMA`, `PREEMPT`) silently lost |
| `boot.kernelPackages = linuxPackagesFor (callPackage kernel.nix { injected buildLinux })` | works, but NixOS modules lack `inputs` (specialArgs empty) → needs 2-file change |
| **`nixpkgs.overlays` on `buildLinux`, guarded by `defconfig == "bcm2711_defconfig"`** | **chosen: merges (never replaces), scoped to the RPi kernel only, 1 file** |

See `nix-flake-authoring` skill for the final overlay code and the Kconfig
choice-merge rule (`ARM64_VA_BITS_39 = no` must accompany `..._48 = yes`).
