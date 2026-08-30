# NixOS Packages, Users, Filesystems (distilled from NixOS Manual §sec-package-management, §sec-user-management, §ch-file-systems)

## Two package-management styles

1. **Declarative** — set `environment.systemPackages` in `configuration.nix`, then
   `nixos-rebuild switch`. Consistent, reproducible set.
2. **Ad-hoc** — `nix-env` CLI. Mixes versions; only choice for non-root users.

### Declarative

```nix
{ environment.systemPackages = [ pkgs.thunderbird ]; }
```

- Uninstall = remove from the list + `switch`.
- Some packages also need a NixOS **module** (D-Bus/systemd registration); check
  the options list before assuming `systemPackages` suffices.
- List available: `nix-env -qaP '*' --description` — first column is the attribute
  name (e.g. `nixos.thunderbird`). The `nixos` prefix is CLI-only; in config use
  the `pkgs` variable.

### Customising packages

- Allow unfree (this NixOS config only): `nixpkgs.config = { allowUnfree = true; };`
- Package extensions:

  ```nix
  environment.systemPackages = with pkgs; [
    (pass.withExtensions (s: with s; [ pass-otp ]))
    (python3.withPackages (s: with s; [ requests ]))
  ];
  ```

- **Local (non-global) override**: `(pkgs.emacs.override { gtk = pkgs.gtk3; })`
  (parens required — list vs function application).
- **overrideAttrs** (change `mkDerivation` inputs, e.g. source):

  ```nix
  (pkgs.emacs.overrideAttrs (oldAttrs: { name = "emacs-25.0-pre"; src = /path/to/tree; }))
  ```

- **Global override** (everything depends on your instance):

  ```nix
  nixpkgs.config.packageOverrides = pkgs: { emacs = pkgs.emacs.override { gtk = pkgs.gtk3; }; };
  ```

  `pkgs.emacs` inside refers to the *original* to avoid infinite recursion.

### Adding a custom package

- In-tree: clone nixpkgs, add, submit PR.
- Out-of-tree: define `stdenv.mkDerivation` directly in `configuration.nix` or an
  imported file; test with `nix-build my-hello.nix && ./result/bin/hello`.
- Pre-built executables usually **won't** run on NixOS; exceptions are **flatpak**
  and **AppImage** (`programs.appimage.enable = true; programs.appimage.binfmt = true;`).

## Ad-hoc (nix-env)

- `nix-env -iA nixos.thunderbird` — `-A` = attribute name (fast, unambiguous);
  without it, matches by package name (slower, ambiguous). As root →
  `/nix/var/nix/profiles/default` (all users); as user → per-user profile.
- Upgrade channel: `nix-channel --update nixos`, then `nix-env -i`. Or `nix-env -u '*'`
  to upgrade all. `nix-env -e thunderbird` uninstall; `nix-env --rollback`.

## User management

- Declarative:

  ```nix
  users.users.alice = {
    isNormalUser = true; home = "/home/alice";
    extraGroups = [ "wheel" "networkmanager" ];
    openssh.authorizedKeys.keys = [ "ssh-dss AAAAB3Nza... alice@foobar" ];
  };
  ```

  No password by default; set via `passwd` (retained across rebuild) or
  `hashedPassword` (set `users.mutableUsers = false` to make `/etc/passwd`/`group`
  congruent to config and disable `useradd`). uid/gid auto-assigned or manual.
- Imperative: `useradd -m alice`, `passwd alice`, `userdel -r alice`, `groupadd`, …
- `systemd.sysusers.enable = true` (experimental) — removes perl dep.
- `services.userborn.enable = true` (recommended experimental) — can update
  passwords, warns on insecure hashing; `services.userborn.passwordFilesLocation`
  stores passwd/group/shadow outside `/etc`.

## Filesystems

```nix
fileSystems."/data" = { device = "/dev/disk/by-label/data"; fsType = "ext4"; options = [ "rw" "relatime" ]; };
```
