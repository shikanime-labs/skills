# Skills

A curated catalog of self-improved agent skills for
[Hermes](https://hermes-agent.nousresearch.com/docs) and compatible agents.

This catalog encodes **two parallel org workflows** distilled from practice —
the shikanime `sks-*` family and the cloud-pi-native `cpn-*` family — covering
the full lifecycle: **discussion → issue → issue comments → PR**, with
proven-done gates, assumption validation, jj-workspace parallel fan-out, and
stacked PR landing. A third, standalone `nixpkgs` family (`nix-pr-*`) reviews
upstream NixOS/nixpkgs pull requests through the official contribution
process.

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
npx skills add shikanime-labs/skills --skill sks-dev-workflow -g

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
hermes skills install shikanime-labs/skills/shikanime-studio/sks-dev-workflow

# Or copy manually
cp -r skills/shikanime-studio/sks-dev-workflow ~/.hermes/skills/shikanime-studio/
```

### Install via npm

```bash
# Install as an npm package (skills are bundled via the agents field)
npm install @shikanime-labs/skills

# Then export to your agent's skill directory
npx agents export --target claude
```

The `agents` field in `package.json` and the `skills.json` manifest at the repo
root enable discovery by npm-based skill managers. Both list the skills below.

## The Two Workflows

Two orgs, one doctrine. The lifecycle is identical — **discussion → issue →
issue comments → PR** — with org-specific conventions:

- **shikanime (`sks-*`)**: plain English commits with the Automata co-author
  trailer, plain `gh pr` landing, direct push on explicit instruction.
- **cloud-pi-native (`cpn-*`)**: French artifacts, conventional commits, PRs
  pushed to origin from `cloud-pi-native/*`, Release Please versioning.

Shared doctrine across both families:

1. **Issue-first** — a PR always solves an issue; the issue body is the problem
   statement, acceptance criteria are a command-decidable tasklist (the gate
   ledger), findings go in comments.
2. **Done is proven, not asserted** — every landing claim is verified against
   real command output; a red check is surfaced, never `--admin`'d past.
3. **Validate assumptions before work** — probe identity, push rights,
   toolchain, and issue existence; report `BLOCKED:` with evidence and a
   recovery path rather than silently narrowing scope.
4. **Parallelize in a graph** — `sks-async` splits multi-unit work into jj
   workspaces (fan-out), joins with multi-parent commits, lands as independent
   PRs or stacked chains.
5. **Many-to-many linkage** — link PRs with `Related:` / `Issues liées:`; avoid
   auto-close keywords; close deliberately after verifying the ledger.

## What's Here

All skills follow the [Agent Skills](https://agentskills.io/specification)
specification, compatible with the
[Hermes format](https://hermes-agent.nousresearch.com/docs).

### shikanime family

| Skill                   | Description                                                                                                                  |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `sks-adversarial`       | Disposable sandbox for uncertain results: probe via sks-isolate/sks-async, then promote or discard                           |
| `sks-async`             | jj workspace fan-out + stacked PRs for parallel work                                                                         |
| `sks-commit`            | shikanime commit style + Automata co-author trailer                                                                          |
| `sks-curate`            | Update, improve, compress, and token-optimize skills in the catalog                                                          |
| `sks-dev-workflow`      | Branch/push discipline, gates, landing                                                                                       |
| `sks-discussion`        | RFC Discussions (pre-issue stage)                                                                                            |
| `sks-discussion-triage` | Discussion triage: category + lifecycle (GraphQL)                                                                            |
| `sks-doc`               | Repo `docs/` knowledge base (internal ops + optional user docs) as reviewable in-repo Markdown                               |
| `sks-gc`                | Reclaim dangling bookmarks, skill-created jj workspaces, and leftover working-copy dirs from sks-async/sks-dev-workflow      |
| `sks-investigate`       | Root-cause a bug/test/build failure before any fix; minimal repro + proven verification                                      |
| `sks-isolate`           | Isolate one unit of shikanime work in a fresh jj workspace; bookmarks + pushes scoped to that workspace                      |
| `sks-issue`             | Issues with the gate-ledger tasklist                                                                                         |
| `sks-issue-refine`      | Iterate a problem to convergence within its issue via research + comments                                                    |
| `sks-issue-triage`      | Issue triage: metadata + rationale closes                                                                                    |
| `sks-issue-workflow`    | Issue side end-to-end: create → refine → triage                                                                              |
| `sks-land`              | Merge PRs after DoD + review gates pass                                                                                      |
| `sks-pr`                | PRs derived from the commit, pushed to origin                                                                                |
| `sks-pr-resolve`        | Reconcile PR review threads + ledger, report readiness without merging                                                       |
| `sks-pr-review`         | Code review: YAGNI, root-cause, conventions                                                                                  |
| `sks-pr-triage`         | PR triage: metadata, reviewers, issue linkage                                                                                |
| `sks-stack`             | Single-unit jj workspace isolation primitive: fork a clean workspace from `main@origin`, push, hand off to PR workflow       |
|                         | `sks-pr-workflow`                                                                                                            |
| `sks-restack`           | Restack a jj stack onto moved main and resolve every conflict (jj marker dialect, :ours/:theirs, push gate)                  |
| `sks-converge`           | Resolve jj conflicts and divergent changes after a tree move: per-revision resolution, twin abandonment, push gate          |
| `sks-swarm`             | Distribute a task across an agent cluster over A2A: route by capability, machine, and runner pressure (optionally sandboxed) |
| `sks-update`            | Update the whole catalog by default (or named skills): curate, ship via dev workflow, resync to local Hermes agents                      |

### cloud-pi-native family

| Skill                   | Description                                                                                           |
| ----------------------- | ----------------------------------------------------------------------------------------------------- |
| `cpn-async`             | Fan-out parallèle sur workspaces jj + PR en stack                                                     |
| `cpn-commit`            | Conventional commits for console                                                                      |
| `cpn-dev-workflow`      | Console repo dev loop, gates, PR workflow                                                             |
| `cpn-discussion`        | French Discussions via GraphQL                                                                        |
| `cpn-discussion-triage` | Triage de discussion : catégorie + cycle (GraphQL)                                                    |
| `cpn-issue`             | French issue templates + gate ledger                                                                  |
| `cpn-issue-refine`      | Raffine un problème vers la convergence dans l'issue                                                  |
| `cpn-issue-triage`      | Triage d'issue : métadonnées + fermetures motivées                                                    |
| `cpn-issue-workflow`    | Workflow issue : créer → raffiner → trier                                                             |
| `cpn-pr`                | French PRs, pushed to origin, conventional                                                            |
| `cpn-pr-resolve`        | Réconcilie les threads de review, rapporte sans merger                                                |
| `cpn-pr-review`         | Review console PRs: arch, French artifacts                                                            |
| `cpn-pr-triage`         | Triage de PR : métadonnées, reviewers, lien issue                                                     |
| `cpn-pr-workflow`       | Workflow PR : issue liée → PR draft → trier                                                           |
| `cpn-release-patch`     | Backporte l'écart entre deux tags release sur une branche hotfix pour release-please                    |
| `cpn-stack`             | Isolation d'une unité en workspace jj frais : fork propre depuis main@origin, bookmark + push limités |
| `cpn-swarm`             | Essaim d'agents A2A : routage par capacité, machine et pression runner                                |

### nixpkgs family

Standalone skills for reviewing upstream
[NixOS/nixpkgs](https://github.com/NixOS/nixpkgs) pull requests — distinct from
the org workflows above.

| Skill           | Description                                                         |
| --------------- | ------------------------------------------------------------------- |
| `nix-pr-review` | Review an upstream nixpkgs PR: build changed packages with nixpkgs-review and check the diff against nixpkgs conventions |

### reference (book-*) family

Distilled documentation knowledge bases for libraries, toolchains, and
platform components — loaded on demand via `skill_view`. These carry the
`book-` prefix and are organized by domain under `skills/`.

| Skill                     | Description                                                                                        |
| ------------------------- | -------------------------------------------------------------------------------------------------- |
| `book-cert-manager`       | cert-manager install, issuers, and certs reference                                                 |
| `book-envoy-gateway`      | Reference for Envoy Gateway concepts, install, and tasks                                            |
| `book-external-dns`       | ExternalDNS ops, annotations, and provider pitfalls                                                |
| `book-fluxcd`             | Flux Toolkit controllers, CRDs, and CLI reference                                                  |
| `book-k8s-gateway-api`    | Gateway API reference: resources, routes, TLS, mesh                                               |
| `book-longhorn`           | Distilled Longhorn 1.12.1 documentation knowledge base                                             |
| `book-nix`                | Distilled reference for Nix, NixOS, and Nixpkgs manuals                                            |
| `book-victoria-metrics`   | VictoriaMetrics reference: metrics, queries, cluster, ops                                          |
| `book-victorialogs`       | VictoriaLogs: data model, LogsQL, ingestion, querying, ops                                         |
| `book-kameo`              | Distilled reference for the Kameo Rust actor framework                                             |
| `book-nestjs`             | NestJS patterns and APIs distilled from official docs                                              |
| `book-pnpm`              | Use when managing pnpm deps, workspaces, or lockfile                                              |
| `book-rust`               | Distilled Rust Book and Reference knowledge base                                                   |
| `book-vite`              | Use when configuring Vite, vite.config, or the dev server                                         |
| `book-vitest`             | Use when adding or running Vitest tests and config                                                 |
| `book-vue3`              | Vue 3 guide distilled: reactivity, components, composables                                         |
| `book-llama-cpp`          | Local llama.cpp GGUF inference, serving, and Hub discovery                                         |
| `book-nushell`            | Nushell book distilled: types, pipelines, commands, modules                                        |

## Development

```bash
nix develop
```

Format Nix files before committing:

```bash
nix fmt
```

### Evals

Every skill carries `evals/evals.json` — realistic prompts plus assertions, in
the agentskills.io test-case format. Each entry has a positive case (the skill
should fire) and a negative case (a near-miss that should not). Assertions
check: frontmatter parses, `name` matches the directory, the description is an
imperative `Use when …` / `À utiliser quand …` under 200 characters, no
cross-family prefix leak, body depth, and — against a baseline — description
token recall and body-size ratio. Commit `evals/evals.json` alongside any skill
change; a failing assertion blocks the merge.

## License

Apache 2.0 — See [LICENSE](./LICENSE) for details.
