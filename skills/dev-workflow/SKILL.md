---
name: dev-workflow
description:
  "The strict development workflow: one skill covering setup, spec-as-issue
  (validation gate), ticket decomposition, triage, implementation, and review —
  with the always-on Ponytail laziness ladder running through every coding step.
  Adapted from mattpocock/skills and DietrichGebert/ponytail."
version: 2.0.0
author:
  Operator 21O (merged from mattpocock/skills and DietrichGebert/ponytail, MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags:
      [
        workflow,
        spec,
        tickets,
        triage,
        implementation,
        review,
        ponytail,
        laziness,
        yagni,
      ]
    related_skills: []
---

<!-- markdownlint-disable MD013 MD033 -->

# Dev Workflow

One skill. The whole strict development workflow.

Every feature is **drafted as a GitHub issue** to validate the task or feature
before any code is written. A **strategic documentation substrate** in
`docs/agents/` keeps maintainers, humans, and other agents on one map. And the
**Ponytail laziness ladder** runs through every coding step, so the code that
ships is only what the task needs — never cutting validation, security, or
accessibility.

Two forces drive this:

- **The pipeline** (Matt Pocock's engineering skills): idea → spec → tickets →
  triage → implement → review. Nothing is built until it exists as a validated
  issue.
- **The ladder** (Ponytail): an always-on guard on any coding step — write only
  what the task needs.

## How to use this skill

This is a long skill. Read the **whole** thing once, then jump to the section
for the phase you are in. The phases are sequential but you may enter at any
point (e.g. a `ready-for-agent` ticket already exists → go to § Implement).

| You want to...                              | Go to                       |
| ------------------------------------------- | --------------------------- |
| Set up a repo for the first time            | § Setup                     |
| Turn a discussion into a validated feature  | § Spec                      |
| Break a spec into buildable tickets         | § Tickets                   |
| Sort / label / brief issues                 | § Triage                    |
| Build a spec or ticket                      | § Implement                 |
| Review a branch/PR (Standards + Spec)       | § Review                    |
| Find what to delete / is it over-engineered | § Review → over-engineering |
| See the shortcuts we deferred               | § Debt                      |
| Simplest-solution discipline on any coding  | § The Ladder (always on)    |

## The substrate: `docs/agents/`

The pipeline reads configuration from three files instead of guessing.
`dev-workflow` § Setup writes them; day-to-day tweaks are just edits.

- `docs/agents/issue-tracker.md` — where work lives, auth, label vocabulary, how
  to create issues and blocking edges.
- `docs/agents/domain.md` — glossary (`CONTEXT.md`) + ADR layout and consumer
  rules.
- `docs/agents/workflow.md` — this pipeline, written for humans and other
  agents.

If `docs/agents/issue-tracker.md` is missing, run § Setup first.

---

## § Setup (run once per repo)

Teach this repo where issues live, what the triage labels are called, and where
the domain docs sit — and record those answers as the `docs/agents/` files the
rest of the pipeline reads.

Prompt-driven, not a deterministic script: explore, present what you found,
confirm with the user, then write. Never guess where guessing can be replaced by
looking.

### 1. Explore

Read what already exists; don't assume:

- `git remote -v` — is this a GitHub repo? Which owner/repo?
- `AGENTS.md` / `CLAUDE.md` at root — does either exist? Is there an
  `## Agent skills` section?
- `CONTEXT.md`, `CONTEXT-MAP.md` at root.
- `docs/adr/` and any `src/*/docs/adr/`.
- `docs/agents/` — did a prior run already write these?
- Existing issue labels (`gh label list`, or the GitHub MCP) — so triage maps
  onto real labels instead of creating duplicates.
- Monorepo signals (`pnpm-workspace.yaml`, `workspaces` in `package.json`,
  populated `packages/*`) — decides single- vs multi-context docs.

### 2. Present findings and ask

Summarise what's present and missing. Take the three decisions in order, each
led by a recommended answer the user can accept in a word. Skip any the
exploration already settled.

**A — Issue tracker.** Where work is tracked. Default: GitHub Issues on
`origin`. Alternatives: GitLab, local markdown under `.scratch/`, or a workflow
the user describes. Propose the one matching the git remote.

**B — Triage labels.** Keep the default canonical labels (`bug`, `enhancement`,
`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`)?
Say no only if the tracker already uses other strings — then map onto those.

**C — Domain docs layout.** Assume single-context (one `CONTEXT.md` +
`docs/adr/` at root) unless monorepo signals appeared, in which case propose a
`CONTEXT-MAP.md`.

### 3. Write

Write `docs/agents/issue-tracker.md`, `docs/agents/domain.md`, and
`docs/agents/workflow.md` from the confirmed answers, and add an
`## Agent skills` block pointing at them in whichever of `CLAUDE.md` /
`AGENTS.md` the repo already uses.

**It's working if:** `docs/agents/issue-tracker.md` and `domain.md` land (plus
`workflow.md`), an `## Agent skills` section appears in `CLAUDE.md` or
`AGENTS.md`, the proposed tracker matches the real git remote, and the labels
match strings that already exist.

Re-run only to switch trackers or start over.

---

## § Spec (the validation gate)

Turn the current conversation into a **spec** (a PRD) and **publish it as a
GitHub issue**. A feature exists as a reviewed spec issue before any code is
written.

Do **not** interview the user — synthesize what you already discussed. The issue
tracker and label vocabulary come from `docs/agents/issue-tracker.md`. Use the
glossary in `docs/agents/domain.md` throughout, and respect ADRs in the area you
touch.

### Process

1. **Explore the repo** to understand current state if you haven't already.
2. **Sketch the seams** at which you'll test the feature. Prefer existing seams
   to new ones; use the highest seam possible; fewer is better (ideal: one).
   Confirm the seams match the user's expectations.
3. **Write the spec** using the template, then publish it as an issue and apply
   the `ready-for-agent` label (no further triage needed).

<spec-template>

## Problem Statement

The problem the user faces, from the user's perspective.

## Solution

The solution, from the user's perspective.

## User Stories

A long, numbered list, each:
`As an <actor>, I want <feature>, so that <benefit>`. Cover all aspects of the
feature — be extensive.

## Implementation Decisions

Modules built/modified, their interfaces, technical clarifications,
architectural decisions, schema changes, API contracts, specific interactions.
Do NOT include file paths or code snippets (they go stale fast) — the exception
is a snippet from a prototype that encodes a decision more precisely than prose.

</spec-template>

### Publishing

Create the issue via the GitHub MCP (`GitHub_issue_write`) or `gh issue create`,
per `docs/agents/issue-tracker.md`. Title it in the domain's vocabulary. Hand
back the issue URL.

**Boundaries:** produces one spec issue. Does not break it into tickets (that's
§ Tickets) and does not implement it (that's § Implement).

---

## § Tickets (decomposition)

Break a plan, spec, or the current conversation into a set of **tickets** —
tracer-bullet vertical slices, each declaring the tickets that **block** it —
and publish them to the tracker.

The tracker and label vocabulary come from `docs/agents/issue-tracker.md`.
Titles and bodies use the glossary in `docs/agents/domain.md`.

### Process

1. **Gather context.** Work from the conversation. If the user passes a
   reference (spec path, issue number/URL), fetch its full body and comments.
2. **Explore the codebase (optional).** If not already done, explore to
   understand current state. Look for **prefactoring** opportunities: "make the
   change easy, then make the easy change."
3. **Draft vertical slices.**

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API,
  UI, tests) — vertical, NOT a horizontal slice of one layer.
- A completed slice is demoable or verifiable on its own.
- Each slice fits in a single fresh context window.
- Any prefactoring is done first.

</vertical-slice-rules>

Give each ticket its **blocking edges** — the tickets that must complete before
it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception.** A mechanical change whose blast radius
fans across the whole codebase can't be a single tracer bullet. Sequence it
**expand–contract**: first expand (add the new form beside the old so nothing
breaks), then migrate call sites in batches sized by blast radius (per package /
directory), each batch a ticket blocked by the expand, keeping CI green; a final
contract ticket removes the old form once all batches land.

4. **Publish.** Create one issue per ticket via the GitHub MCP
   (`GitHub_issue_write`, `GitHub_sub_issue_write`) or `gh`. Model blocking
   edges as native sub-issues, or a `Blocked by: #N` line in the body. Apply the
   `ready-for-agent` label to tickets with no unresolved blockers. Hand back the
   ticket URLs and the blocking graph.

**Boundaries:** produces tickets and their edges. Does not implement them
(that's § Implement).

---

## § Triage (state machine)

Move issues on the tracker through a small state machine of triage roles. A PR
is an issue with attached code — same roles, same states, same machine.

The tracker and label vocabulary come from `docs/agents/issue-tracker.md`.

Every comment or issue an agent posts during triage **must** start with:

```text
> *This was generated by AI during triage.*
```

### Roles

Two **category** roles: `bug` (something is broken), `enhancement` (new feature
or improvement).

Five **state** roles:

- `needs-triage` — maintainer must evaluate
- `needs-info` — waiting on reporter
- `ready-for-agent` — fully specified, an AFK agent can take it
- `ready-for-human` — needs a human
- `wontfix` — will not be actioned

Every triaged issue carries exactly one category role and one state role. If
state roles conflict, flag it and ask the maintainer before doing anything.

These are canonical names; the actual label strings live in
`docs/agents/issue-tracker.md`.

### State transitions

An unlabeled issue → `needs-triage` → one of `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`. `needs-info` returns to `needs-triage` once the
reporter replies. The maintainer can override at any time — flag unusual
transitions and ask before proceeding.

### Invocation

The maintainer describes what they want in natural language ("show me anything
that needs my input", "triage #42", "is this ready for an agent?"). Interpret
and act.

### Agent-ready briefs

When moving an issue to `ready-for-agent`, attach a brief an AFK agent can act
on cold: the goal in the domain's vocabulary, the seams to test at, the files
likely in scope, and the acceptance criteria. A brief that assumes conversation
context is not ready.

**Boundaries:** categorises and transitions issues; writes briefs. Does not
implement.

---

## § Implement (build)

Build the work described by a spec or ticket. This is the execution end of the
pipeline: the feature was validated as an issue by § Spec / § Tickets; now it
gets built under discipline.

Read `docs/agents/domain.md` for vocabulary and respect the ADRs in the area you
touch. Fetch the originating issue per `docs/agents/issue-tracker.md`.

### Process

1. **Understand first.** Read the spec/ticket and the code the change touches.
   Trace the real flow end to end before writing anything.
2. **Stay lazy — the Ponytail ladder (§ The Ladder).** Stop at the first rung
   that holds. Lazy about the solution, never about reading — and never cut
   validation, error handling, security, or accessibility.
3. **Drive test-driven development** at the pre-agreed seams — one red-green
   slice at a time. Prefer the highest, fewest seams. Write the failing test
   first; watch it fail for the right reason; make it pass minimally; refactor
   on the green.
4. **Verify continuously.** Run typechecking and single test files regularly;
   run the full suite once at the end.
5. **Close with § Review** — the two-axis (Standards + Spec) review of the diff
   — before committing.
6. **Commit** to the current branch, referencing the issue (`Closes #N`).

### Bug fixes

A ticket names a symptom. Before editing, find every caller of the function
you're about to touch and fix the **root cause** where all callers route through
— one guard in the shared function, not one in every caller. Patching only the
path the ticket names leaves every sibling caller still broken.

**Boundaries:** builds one spec/ticket. Sized to a single context window — if it
doesn't fit, it should have been split by § Tickets. Does not decompose work
itself.

---

## § Review (two-axis)

Two-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards** — does the code conform to this repo's documented coding
  standards?
- **Spec** — does the code faithfully implement the originating issue / PRD /
  spec?

Both axes run as **parallel sub-agents** (`delegate_task`) so they don't pollute
each other's context; this skill aggregates their findings side by side. The
issue tracker comes from `docs/agents/issue-tracker.md`.

### Process

1. **Pin the fixed point.** Whatever the user said — a commit SHA, branch, tag,
   `main`, `HEAD~5`. If unspecified, ask. Capture once:
   `git diff <fixed-point>...HEAD` (three-dot, against the merge-base) and
   `git log <fixed-point>..HEAD --oneline`. Confirm the ref resolves
   (`git rev-parse`) and the diff is non-empty before spawning sub-agents — a
   bad ref or empty diff fails here, not inside two children.
2. **Identify the spec source.** In order: issue references in commit messages
   (`#123`, `Closes #45`) fetched per `docs/agents/issue-tracker.md`; a path the
   user passed; a spec under `docs/`, `specs/`, or `.scratch/` matching the
   branch. If none, ask; if the user says there isn't one, the Spec sub-agent
   reports "no spec available".
3. **Identify the standards sources.** `CODING_STANDARDS.md`, `CONTRIBUTING.md`,
   `AGENTS.md`, `.cursorrules`, etc. On top of whatever the repo documents, the
   Standards axis always carries a **smell baseline** — Fowler's code smells
   (long method, large class, feature envy, primitive obsession, shotgun
   surgery, ...) — so review has teeth even when the repo documents nothing.
4. **Run both axes in parallel.** Spawn two sub-agents with `delegate_task`:
   - **Standards agent** — the diff + the standards sources + smell baseline.
   - **Spec agent** — the diff + the spec. Reports each user story / acceptance
     criterion as met / partial / missing.
5. **Aggregate.** Report the two axes side by side. Per finding: location
   (`path:line`), the issue, and the fix. End with a verdict per axis (pass /
   changes requested) and the single most important change.

**Boundaries:** reviews; does not apply fixes.

### Over-engineering pass (the Ponytail lens)

Review diffs for unnecessary complexity. One line per finding: location, what to
cut, what replaces it. The diff's best outcome is getting shorter. This is a
focused sub-mode of the Standards axis — run it when the user asks "what can we
delete" or "is this over-engineered".

Format: `L<line>: <tag> <what>. <replacement>.`, or `<file>:L<line>: ...` for
multi-file diffs.

Tags:

- `delete:` dead code, unused flexibility, speculative feature. Replacement:
  nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the
  feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with
  one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.

End with the only metric that matters: `net: -<N> lines possible.` Nothing to
cut: `Lean already. Ship.`

A single smoke test or `assert`-based self-check is the Ponytail minimum, not
bloat — never flag it for deletion.

---

## § Debt (deferral ledger)

Every deliberate Ponytail shortcut is marked with a `ponytail:` comment naming
its ceiling and upgrade path (see § The Ladder). This collects them into one
ledger so a deferral can't quietly become permanent.

The marker convention (from § The Ladder) is:

```text
// ponytail: <ceiling>, <upgrade trigger>
```

### Scan

Grep the repo for the marker, skipping `node_modules`, `.git`, and build output.
The comment prefix keeps prose that merely mentions the convention out of the
ledger:

```bash
grep -rnE '(#|//|--|;) ?ponytail:' . \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist
```

Add other comment prefixes if your stack uses them. Each hit is one ledger row.

### Output

One row per marker, grouped by file:

`<file>:<line>, <what was simplified>. ceiling: <the limit named>. upgrade: <the trigger to revisit>.`

Pull the ceiling and trigger straight from the comment. Want an owner per row?
add `git blame -L<line>,<line>`.

Flag the rot risk: any `ponytail:` comment naming no upgrade path or trigger
gets a `no-trigger` tag — those are the ones that silently rot.

End with `<N> markers, <M> with no trigger.` Nothing found:
`No ponytail: debt. Clean ledger.`

**Boundaries:** reads and reports only; changes nothing. To persist it, ask and
write the ledger to `PONYTAIL-DEBT.md`. One-shot.

---

## § The Ladder (always on)

You are a lazy senior developer. Lazy means efficient, not careless. You have
seen every over-engineered codebase and been paged at 3am for one. The best code
is the code never written.

**ACTIVE EVERY RESPONSE** on any coding task. No drift back to over-building.
Still active if unsure. Off only on "stop ponytail" / "normal mode". Default
intensity: **full** (`lite` | `full` | `ultra`).

### The ladder

Stop at the first rung that holds:

1. **Does this need to exist at all?** Speculative need = skip it, say so in one
   line. (YAGNI)
2. **Already in this codebase?** A helper, util, type, or pattern that already
   lives here → reuse it. Look before you write; re-implementing what's a few
   files over is the most common slop.
3. **Stdlib does it?** Use it.
4. **Native platform feature covers it?** `<input type="date">` over a picker
   lib, CSS over JS, DB constraint over app code.
5. **Already-installed dependency solves it?** Use it. Never add a new one for
   what a few lines can do.
6. **Can it be one line?** One line.
7. **Only then:** the minimum code that works.

The ladder is a reflex, not a research project — but it runs _after_ you
understand the problem, not instead of it. Read the task and the code it touches
first, trace the real flow end to end, then climb. Two rungs work → take the
higher one and move on.

**Bug fix = root cause, not symptom.** Before you edit, grep every caller of the
function you're about to touch. One guard in the shared function is a smaller
diff than a guard in every caller — and patching only the path the ticket names
leaves every sibling caller still broken.

### Rules

- No unrequested abstractions: no interface with one implementation, no factory
  for one product, no config for a value that never changes.
- No boilerplate, no scaffolding "for later"; later can scaffold for itself.
- Deletion over addition. Boring over clever — clever is what someone decodes at
  3am.

### Never lazy about

Trust-boundary validation, data-loss handling, security, and accessibility are
**never** on the chopping block. The code ends up small because it's necessary,
not golfed.

### Deferral marker

When you deliberately take a shortcut, mark it so it can be tracked:
`// ponytail: <ceiling>, <upgrade trigger>`. § Debt harvests these.

---

## The full pipeline at a glance

1. **Sharpen the idea.** Discuss it against the codebase. Sharpen terminology
   into `CONTEXT.md`, record decisions as ADRs (`docs/agents/domain.md`).
2. **§ Spec** — turn the conversation into a spec and **publish it as a GitHub
   issue** labelled `ready-for-agent`. No spec issue, no build.
3. **§ Tickets** — break the spec into tracer-bullet tickets with blocking
   edges, published as sub-issues.
4. **§ Triage** — move issues through the state machine.
5. **§ Implement** — build a `ready-for-agent` ticket. TDD at the seams, on the
   ladder, close with § Review, then commit.
6. **§ Review** — two-axis review (Standards + Spec) of the diff.

For a single-session change, skip 3 and go spec → implement in one context.
