# Agent Workflow

This catalog ships 49 skills. One of them, cpn-release-patch, serves the cloud-
pi-native org. The other 48 carry the sks- prefix and share one doctrine from
sks-context. This document maps those 48 by concern so an agent can reach the
right skill without loading the whole catalog.

## Loading levels

Content loads at three levels. Design around the levels, not around topics.

| Level | Content | When loaded | Cost |
| --- | --- | --- | --- |
| 1 | name and description | Always, at startup | ~chars/4 + 25 tokens |
| 2 | SKILL.md body | When the skill triggers | Keep under ~5k tokens |
| 3 | references/, scripts/ | On demand while executing | What is read |

Read a level-3 file only when its load condition fires. The body that points at
the file states the condition. A generic pointer does not count.

## Family map

Read the group that matches the task. Load one skill from that group, then
follow its own pointers. Every entry below carries its load condition in the
description.

### Start and loop

Open here when a task enters the family. These skills own the doctrine and the
pick-next-step decision.

- `sks-context` — Use when working in a target org's repos: the ecosystem map,
  environment facts, and shared assumptions every workflow skill builds on.
- `sks-dev` — Use when running the local dev loop in a target org's repos:
  branching in a fresh jj workspace, push-to-origin, jj bookmark tracking, and
  landing via plain gh pr merge or direct push.
- `sks-iterate` — Use when running a board-driven work loop across cards: pull
  the next card, apply the coordination ladder per card, stop on empty column,
  BLOCKED parking, or budget exhaustion.
- `sks-tldr` — Use when ending any agent work loop — investigation, dev unit,
  batch, or delegation fan-out: emit the fixed report block so status, evidence,
  and handoff stay uniform across parallel tasks.

### Converge and plan

Open here before implementation. These skills settle the problem, cut the unit
set, and track the board.

- `sks-discussion` — Use when opening an RFC Discussion in the target org as the
  pre-issue stage: converge on the problem, then derive the issue.
- `sks-discussion-triage` — Use when triaging an existing org discussion:
  category, body shape, Q&A answer, and conversion to an issue.
- `sks-plan` — Use when planning a milestone from a goal or a single unit:
  converge direction, decompose into dependency-ordered units, fill the
  milestone with triaged, boarded issues ready for sks-iterate.
- `sks-issue` — Use when opening an issue in an org repo: body is the problem
  statement, acceptance criteria as a command-decidable tasklist.
- `sks-issue-refine` — Use when iterating a problem to convergence inside its
  GitHub issue via research and comments before deriving the PR.
- `sks-issue-triage` — Use when triaging an existing org issue: assign type,
  labels, assignee, milestone, project, relationships, and fields; close with
  rationale if not workable.
- `sks-issues-sweep` — Use when sweeping GitHub issues across an org's repos:
  enumerate open issues, dedup against prior coverage, surface stale or silent
  ones, and file summary issues for systemic patterns.
- `sks-project` — Use when tracking issue/PR advancement on an org board:
  resolve the board from context or provision one, set Status to the real phase,
  audit drift.
- `sks-experiment` — Use when converting a finding or RFC outcome into a
  hypothesis-gated experiment: one experiment issue per falsifiable claim, a
  recorded verdict, confirmed outcomes handed to sks-plan.
- `sks-evolve` — Use when evolving the agent substrate without a hand-named
  target: mine experience for signals, evolve skills, profiles, memory,
  conventions, cron, or config, and repeat the fitness loop.
- `sks-design` — Use when designing or redesigning an interface — landing page,
  app screen, dashboard, deck, or report — with a taste anchor, a real component
  system, and screenshot verification.
- `sks-milestone` — Use when provisioning nixpkgs-release-aligned milestones
  across the org's Nix repos: discover the flake roster, create per-release
  milestones, assign issues and PRs, audit drift.

### Isolate and work

Open here when work needs a clean workspace. These skills own isolation, stacks,
conflicts, and cleanup.

- `sks-delegate` — Use when isolating one unit of work in a fresh jj workspace —
  the mandatory entry to implementation for every unit, so concurrent WIP never
  folds in and bookmarks/pushes stay scoped.
- `sks-async` — Use when splitting multi-unit work into parallel, isolated jj
  workspaces (depth-tree fan-out) and landing as independent plain `gh pr`
  merges.
- `sks-swarm` — Use when distributing a task across a cluster of agents over A2A
  — route by capability need, machine resource, and runner pressure, optionally
  in a disposable sks-adversarial sandbox.
- `sks-converge` — Use when jj conflicts or divergent changes block a jj repo
  after a tree move — resolve conflicted revisions and divergent twins until
  pushable.
- `sks-restack` — Use when rebasing a jj stack onto moved main leaves conflicts
  — restack, then resolve each conflicted revision with edit/resolve until
  pushable.
- `sks-split` — Use when one jj commit or in-flight stack has grown multiple
  responsibilities and must be split into parallel sibling units or a
  parent/child stack, decided per unit pair by dependency.
- `sks-gc` — Use when reclaiming resources leaked by jj-based agent workflows —
  dangling bookmarks, skill-created jj workspaces, and leftover working-copy
  dirs from sks-async/sks-dev.

### Investigate and author

Open here to find a root cause or write a change. These skills own evidence,
authoring rules, and bulk edits.

- `sks-investigate` — Use when investigating a bug, test failure, build break,
  or unexpected behavior — find root cause, form a hypothesis, and propose a
  solution, never apply the fix itself.
- `sks-adversarial` — Use when probing uncertain results in a disposable sandbox
  — large investigation, development, debugging, testing, UAT, white-room, or
  data validation before promoting a change.
- `sks-edit` — Use when a write-phase change needs authoring conventions:
  identify the matching family (TypeScript, Nix, skill authoring, sops secrets,
  Kubernetes manifests, plain English, wiki) and apply its fused rules in this
  skill.
- `sks-curate` — Use when updating, improving, compressing, or token-optimizing
  a skill or profile in a skills catalog: rework the body, tighten it, refresh
  evals, and keep it loadable.
- `sks-bulk` — Use when applying one instruction to many targets — repos,
  issues, PRs, orgs, or any enumerable agentic batch: enumerate targets, drive
  the batch from a plan file, and verify every result.
- `sks-audit` — Use when auditing fleet or org health - security alerts,
  redteam, CI failures, alerting, Flux readiness, Kubernetes events, SDLC
  efficiency: read the surface, dedup, file findings, fastlane fixes.
- `sks-maintenance` — Use when maintaining the org's repos, fleet, and runtimes:
  renovate and language dependency bumps, nixpkgs/runtime upgrades, and the
  issue → PR → land → post-merge validation loop.

### Commit, PR, and land

Open here to move a finished unit onto main. These skills own the commit, the
PR, review, and the merge gate.

- `sks-commit` — Use when committing in a target-org repo: plain-English
  imperative titles and repo-enforced hooks (gitlint, DCO) win.
- `sks-pr` — Use when opening a PR in a target-org repo: push to origin, --head
  org:branch, plain-English title, issue linkage, parity with commit.
- `sks-pr-ready` — Use when switching an org PR from draft to ready for human
  review: verify CI green on the pushed head, first review done, triage
  complete, body reconciled with the diff, then gh pr ready.
- `sks-pr-triage` — Use when triaging an existing org PR: labels, assignee,
  milestone, and reviewers.
- `sks-pr-resolve` — Use when resolving a PR's review conversations, including
  CodeRabbit review comments, checking the DoD ledger, and reconciling before
  merge (no merge itself).
- `sks-review` — Use when reviewing code, a diff, or a PR: route the org-repo
  pass (YAGNI lens, security scan, issue cross-check) or the upstream
  NixOS/nixpkgs PR review strategy.
- `sks-land` — Use when landing a target-org PR after reconciliation
  (sks-pr-resolve) and review approval gates pass; closes the linked issue
  deliberately.
- `sks-fastlane` — Use when the user designates a change as trivial and asks for
  an expedited merge: run the eligibility gate, then merge once CI is green.
- `sks-repo` — Use when creating a new org repo: apply the 5-ruleset protection
  template, bootstrap the devlib devenv scaffold, and tag v0.1.0.
- `sks-release` — Use when cutting a release of the skills catalog: verify green
  main, bump manifest versions, signed tag, published notes, RC pre-release when
  unproven.
- `sks-selfupdate` — Use when updating skills or profiles in a skills catalog:
  curate every skill by default (or named ones only), land through the dev
  workflow, and resync to local Hermes agents.
- `sks-sudo` — Use when a gh operation must run under a different org identity:
  lock, switch to the agent account, confirm the flip, restore the operator.

### Documentation and communications

Open here to write project knowledge or handle GitHub conversations. These
skills own docs, wiki, and notices.

- `sks-doc` — Use when documenting a project's technical knowledge in its
  in-repo docs/ and GitHub wiki: writing canonical docs/, enabling and indexing
  the wiki, and syncing both after a behavior-changing PR.
- `sks-comment` — Use when reading, writing, updating, or moderating comments on
  issues, PRs, or discussions: cross-surface extraction, the directed-value bar,
  the look-back loop, and update/rectification routing.
- `sks-moderate` — Use when hiding, unhiding, or moderating comments on GitHub
  issues, PRs, or discussions, or locking and unlocking conversations:
  Hide-feature classifiers and GraphQL mutations, REST conversation locks,
  verification.
- `sks-notif-sweep` — Use when sweeping unread GitHub notifications: filter
  noise, act on the answerable, mark processed threads read, never re-report a
  thread.
- `sks-triage` — Use when triaging a target org, repo, issue, or PR: sweep the
  scope for untriaged items, then assign every empty, context-derivable field —
  type, labels, assignee, fields.
- `sks-gist` — Use when a verified command, script, config, or output would be
  retyped or re-derived later — publish it as a gist for DRY reuse and link it
  from the artifact that motivated it.

## Coordination ladder

Use the smallest rung that fits the unit count and the infrastructure.

- `sks-delegate` for one unit in one fresh workspace.
- `sks-async` for N parallel units in one repo.
- `sks-swarm` for units that need different machines or capabilities.

Escalation is one way. Never spin a swarm for one unit, and never fan out before
the issue ledger is settled.

## See also

- `docs/authoring-practices.md` — the rules for authoring and compressing these
skills.
- `sks-context` — the shared doctrine and the environment probes.
