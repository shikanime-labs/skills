# Skills

A curated catalog of self-improved agent skills for
[Hermes](https://hermes-agent.nousresearch.com/docs) and compatible agents.

This catalog encodes **one org-agnostic workflow** distilled from practice,
covering the full lifecycle: **discussion → issue → issue comments → PR**,
with proven-done gates, assumption validation, jj-workspace parallel fan-out,
and stacked PR landing. Organization-specific conventions (shikanime,
cloud-pi-native, upstream nixpkgs review) live behind per-skill references
and load only when working in that org's repos.

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
hermes skills install shikanime-labs/skills/sks-dev-workflow

# Or copy manually
cp -r skills/sks-dev-workflow ~/.hermes/skills/sks-dev-workflow
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

## One Workflow, Per-Org Flavors

One lifecycle everywhere — **discussion → issue → issue comments → PR**. The
issue body is the problem statement, acceptance criteria are a
command-decidable tasklist (the gate ledger), the PR proves it. Skill bodies
are org-neutral; organization-specific conventions load on demand from
per-skill references:

- `references/org-conventions.md` — shikanime defaults (plain-English
  commits, Automata co-author trailer, plain `gh pr` landing).
- `references/cloud-pi-native.md` — cloud-pi-native overrides (French
  artifacts, conventional commits, Release Please, console specifics).

Shared doctrine:

1. **Issue-first** — a PR always solves an issue; findings go in issue
   comments.
2. **Repo templates override the defaults.** When a repo ships
   `.github/ISSUE_TEMPLATE` or a PR template, bodies conform to its sections
   verbatim; without one the `## Problem`/`## Acceptance` (issue) and
   `## Why`/`## What`/`## References` (PR) shapes apply.
3. **Done is proven, not asserted** — every landing claim is verified against
   real command output; a red check is surfaced, never `--admin`'d past.
4. **Validate assumptions before work** — probe identity, push rights,
   toolchain, and issue existence; report `BLOCKED:` with evidence and a
   recovery path rather than silently narrowing scope.
5. **Parallelize in a graph** — `sks-async` splits multi-unit work into jj
   workspaces (fan-out), joins with multi-parent commits, lands as independent
   PRs or stacked chains.
6. **Many-to-many linkage** — link PRs with `Related:`; avoid auto-close
   keywords; close deliberately after verifying the ledger.

## What's Here

All skills follow the [Agent Skills](https://agentskills.io/specification)
specification, compatible with the
[Hermes format](https://hermes-agent.nousresearch.com/docs).

| Skill | Description |
| --- | --- |
| `sks-adversarial` | Use when probing uncertain results in a disposable sandbox — large investigation, development, debugging, testing,... |
| `sks-async` | Use when splitting multi-unit work into parallel, isolated jj workspaces (depth-tree fan-out) and landing as indepe... |
| `sks-commit` | Use when committing in shikanime-labs or shikanime-studio repos: plain-English imperative titles and repo-enforced... |
| `sks-converge` | Use when jj conflicts or divergent changes block a shikanime repo after a tree move: resolve conflicted revisions a... |
| `sks-curate` | Use when updating, improving, compressing, or token-optimizing a skill in the shikanime-labs/skills catalog: rework... |
| `sks-delegate` | Use when isolating one unit of shikanime work in a fresh jj workspace so concurrent editors / WIP never get folded... |
| `sks-dev-workflow` | Use when running the shikanime local dev loop: branching, push-to-origin, jj bookmark tracking, and landing via pla... |
| `sks-discussion` | Use when opening an RFC Discussion in a shikanime org as the pre-issue stage: converge on the problem, then derive... |
| `sks-discussion-triage` | Use when triaging an existing shikanime org discussion: category, body shape, Q&A answer, and conversion to an issue. |
| `sks-doc` | Use when documenting a shikanime project in the repo's docs/ directory after a behavior-changing PR. |
| `sks-gc` | Use when reclaiming resources leaked by shikanime jj workflows: dangling bookmarks, skill-created jj workspaces, an... |
| `sks-investigate` | Use when investigating a bug, test failure, build break, or unexpected behavior in a shikanime repo: find root caus... |
| `sks-issue` | Use when opening an issue in shikanime-labs or shikanime-studio: body is the problem statement, acceptance criteria... |
| `sks-issue-refine` | Use when iterating a problem to convergence inside its GitHub issue via research and comments before deriving the PR. |
| `sks-issue-triage` | Use when triaging an existing shikanime org issue: assign labels, assignee, milestone, and project; close with rati... |
| `sks-issue-workflow` | Use when you need the single entry point for the shikanime issue side: create, refine, and triage the issue before... |
| `sks-land` | Use when landing a shikanime org PR after reconciliation (sks-pr-resolve) and review approval gates pass; closes th... |
| `nixpkgs-pr-review` | Use when reviewing an upstream NixOS/nixpkgs pull request: build the changed packages with nixpkgs-review and check... |
| `sks-pr` | Use when opening a PR in shikanime-labs or shikanime-studio: push to origin, --head org:branch, plain-English title... |
| `sks-pr-resolve` | Use when resolving a shikanime PR's review conversations, checking the DoD ledger, and reconciling before merge (no... |
| `sks-pr-review` | Use when reviewing shikanime code: enforce YAGNI, root-cause fixes, and project conventions before approval. |
| `sks-pr-triage` | Use when triaging an existing shikanime org PR: labels, assignee, milestone, and reviewers. |
| `sks-pr-workflow` | Use when you need the single entry point for the shikanime PR side: ensure the issue exists, open, triage, and land... |
| `cpn-release-patch` | Use when backporting the commits between two release tags onto a hotfix branch in <org>/<repo>: find the patch mile... |
| `sks-restack` | Use when rebasing a shikanime jj stack onto moved main leaves conflicts: restack, then resolve each conflicted revi... |
| `sks-skill-authoring` | Use when creating a brand-new skill for the shikanime-labs/skills catalog: grounded body, evals, manifests, and shi... |
| `sks-swarm` | Use when distributing one task across a cluster of agents over A2A — route by capability need, machine resource, an... |
| `sks-update` | Use when updating skills in the shikanime-labs/skills catalog: curate every skill by default (or named ones only),... |

### Agent profiles

`profiles/<name>/` carries one Hermes profile distribution per directory
(`distribution.yaml`, `SOUL.md`, `config.yaml`, `cron/`) — the shikanime
fleet's agent personas, versioned like the skills above. Install with:

```bash
hermes profile install --name <name> --force profiles/<name>
```

Each install registers the profile with `hermes profile update` semantics:
persona, settings, and cron are distribution-owned; memories, sessions, and
credentials are never touched. Credential values are blanked in this repo —
fill them in after install.

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
