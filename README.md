# Skills

A single, strict development workflow for
[Hermes](https://hermes-agent.nousresearch.com/docs) and compatible agents.

This repo no longer ships a catalog of separate skills. It ships **one**
comprehensive skill — `dev-workflow` — that encodes the entire pipeline so the
behavior is consistent and self-contained.

## The workflow

Every feature is **drafted as a GitHub issue** to validate the task or feature
before any code is written. A **strategic documentation substrate** in
`docs/agents/` keeps maintainers, humans, and other agents on one map. The
**Ponytail laziness ladder** runs through every coding step, so the code that
ships is only what the task needs — never cutting validation, security, or
accessibility.

Two forces drive it:

- **The pipeline** (Matt Pocock's engineering skills): idea → spec → tickets →
  triage → implement → review. Nothing is built until it exists as a validated
  issue.
- **The ladder** (Ponytail): an always-on guard on any coding step — write only
  what the task needs.

## Install

```bash
# Add as a tap
hermes skills tap add shikanime-labs/skills

# Verify loaded skills
hermes skills list
```

```bash
# Or copy manually
cp -r skills/dev-workflow ~/.hermes/skills/
```

## What's inside `dev-workflow`

The skill is one `SKILL.md` with sequential phases you jump between:

| Phase        | Purpose                                               |
| ------------ | ----------------------------------------------------- |
| § Setup      | Bootstrap a repo: tracker, labels, docs layout        |
| § Spec       | Turn a discussion into a validated GitHub issue       |
| § Tickets    | Decompose a spec into tracer-bullet tickets           |
| § Triage     | Move issues through the triage state machine          |
| § Implement  | Build a ticket: TDD at the seams, on the ladder       |
| § Review     | Two-axis (Standards + Spec) review + over-engineering |
| § Debt       | Harvest `ponytail:` deferral markers into a ledger    |
| § The Ladder | The always-on simplest-solution discipline            |

## The substrate: `docs/agents/`

The pipeline reads configuration from three files instead of guessing. § Setup
writes them; day-to-day tweaks are just edits.

- `docs/agents/issue-tracker.md` — where work lives, auth, label vocabulary, how
  to create issues and blocking edges.
- `docs/agents/domain.md` — glossary (`CONTEXT.md`) + ADR layout and consumer
  rules.
- `docs/agents/workflow.md` — the pipeline, written for humans and other agents.

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
