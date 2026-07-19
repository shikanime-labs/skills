# Skills

A curated catalog of self-improved agent skills for
[Hermes](https://hermes-agent.nousresearch.com/docs) and compatible agents.

This catalog encodes **one strict development workflow**: a spec-as-issue
pipeline where every feature is drafted as a GitHub issue to validate it before
code exists, combined with an always-on minimalism discipline (write only what
the task needs) woven through every coding step rather than split into separate
skills. `docs/agents/` holds the durable substrate so maintainers, humans, and
other agents share one map; features ship behind feature-driven tests and
property-based stability tests.

See `docs/agents/workflow.md` for the **Inspiration** note crediting the two
MIT-licensed sources this workflow adapts.

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
npx skills add shikanime-labs/skills --skill implement -g

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
hermes skills install shikanime-labs/skills/workflow/implement

# Or copy manually
cp -r skills/workflow/implement ~/.hermes/skills/workflow/
```

### Install via npm

```bash
# Install as an npm package (skills are bundled via the agents field)
npm install @shikanime-labs/skills

# Then export to your agent's skill directory
npx agents export --target claude
```

The `agents` field in `package.json` and the `skills.json` manifest at the repo
root enable discovery by npm-based skill managers. Both now list only the 7
workflow skills; the minimalism discipline is part of the workflow, not a
separate entry.

## The Workflow

A single narrative, not a toolbox. Read `docs/agents/workflow.md` for the full
flow; in short:

1. **`bootstrap`** — run once per repo; writes `docs/agents/*`.
2. **`to-spec`** — turn a discussion into a spec and publish it as a GitHub
   issue (the validation gate). Also keeps `docs/agents/` current.
3. **`to-tickets`** — split a spec into tracer-bullet tickets with blocking
   edges.
4. **`triage`** — move issues through the state machine.
5. **`implement`** — load context for a task (read spec/ticket, explore
   codebase, present task context). The user controls implementation.
6. **User implements** — the user writes code, tests it, and prepares the PR.
7. **`code-review`** — Standards + Spec (+ Stability) review.
8. **`ask`** — router over the catalog.

Each ticket ships as **one atomic PR** through a required human review gate —
the agent's `code-review` is a pre-flight, a human approves the merge. See
`docs/agents/workflow.md` → _Delivery: atomic stacked PRs_.

**The minimalism discipline is not a skill — it is the always-on discipline
woven through every coding step.** The ladder (YAGNI → reuse → stdlib → native →
dep → one line → minimum), the non-negotiable guarantees (validation, error
handling, security, accessibility), the `deferral:` marker, the over-engineering
audit, and the deferral ledger all live in `docs/agents/workflow.md` and are
applied by the user during implementation.

## What's Here

All skills live under `skills/workflow/` and follow the
[Agent Skills](https://agentskills.io/specification) specification, compatible
with the [Hermes format](https://hermes-agent.nousresearch.com/docs).

| Skill         | Description                                                                                                      |
| ------------- | ---------------------------------------------------------------------------------------------------------------- |
| `bootstrap`   | Bootstrap a repo: write `docs/agents/*`                                                                          |
| `to-spec`     | Discussion → spec issue (validation gate) + docs update                                                          |
| `to-tickets`  | Spec → tracer-bullet tickets with blocking edges                                                                 |
| `triage`      | Issue state machine: categorise, brief, transition                                                               |
| `implement`   | Load context for a task: read spec/ticket, explore codebase, present task context. User controls implementation. |
| `code-review` | Three-axis (Standards + Spec + Stability) review                                                                 |
| `ask`         | Router over the workflow catalog                                                                                 |

**Minimalism discipline** (ladder, non-negotiable guarantees, `deferral:`
marker, over-engineering audit, deferral ledger) is defined once in
`docs/agents/workflow.md` and applied by the user during implementation — it is
not a separate skill.

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
