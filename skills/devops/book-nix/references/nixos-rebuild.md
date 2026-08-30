# nixos-rebuild (distilled from NixOS Manual §sec-changing-config, §sec-building-image)

## Applying the configuration

All commands must run as **root** (`sudo -i` or root shell). They do **not**
auto start/stop user services (only `daemon-reload` per user).

- `nixos-rebuild switch` — build, set as **boot default**, and activate in the
  running system (restarts affected system services).
- `nixos-rebuild test` — build + activate in the running system, but **not** the
  boot default. Reboot reverts to the previous config (safe for risk experiments).
- `nixos-rebuild boot` — build + set boot default, but do **not** switch now
  (takes effect after next reboot).
- `nixos-rebuild switch -p test` — puts the config in a GRUB submenu
  "NixOS - Profile 'test'", separating test from stable configs.
- `nixos-rebuild build` — build only, apply nothing. Use to confirm everything
  compiles.
- `nixos-rebuild repl` — REPL with config loaded into `config`; tab-complete;
  `:r` reload; `:?` help.
- `nixos-rebuild build-vm` then `./result/bin/run-*-vm` — boot the config in a QEMU
  VM (no host data) to test safely.

## Upgrade & sources

- `nixos-rebuild switch --upgrade` — update the channel, then build/switch.
- Use your own Nixpkgs tree: `nixos-rebuild switch -I nixpkgs=/path/to/my/nixpkgs`.

## Building images

- `nixos-rebuild build-image` — produce a (Live) ISO of the current config.
- `systemd-repart`-based images are also supported (see §sec-image-repart).

## Verification

- After `switch`/`test`, confirm the running system reflects the change
  (service active, file present). Use `nixos-rebuild build` in CI to gate
  syntax/type errors before applying.
