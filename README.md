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
npx skills add shikanime-labs/skills --skill sks-dev -g

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
hermes skills install shikanime-labs/skills/sks-dev

# Or copy manually
cp -r skills/sks-dev ~/.hermes/skills/sks-dev
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

- `references/shikanime.md` — shikanime defaults (plain-English
  commits, Automata co-author trailer, plain `gh pr` landing).
- `references/cloud-pi-native.md` — cloud-pi-native overrides (French
  artifacts, conventional commits, Release Please, console specifics).

Shared doctrine:

1. **Issue-first** — a PR always solves an issue; findings go in issue
   comments.
2. **Repo templates override the defaults.** When a repo ships
   `.github/ISSUE_TEMPLATE` or a PR template, bodies conform to its sections
   verbatim; without one the `# Problem`/`## Acceptance` (issue) and
   `# Why`/`## What`/`## References` (PR) shapes apply.
3. **Done is proven, not asserted** — every landing claim is verified against
   real command output; a red check is surfaced, never `--admin`'d past.
4. **Validate assumptions before work** — probe identity, push rights,
   toolchain, and issue existence; report `BLOCKED:` with evidence and a
   recovery path rather than silently narrowing scope.
5. **Parallelize in a graph** — `sks-async` splits multi-unit work into jj
   workspaces (fan-out), joins with multi-parent commits, lands as independent
   PRs or stacked chains.
6. **Many-to-many linkage** — link PRs to issues via Development metadata
   (`addCloseIssueReferences`), never a closing keyword in the body; close
   deliberately after verifying the ledger.

## What's Here

All skills follow the [Agent Skills](https://agentskills.io/specification)
specification, compatible with the
[Hermes format](https://hermes-agent.nousresearch.com/docs).

| Skill | Description |
| --- | --- |
| `sks-adversarial` | Use when probing uncertain results in a disposable sandbox — large investigation, development, debugging, testing, UAT, white-room, or data validation before promoting a change. |
| `sks-async` | Use when splitting multi-unit work into parallel, isolated jj workspaces (depth-tree fan-out) and landing as independent plain `gh pr` merges. |
| `sks-bulk` | Use when applying one instruction to many targets — repos, issues, PRs, orgs, or any enumerable agentic batch: enumerate targets, drive the batch from a plan file, and verify every result. |
| `sks-commit` | Use when committing in a target-org repo: plain-English imperative titles and repo-enforced hooks (gitlint, DCO) win. |
| `sks-converge` | Use when jj conflicts or divergent changes block a jj repo after a tree move — resolve conflicted revisions and divergent twins until pushable. |
| `sks-curate` | Use when updating, improving, compressing, or token-optimizing a skill or profile in a skills catalog: rework the body, tighten it, refresh evals, and keep it loadable. |
| `sks-delegate` | Use when isolating one unit of work in a fresh jj workspace — the mandatory entry to implementation for every unit, so concurrent WIP never folds in and bookmarks/pushes stay scoped. |
| `sks-dev` | Use when running the local dev loop in a target org's repos: branching in a fresh jj workspace, push-to-origin, jj bookmark tracking, and landing via plain gh pr merge or direct push. |
| `sks-discussion` | Use when opening an RFC Discussion in the target org as the pre-issue stage: converge on the problem, then derive the issue. |
| `sks-discussion-triage` | Use when triaging an existing org discussion: category, body shape, Q&A answer, and conversion to an issue. |
| `sks-doc` | Use when documenting a project in the repo's docs/ directory after a behavior-changing PR. |
| `sks-evolve` | Use when evolving the agent substrate without a hand-named target: mine experience for signals, evolve skills, profiles, memory, conventions, cron, or config, and repeat the fitness loop. |
| `sks-gc` | Use when reclaiming resources leaked by jj-based agent workflows — dangling bookmarks, skill-created jj workspaces, and leftover working-copy dirs from sks-async/sks-dev. |
| `sks-gist` | Use when a verified command, script, config, or output would be retyped or re-derived later — publish it as a gist for DRY reuse and link it from the artifact that motivated it. |
| `sks-github-text-authoring` | Use when writing any GitHub text in the target org's repos — commit message, issue or PR body, discussion RFC, review or issue comment. Owns all shared prose rules; surface skills handle procedure. |
| `sks-investigate` | Use when investigating a bug, test failure, build break, or unexpected behavior — find root cause, form a hypothesis, and propose a solution, never apply the fix itself. |
| `sks-issue` | Use when opening an issue in an org repo: body is the problem statement, acceptance criteria as a command-decidable tasklist. |
| `sks-issue-refine` | Use when iterating a problem to convergence inside its GitHub issue via research and comments before deriving the PR. |
| `sks-issue-triage` | Use when triaging an existing org issue: assign type, labels, assignee, milestone, project, relationships, and fields; close with rationale if not workable. |
| `sks-issue-workflow` | Use when you need the single entry point for the issue side: create, refine, and triage the issue before any PR. |
| `sks-land` | Use when landing a target-org PR after reconciliation (sks-pr-resolve) and review approval gates pass; closes the linked issue deliberately. |
| `sks-fastlane` | Use when a hotfix, small update, or insignificant chore is too trivial for the full gate train: merge its PR without human review once CI is green. |
| `nixpkgs-pr-review` | Use when reviewing an upstream NixOS/nixpkgs pull request: build the changed packages with nixpkgs-review and check the diff against nixpkgs conventions. |
| `sks-moderate` | Use when hiding, unhiding, or moderating comments on GitHub issues, PRs, or discussions with the Hide feature: classifier choice, GraphQL mutations, verification. |
| `sks-pr` | Use when opening a PR in a target-org repo: push to origin, --head org:branch, plain-English title, issue linkage, parity with commit. |
| `sks-pr-resolve` | Use when resolving a PR's review conversations, including CodeRabbit review comments, checking the DoD ledger, and reconciling before merge (no merge itself). |
| `sks-pr-review` | Use when reviewing code in an org repo: cross-check related issues, enforce YAGNI, root-cause fixes, and project conventions before approval. |
| `sks-pr-triage` | Use when triaging an existing org PR: labels, assignee, milestone, and reviewers. |
| `sks-pr-workflow` | Use when you need the single entry point for the org PR side: ensure the issue exists, open, and triage the PR. Land separately via sks-land. |
| `sks-project` | Use when tracking issue/PR advancement on an org board: resolve the board from context or provision one, set Status to the real phase, audit drift. |
| `cpn-release-patch` | Use when backporting the commits between two release tags onto a hotfix branch in <org>/<repo>: find the patch milestone and duplicate those commits onto the tag with jj. |
| `sks-restack` | Use when rebasing a jj stack onto moved main leaves conflicts — restack, then resolve each conflicted revision with edit/resolve until pushable. |
| `sks-split` | Use when one jj commit or in-flight stack has grown multiple responsibilities and must be split into parallel sibling units or a parent/child stack, decided per unit pair by dependency. |
| `sks-kubernetes-manifests-authoring` | Use when authoring or editing Kubernetes manifests or kustomize overlays in a GitOps repo: placement, patches, generators, labels, probes, and live-cluster cross-checks. |
| `sks-nix-authoring` | Use when authoring or editing Nix in an org repo: nixfmt-sorted style, single-use let bindings, no explanatory comments, YAGNI on new options. |
| `sks-text-authoring` | Use when writing or revising technical English — docs, runbooks, commits, PR and issue bodies, error messages — under ASD-STE100 Simplified Technical English rules. |
| `sks-sops-secrets-authoring` | Use when editing sops-encrypted files: decrypt-and-edit workflow, re-encryption guards, and sops-nix secret plumbing. |
| `sks-skill-authoring` | Use when creating a brand-new skill or profile for a skills catalog: grounded body, evals, manifests, and ship through the dev workflow. |
| `sks-sudo` | Use when a gh operation must run under a different org identity: lock, switch to the agent account, confirm the flip, restore the operator. |
| `sks-swarm` | Use when distributing a task across a cluster of agents over A2A — route by capability need, machine resource, and runner pressure, optionally in a disposable sks-adversarial sandbox. |
| `sks-ts-authoring` | Use when writing or reviewing TypeScript: parse-don't-validate boundaries, cast-free explicit types, linear single-purpose functions, and schema-first inputs. |
| `sks-repo` | Use when creating a new org repo: apply the 5-ruleset protection template, bootstrap the devlib devenv scaffold, and tag v0.1.0. |
| `sks-triage` | Use when triaging a target org, repo, issue, or PR: sweep the scope for untriaged items, then assign every empty, context-derivable field — type, labels, assignee, fields. |
| `sks-update` | Use when updating skills or profiles in a skills catalog: curate every skill by default (or named ones only), land through the dev workflow, and resync to local Hermes agents. |

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
