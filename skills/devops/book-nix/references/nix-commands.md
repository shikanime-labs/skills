# Nix Commands & Environment (distilled from nix.dev/manual/nix/2.28/command-ref)

## CLI surface

- **Classic (stable) commands**: `nix-env`, `nix-build`, `nix-instantiate`,
  `nix-store`, `nix-collect-garbage`, `nix-shell`, `nix-channel`.
- **New `nix` subcommands (experimental)**: `nix build`, `nix shell`, `nix develop`,
  `nix run`, `nix repl`, … conform to the XDG/standard layout by default. Enable via
  the experimental-features setting. Prefer classic commands unless the modern
  workflow is explicitly requested.

## Common environment variables

- `NIX_PATH` — colon-separated search paths resolving lookup paths like `<nixpkgs>`.
  Overrides the `nix-path` config setting; extend with `-I`. Empty string → lookup
  always fails (`error: file 'nixpkgs' was not found in the Nix search path`).
- `NIX_REMOTE` — set to `daemon` for multi-user installs (required); `unix://path`
  for a non-default socket; otherwise leave unset.
- `NIX_IGNORE_SYMLINK_STORE` — set `1` to allow a symlinked store (risky: can yield
  non-reproducible builds across machines). Prefer a `bind` mount instead
  (`mount -o bind /mnt/otherdisk/nix /nix`).
- `NIX_STORE_DIR` / `NIX_DATA_DIR` / `NIX_LOG_DIR` / `NIX_STATE_DIR` / `NIX_CONF_DIR`
  — override default locations.
- `NIX_CONFIG` — inline settings (newline-separated), treated like a config file.
- `NIX_USER_CONF_FILES` — `:`-list of config files to load.
- `TMPDIR` — build temp dir; can consume large disk. Default `/tmp`.
- `IN_NIX_SHELL` — `pure` or `impure`; tells you if the shell was set up by
  `nix-shell`.
- `NIX_SHOW_STATS=1` / `NIX_COUNT_CALLS=1` — debugging evaluation.

## XDG / Nix home dirs

- `XDG_CONFIG_HOME` (default `~/.config`), `XDG_STATE_HOME` (`~/.local/state`),
  `XDG_CACHE_HOME` (`~/.cache`).
- Nix-specific overrides: `NIX_CONFIG_HOME` (default `$XDG_CONFIG_HOME/nix`),
  `NIX_STATE_HOME`, `NIX_CACHE_HOME`.
- When `use-xdg-base-directories` is enabled: config dir resolves
  `NIX_CONFIG_HOME` → `XDG_CONFIG_HOME/nix` → `~/.config/nix`.

## Config files

- `nix.conf` (system or user) holds settings (binary caches, substituters,
  experimental-features, trusted-users, etc.).
- Lookup-path resolution and channel sources are config-driven.

## Quick verification

- `nix-env --version` — confirms a working Nix install.
- `echo $NIX_PATH` — shows `<nixpkgs>` resolution roots.
