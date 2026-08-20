# Skills

A curated catalog of self-improved agent skills for
[Hermes](https://hermes-agent.nousresearch.com/docs) and compatible agents.

This catalog encodes **two parallel org workflows** distilled from practice —
the shikanime `sk-*` family and the cloud-pi-native `cpn-*` family — covering
the full lifecycle: **discussion → issue → issue comments → PR**, with
proven-done gates, assumption validation, jj-workspace parallel fan-out, and
stacked PR landing.

## Quick Start

### Install via npx skills (Claude Code, Codex, Cursor, OpenCode, …)

[skills.sh](https://skills.sh/) is the open agent skills registry. Install any
skill from this repo:

```bash
# List available skills
npx skills add shikanime-labs/skills --list

# Install all skills globally
npx skills add shikanime-labs/skills -g -y

# Install a specific skill
npx skills add shikanime-labs/skills --skill sk-dev-workflow -g

# Install all skills for specific agents
npx skills add shikanime-labs/skills -g -a claude-code -a cursor -y
```

### Install as a Hermes skill source

Add the repo as a tap:

```bash
# Add as a tap
hermes skills tap add shikanime-labs/skills

# Verify loaded skills
hermes skills list
```

### Install individual skills

```bash
# Install a single skill from the tap
hermes skills install shikanime-labs/skills/shikanime/sk-dev-workflow

# Or copy manually
cp -r skills/shikanime/sk-dev-workflow ~/.hermes/skills/shikanime/
```

### Install via npm

```bash
# Install as an npm package (skills are bundled via the agents field)
npm install @shikanime-labs/skills

# Then export to your agent's skill directory
npx agents export --target claude
```

The `agents` field in `package.json` and the `skills.json` manifest at the repo
root enable discovery by npm-based skill managers. Both list the 11 skills
below.

## The Two Workflows

Two orgs, one doctrine. The lifecycle is identical — **discussion → issue →
issue comments → PR** — with org-specific conventions:

- **shikanime (`sk-*`)**: plain English commits with the Automata co-author
  trailer, `gh stack` landing, direct push on explicit instruction.
- **cloud-pi-native (`cpn-*`)**: French artifacts, conventional commits,
  upstream-only PRs from `cloud-pi-native/*` (never a fork), Release Please
  versioning.

Shared doctrine across both families:

1. **Issue-first** — a PR always solves an issue; the issue body is the problem
   statement, acceptance criteria are a command-decidable tasklist (the gate
   ledger), findings go in comments.
2. **Done is proven, not asserted** — every landing claim is verified against
   real command output; a red check is surfaced, never `--admin`'d past.
3. **Validate assumptions before work** — probe identity, push rights,
   toolchain, and issue existence; report `BLOCKED:` with evidence and a
   recovery path rather than silently narrowing scope.
4. **Parallelize in a graph** — `sk-async` splits multi-unit work into jj
   workspaces (fan-out), joins with multi-parent commits, lands as independent
   PRs or stacked chains.
5. **Many-to-many linkage** — link PRs with `Related:` / `Issues liées:`; avoid
   auto-close keywords; close deliberately after verifying the ledger.

## What's Here

All skills follow the [Agent Skills](https://agentskills.io/specification)
specification, compatible with the
[Hermes format](https://hermes-agent.nousresearch.com/docs).

### shikanime family (`skills/shikanime/`)

| Skill             | Description                                          |
| ----------------- | ---------------------------------------------------- |
| `sk-dev-workflow` | Branch/push discipline, gates, landing               |
| `sk-async`        | jj workspace fan-out + stacked PRs for parallel work |
| `sk-commit`       | shikanime commit style + Automata co-author trailer  |
| `sk-discussion`   | RFC Discussions (pre-issue stage)                    |
| `sk-issue`        | Issues with the gate-ledger tasklist                 |
| `sk-pr`           | Fork-first PRs derived from the commit               |

### cloud-pi-native family

| Skill              | Description                               |
| ------------------ | ----------------------------------------- |
| `cpn-dev-workflow` | Console repo dev loop, gates, PR workflow |
| `cpn-commit`       | Conventional commits for console          |
| `cpn-discussion`   | French Discussions via GraphQL            |
| `cpn-issue`        | French issue templates + gate ledger      |
| `cpn-pr`           | French PRs, upstream-only, conventional   |

## Development

```bash
nix develop
```

Format Nix files before committing:

```bash
nix fmt
```

## License

Apache 2.0 — See [LICENSE](./LICENSE) for details.
