# NixOS Configuration (distilled from NixOS Manual §sec-configuration-syntax, §sec-module-abstractions, §sec-modularity)

## The configuration file

- `/etc/nixos/configuration.nix` is a **Nix expression**: a function returning an
  attrset of option definitions.

  ```nix
  { config, pkgs, ... }:
  {
    services.httpd.enable = true;
    services.httpd.adminAddr = "alice@example.org";
  }
  ```

- `config` = the fully merged system config (lazy). `pkgs` = Nixpkgs set.
- Dotted option names are **nested-set shorthand**:
  `services.httpd.enable = true` ≡ `services = { httpd = { enable = true; }; }`.

## Value types

- **String**: `"dexter"`. Escape `"` with `\"`.
- **Multiline**: `''` … `''` strips common indentation; `"` and `\` are literal.
- **Boolean**: `true` / `false` (`networking.firewall.enable = true;`).
- **Integer**: `boot.kernel.sysctl."net.ipv4.tcp_keepalive_time" = 60;` — note the
  quotes: the key is a *literal kernel name*, not a nested option.
- **Set**: `fileSystems."/boot" = { device = "/dev/sda1"; fsType = "ext4"; options = ["rw" "relatime"]; };`
- **List**: whitespace-separated — `boot.kernelModules = [ "fuse" "kvm-intel" ];`.
- **Package**: via `pkgs` — `environment.systemPackages = [ pkgs.thunderbird pkgs.emacs ];`
  or swap a service's package: `services.postgresql.package = pkgs.postgresql_14;`.

## Type-checking

- Unknown option → `The option 'services.httpd.enable' … does not exist.`
- Wrong type → `The option value 'services.httpd.enable' … is not a boolean.`

## Abstractions

- `let commonConfig = { adminAddr = "alice@example.org"; forceSSL = true; }; in`
  then merge with `//`: `(commonConfig // { documentRoot = "/webroot/blog"; })`.
- Functions: `makeVirtualHost = webroot: { documentRoot = webroot; … };`.
- A `let` may appear wherever an expression is allowed; NOT as an attribute name.

## Modularity (configuration.nix IS a module)

- Split large configs: `imports = [ ./vpn.nix ./kde.nix ];`. Submodules share syntax.
- **List-typed options MERGE** across modules (concatenated; the importing module's
  value is appended *last*). Use `mkBefore` to prepend:
  `boot.kernelModules = mkBefore [ "kvm-intel" ];`.
- **Unique-typed options ERROR** on conflict:
  `The unique option 'services.httpd.adminAddr' is defined multiple times`.
  Force precedence with `pkgs.lib.mkForce`:
  `services.httpd.adminAddr = pkgs.lib.mkForce "bob@example.org";`.
- Cross-module reads use `config`:
  `environment.systemPackages = if config.services.xserver.enable then [ pkgs.firefox ] else [ ];`

## Inspection

- `nixos-option services.xserver.enable` — prints the merged value.
- `nix repl` — REPL with the config in `config`; `:r` reloads, `:?` help.
