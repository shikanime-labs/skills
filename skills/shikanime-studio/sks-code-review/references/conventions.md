# Repo Conventions (enforced in review)

- **No AI-marker comments** — `ponytail:`, `claude:`, `gpt-4:` etc.; replace
  with a real _why_ comment; reject on sight.
- **Commits** — code repos: short imperative, no prefix/body/trailers, one
  commit per logical fix. Doc repos: `doc:` prefix.
- **License** — prefer Apache 2.0 for new repos.
- **Nix style** — inline single-key attrset (`a.b = v`); block for multi-key
  (`a = { b = 1; c = 2; }`); never mix on one line.
- **Go (xqbit/shikanime-labs)** — `jj` + ghstack flow; `gofmt` clean; PRs opened
  as drafts.
- **PR routing** — `shikanime/sk-*` : push to `origin` (the org repo), open
  `--head <org>:<branch>`. `cloud-pi-native/*` : push to `origin`, open
  `--head cloud-pi-native:<branch>`. Never mix.
- **Secrets** — never read/print/commit `.env` or credential files.
- **Agent identity** — commits co-authored by
  `Automata <automata@shikanime.studio>`; gh agent id `yorha-automata`. Do not
  switch `gh` auth.
