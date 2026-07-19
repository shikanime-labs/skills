# Development Workflow

The strict development workflow this catalog encodes. Every feature is drafted
as a GitHub issue to validate the task _before_ it is built; `docs/agents/`
holds the durable substrate so maintainers, humans, and other agents share one
map.

Two forces run through the whole pipeline:

- **The pipeline**: idea → spec → tickets → triage → implement → review. Nothing
  is built until it exists as a validated issue on the tracker.
- **The ladder**: an always-on minimalism guard on every coding step — write
  only what the task needs, never cut validation/security/accessibility.

## The main flow: idea → ship

1. **Sharpen the idea.** Discuss it against the codebase. Sharpen terminology
   into `CONTEXT.md`, record decisions as ADRs (`docs/agents/domain.md`).
2. **`to-spec`** — turn the conversation into a spec (Problem / Solution / User
   Stories / Implementation Decisions) and **publish it as a GitHub issue**
   labelled `ready-for-human`. This is the validation gate: no spec issue, no
   build. Set its **milestone** (the target release), assignee, project, type,
   and priority at creation — the issue body carries only relevant content.
3. **`to-tickets`** — break the spec into tracer-bullet tickets (vertical
   slices, each demoable, each sized for one context window), published as
   sub-issues with blocking edges. Each ticket inherits the meta issue's
   **milestone**, assignee, and project at creation, and sets its **parent** to
   the meta issue so the work rolls up.
4. **`triage`** — move issues through the state machine
   (`needs-triage → needs-info → ready-for-agent → ready-for-human → wontfix`).
5. **`implement`** — build a `ready-for-agent` ticket. Drive
   `test-driven development` at pre-agreed seams (feature-driven tests first),
   stay on the minimalism ladder throughout, then add **property-based stability
   tests** for the spec's invariants, close with `code-review` before
   committing.
6. **`code-review`** — three-axis review (Standards + Spec + Stability) of the
   diff against a fixed point, in parallel sub-agents.
7. **Release** — when the milestone's issues are all landed on `main`, cut the
   release (see _Release management_ below).

For a single-session change, skip 3 and go spec → implement in one context.

## Delivery: trunk-based, atomic, stacked PRs

Tickets are the unit of work; **PRs are the unit of review.** Each ticket maps
to exactly one PR so a human reviews one clear objective at a time.

### One ticket → one bookmark → one PR (trunk-based)

- Base every PR's **target on `main`** (trunk-based development): work lands
  directly to `main`, not through long-lived feature branches. A stack is a
  temporary series of PRs that each target `main` while they wait in review; the
  moment a bottom PR lands, rebase the next bookmark onto `main` and its target
  stays `main`.
- A PR's **review base** (what `gh` shows as the comparison) is the prior ticket's
  bookmark so reviewers see one logical slice: `feat/A` ← `feat/B` ← `feat/C`.
  Landing order follows the blocking graph from `to-tickets`.
- A PR is **atomic**: one objective, one logical change, the issue it closes
  linked in title/body (`Closes #N`). No scope creep, no "and also" fixes.
- Each PR carries the **milestone** (`gh pr create --milestone "vX.Y.Z"`) matching
  the ticket's issue, so the release cut finds every merged change for that
  version.
- Size for a human: small enough to review in one sitting — feature tests +
  implementation + property tests for that single ticket. If it won't fit, the
  ticket was too big; split it (back to `to-tickets`).
- Each PR carries what a reviewer needs: a one-line objective in the title, the
  linked issue, and the acceptance criteria it satisfies. The agent runs
  `code-review` (three-axis) before marking it `ready-for-human`.

### Human review gate

`main` is protected: every PR needs **one approving human review** before it
lands (squash+rebase, signed, linear). The agent's `code-review` is a
pre-flight, not the gate — a human makes the call. After the agent review
passes, the PR moves to `ready-for-human` and waits; it must not self-merge.

### Stacking mechanics (jj)

Prefer **`jj`** (Jujutsu) for all VCS operations; fall back to `git` only when
`jj` is not installed. Under `jj`, stacking is manual — one **bookmark per
ticket** based on the previous, then `gh pr create` per bookmark:

```bash
# ticket A: branch off main
jj bookmark create -r @ feat/A
# ticket B: branch off A's bookmark
jj bookmark set feat/B -r <rev-after-A>
# ... open each PR targeting main, base = prior bookmark
gh pr create --head feat/A --base main --milestone "vX.Y.Z" --title "feat(A): ..."
gh pr create --head feat/B --base main --milestone "vX.Y.Z" --title "feat(B): ..."
```

- Common mappings: `jj status` ≈ `git status`; `jj diff -r <fixed>..@` ≈
  `git diff <fixed>...HEAD`; `jj log -r <fixed>..@` ≈ `git log <fixed>..HEAD`;
  `jj commit` / `jj desc` + `jj commit` ≈ `git commit` / `--amend`;
  `jj bookmark` ≈ `git branch`.
- Land **bottom-up**: after the human approves `feat/A`, let it squash into
  `main`, then `jj rebase -d main feat/B` so `B`'s review base becomes `main`.
  Repeat up the stack. Stacks are short-lived — collapse them as soon as
  reviews pass.
- ghstack is git-only and not used under `jj`; the _Delivery_ discipline is
  identical, only the tooling differs.

## Release management

A release is the **milestone** closing out: every issue and PR in that release
shares one milestone, which is how the cut stays consistent.

### Order of operations

1. **Open the milestone** for `vX.Y.Z` (GitHub has no `gh milestone` command —
   use the REST API): `gh api repos/$OWNER/$REPO/milestones -f title="vX.Y.Z"`.
   List names with `gh api repos/$OWNER/$REPO/milestones --jq '.[].title'`.
2. **Attach the milestone at issue creation.** `to-spec` sets it on the meta
   issue; `to-tickets` inherits it on every tactical ticket. PRs inherit it via
   `gh pr create --milestone "vX.Y.Z"`.
3. **Track on the board.** Add the milestone's issues/PRs to the project board
   (`gh project item-add <number> --owner $OWNER --url <issue-url>`).
4. **Land the stack** through the human review gate (above).
5. **Cut the release.** Tag **signed** first, then ship with auto-generated
   notes:

   ```bash
   git tag -s vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z
   gh release create vX.Y.Z --repo $OWNER/$REPO \
     --title "vX.Y.Z" --generate-notes --target main
   ```

   `--generate-notes` pulls PR/commit titles since the last tag. For the first
   release there is no prior tag; pass `-F notes-file.md` instead.

### Pitfalls

- Milestone name must match exactly (the REST list is the source of truth) —
  `--milestone` fails on a typo with "milestone not found".
- `gh release create` needs the signed tag pushed first; use `--verify-tag` to
  catch a missing one.
- No `gh milestone` command exists — do not invent one; use the REST endpoint.

## Always-on: the minimalism discipline

The minimalism discipline is **not a separate step or a separate skill** — it is
the standing behaviour every coding skill in this workflow runs. The pipeline
decides _what_ to build; the ladder decides _how minimally_ to build it. Every
other skill in this catalog (`to-spec`, `to-tickets`, `triage`, `implement`,
`code-review`) invokes this discipline as part of its process.

### The ladder

On **any** coding step, stop at the first rung that holds:

1. **Does this need to exist?** (YAGNI) → no: skip it, say so in one line.
2. **Already in this codebase?** → reuse the helper/util/type/pattern that
   already lives here. Re-implementing what's a few files over is the most
   common slop.
3. **Stdlib does it?** → use it.
4. **Native platform feature?** → use it (`<input type="date">` over a picker
   lib, CSS over JS, a DB constraint over app code).
5. **Installed dependency?** → use it; never add a new one for what a few lines
   can do.
6. **Can it be one line?** → one line.
7. **Only then:** the minimum code that works.

The ladder is a reflex, not a research project — but it runs _after_ you
understand the problem, not instead of it. Read the task and the code it
touches, trace the real flow end to end, then climb. Two rungs satisfy the need
→ take the higher one and move on.

### Non-negotiable guarantees

Trust-boundary validation, data-loss handling, error handling, security, and
accessibility are **never** on the chopping block. The code ends up small
because it is necessary, not golfed. A single smoke test or `assert`-based
self-check is the minimalism minimum, not bloat — never flag it for deletion.

### Rules

- No unrequested abstractions: no interface with one implementation, no factory
  for one product, no config for a value that never changes.
- No boilerplate or scaffolding "for later"; later can scaffold for itself.
- Deletion over addition. Boring over clever — clever is what someone decodes at
  3am.
- **Bug fix = root cause, not symptom.** Before editing, grep every caller of
  the function you're about to touch. One guard in the shared function is a
  smaller diff than a guard in every caller, and patching only the named path
  leaves every sibling caller still broken.

### Deferral marker

When you deliberately take a shortcut, mark it so it can be tracked and
revisited — never silently:

```text
// deferral: <ceiling>, <upgrade trigger>
```

- `ceiling` — the limit this simplification accepts (scale, inputs, platforms).
- `upgrade trigger` — the concrete condition that means "revisit this". A marker
  with no trigger is the one that rots.

### Over-engineering audit (the minimalism audit procedure)

Before a ticket is closed, run a one-pass audit of the diff for what to delete.
One line per finding: `L<line>: <tag> <what>. <replacement>.` Tags:

- `delete:` dead code, unused flexibility, speculative feature → no replacement.
- `stdlib:` hand-rolled thing the standard library ships → name the function.
- `native:` code doing what the platform already does → name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with
  one caller → inline it.
- `shrink:` same logic, fewer lines → show the shorter form.

End the audit with the one metric that matters: `net: -<N> lines possible.`
Nothing to cut: `Lean already. Ship.`

### Deferral ledger (the deferral-ledger procedure)

Harvest every `deferral:` marker into one ledger so a deferral can't quietly
become permanent. The comment prefix keeps prose that merely mentions the
convention out of the ledger:

```bash
grep -rnE '(#|//|--|;) ?deferral:' . \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist
```

One row per marker, grouped by file:
`<file>:<line>, <what was simplified>. ceiling: <limit>. upgrade: <trigger>.`
Flag any marker naming no trigger with `no-trigger` — those are the rot risk.
End with `<N> markers, <M> with no trigger.` Nothing found: `No deferral: debt.`

These two procedures are the portable reference for any repo using this
workflow. The discipline is original to this catalog and is applied directly by
the skills above — no external plugin required.

## Inspiration

This workflow adapts ideas from two MIT-licensed sources: the spec-as-issue
engineering pipeline popularised by Matt Pocock's agent skills, and the
always-on minimalism guard from the Ponytail project
(`DietrichGebert/ponytail`). They are base inspiration only — the terms,
markers, and procedures in this catalog are intentionally renamed and rewritten.

## Setup

Run **`bootstrap`** once per repo before first use. It discovers the git remote,
existing labels, and docs layout, confirms with you, and writes
`docs/agents/{issue-tracker,domain,workflow}.md`. The pipeline skills read those
files instead of guessing.

## Router

Unsure which skill fits? **`ask`** routes over the whole catalog.

## The substrate

- `docs/agents/issue-tracker.md` — where work lives, auth, label vocabulary, how
  to create issues and blocking edges.
- `docs/agents/domain.md` — glossary + ADR layout and consumer rules.
- `docs/agents/workflow.md` — this file.
