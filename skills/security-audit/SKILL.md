---
name: security-audit
description:
  "Use when auditing code for security vulnerabilities: web, API, auth,
  crypto, client-side, supply chain, cloud, availability, tenant isolation,
  or LLM targets - hunt, validate, report."
version: 0.1.0
author: Automata
license: Apache-2.0
platforms:
  - linux
  - macos
  - windows
metadata:
  hermes:
    tags:
      - security
      - audit
      - vulnerability-research
    related_skills:
      - sks-adversarial
      - sks-async
      - sks-audit
      - sks-investigate
---

# Security Auditing

Find vulnerabilities that violate a real trust boundary, then hand owners
the source evidence, safe reproduction, priority, and smallest effective
fix. Defensive and source-first: a candidate without a concrete affected
principal, resource, or security outcome is not a finding.

## When to Use

- "Security audit this codebase", "pen-test ./src", "find vulnerabilities
  in this service" — full audit mode.
- Security questions, focused reviews, vulnerability triage, validating one
  specific finding — guidance mode.
- Re-auditing a target after changes, or auditing under a bounded budget.

## Operating Modes

Guidance is the default; loading this skill authorizes no file creation and
no multi-agent run.

- **Guidance**: use the relevant parts — the candidate gate and the domain
  companions — and answer inside the current task. No output directory, no
  run files.
- **Full audit**: the user explicitly requests an audit, pen test, or
  report artifacts. Run every phase of the procedure and write the run
  files.
- An ambiguous request gets one focused question before any file is
  created.

Delegation uses the platform's subagent mechanism (for Hermes, the
`hermes-agent` skill's spawning section owns the call shapes). Every
hunter, critic, and verifier runs isolated with its own scratch directory
and returns one structured result. The agent that validates a finding is
never the agent that found it.

## Execution Safety

Source inspection is read-only. Run target-controlled builds, tests,
processes, browsers, emulators, or fuzzers only inside an OS-enforced
sandbox providing all of: no external network, with isolated loopback for
local client/server fixtures only; an empty environment populated from an
explicit allowlist; a read-only target and toolchain; writes confined to
the assigned scratch directory; explicit low CPU, memory, process,
file-size, disk, and wall-clock limits. If any control is missing, execute
nothing — record the missing capability as a `needs_validation` blocker
with a safe validation plan.

- Dummy principals, fixtures, and secrets only.
- Never probe deployed endpoints, external services, shared infrastructure,
  production identities, other users' data, or live control planes; never
  test availability against anything live or shared; never publish
  artifacts, alter releases, or spend paid quota.
- Do not install or fetch dependencies; use only tools already local.
- Stop at the minimum effect that establishes the defect. Sandbox output
  stays untrusted: promote a scratch file to a retained artifact only with
  trusted parent-side code — path-confined, size-bounded, never through a
  symlink, never an archive extraction.

## Full Audit Setup

Resolve before reconnaissance:

- **Target**: absolute repository root under review, the exact source ref,
  and whether the worktree is dirty.
- **Output directory**: new, writable, outside the target; default
  `~/security-audit/<repo>/run-<N>`. Inside the target only when the user
  insists and version control ignores the whole directory.
- **Budget**, when set: a maximum agent-invocation count across phases.

The lead agent is the only writer of the shared run files:
`architecture.md`, `coverage.md`, `findings.json`, `REPORT.md`.

## Procedure

1. **Reconnaissance.** Map the product, stack, entry points, principals
   and their authority, trust boundaries, controls, sinks, derived copies,
   and the offline build and test commands a sandbox could run. Synthesize
   `architecture.md` (about 1,000 words): principals and protected
   resources; entry surfaces and the important source-to-sink paths; each
   trust boundary with the strongest source-visible control on it; offline
   execution limits; prior-run gaps when re-auditing.
2. **Plan coverage.** Enumerate coverage units as the material combinations
   of entry surface, trust boundary, subsystem, and attack class; record
   them in `coverage.md` with a status and owner per unit. The unit list is
   the coverage claim — an agent count or an "auth was reviewed" sentence
   is not. Rank unauthenticated and low-trust entry surfaces first, then
   boundaries protecting credentials, cross-tenant data, code execution,
   and release authority.
3. **Hunt in waves.** Assign units to isolated hunters; closely related
   units in one subsystem may share a hunter, and no unit is silently
   dropped. Read `references/attack-classes.md` for the core classes, then
   the domain companion its reconnaissance evidence calls for. Each hunter
   returns, per unit: a disposition (covered, candidate, or blocked),
   reviewed paths, checks performed, candidate fingerprints, and any
   uncovered surface it found. For every candidate, name the lower-trust
   principal and its starting capability, the accepted input or action,
   the control that should reject or bind it, the exact source path after
   that decision, and the smallest observable result that settles the
   invariant either way.
4. **Check coverage after each wave.** A fresh critic agent that did not
   hunt reads `architecture.md` and the coverage plan for unmapped entry
   points, unchecked parallel paths, units closed without evidence, and
   unjustified exclusions; it proposes coverage, not findings. Stop only
   on a clean critic pass. An early stop — budget, time, scope — is
   recorded and disclosed as partial coverage, never presented as
   complete.
5. **Validate every candidate.** Give each unique fingerprint to a fresh
   verifier that did not hunt it and whose job is to refute it: re-read
   every cited location, reconstruct the strongest source-visible
   controls, and independently reproduce the minimum observed result when
   possible. It returns `confirmed`, `needs_validation`, or `rejected`
   with a corrected record. Apply a correction that strengthens the
   verdict or changes the root cause only after another fresh verifier
   accepts it.
6. **Report.** Write `findings.json` — one final record per fingerprint,
   sorted — then derive `REPORT.md` from the records: run scope and source
   ref; a posture summary; confirmed findings with reproduction, impact,
   priority rationale, and the smallest source fix; needs-validation leads
   with exact blockers and safe next steps; hardening notes; the coverage
   statement. Prose never contradicts the records, and rejected candidates
   are never findings. Read `references/validation-reporting.md` before
   phases 5 and 6.

Do not end a full audit before either every record passes validation and
the report is written, or the run is recorded incomplete with its exact
reason and the gap disclosed in the report.

## Candidate Gate

1. A candidate needs a complete repository-relative source trace and
   evidence for the claimed root cause, including the strongest
   source-visible control on the path.
2. `confirmed` requires a bounded local observed result, meaningful impact
   across a stated boundary, complete conditions, and no visible
   preventing layer.
3. Never strengthen a crash into code execution, ordinary work into shared
   availability, or a same-principal action into privilege gain.
4. A fact outside source and the sandbox — deployment, proxy, provider,
   identity, browser behavior — makes the candidate `needs_validation`
   with the exact missing fact and a safe owner-observed or local check.
   No severity, no speculative completion.
5. A missing best practice with no affected principal or resource is
   hardening, not a finding. A candidate disproved by source is
   `rejected`, not `needs_validation`.
6. One source-derived root cause, one fingerprint, in every state;
   related but independent missing controls take separate fingerprints.
7. An empty candidate list is a valid result when nothing survives.

## Verdict Contracts

Only `confirmed` carries severity. The contracts are disjoint:

- `confirmed` requires `root_cause`, `intended_behavior`, an ordered trace
  (`entrypoint`, then `propagation`, ending at `sink`), `evidence`,
  `conditions`, a target-neutral `execution` with a factual
  `observed_result`, `remediation`, `severity`, and `confidence`. It
  forbids `blockers`, `validation_plan`, and `reason`.
- `needs_validation` requires `claimed_root_cause`, a trace, `evidence`,
  nonempty `blockers`, and a `validation_plan` with a bounded local step
  or an owner-observed deployment check. It forbids severity, `execution`,
  `remediation`, and a confirmed `root_cause`.
- `rejected` requires `claimed_root_cause`, a trace, `evidence`, and
  `reason`. It forbids severity, `execution`, `remediation`, `blockers`,
  and `validation_plan`.

`execution` describes the target's native interface — HTTP input, CLI
call, library call, message, fixture, browser action, or rendered policy —
never a live-probe instruction.

Severity requires demonstrated impact:

- **critical** — unauthenticated code execution, full data-store access,
  or takeover of arbitrary accounts.
- **high** — full defeat of an explicit control with real consequences:
  authentication bypass, cross-tenant read or write, stored script
  execution affecting other users, authenticated code execution.
- **medium** — a real boundary violation with limited blast radius,
  uncommon preconditions, or a narrow resource set.
- **low** — disclosure of non-secret internals, or sustained effort for
  minimal gain.
- **informational** — confirmed but minimal; useful mainly as a
  prerequisite inside a larger finding.

The high/medium discriminator: does the demonstrated result fully defeat
an explicit control for an action with real consequences, or only weaken
it? Overall severity never exceeds demonstrated impact.

## Remediation

For each confirmed finding, name the invariant the code must enforce and
the narrowest source change that enforces it at the last trusted decision
point, with a regression case. The audit describes fixes; it never modifies
target source.

## Prior Runs and Budget

A re-audit is additive. Read prior findings first: carry a prior
`confirmed` record forward only when its relevant source is unchanged, and
send it through fresh verification anyway; changed source, and every prior
`needs_validation`, deferred, or out-of-scope item, is current work; a
prior `rejected` suppresses only its exact claim, never coverage of its
unit. State in the report when no prior run exists — one run never
exhausts a target.

A budget bounds agent invocations across all phases. Reserve validation
first (about two verifiers per expected candidate, or 30 percent of the
balance when unsure) plus one critic call per planned wave; hunt with the
remainder in priority order. When the reserves cannot hold, defer units
with the reason recorded instead of thinning evidence. An unvalidated
candidate stays a coverage candidate listed in the report as incomplete —
never a finding.

## Domain Companions

Read `references/attack-classes.md` in every audit; it carries the core
classes and this routing, by the boundary reconnaissance actually found:

| Target surface | Companion |
| --- | --- |
| Memory-unsafe or privileged native code | `references/memory-safety-binary.md` |
| LLM, agent, RAG, or MCP trust decisions | `references/ai-llm.md` |
| HTTP framing, cache, sessions, identity | `references/web-protocol-auth.md` |
| Browser, extension, service worker | `references/client-side.md` |
| Dependencies, CI, release, plugins | `references/supply-chain-release.md` |
| IAM, IaC, containers, ingress | `references/cloud-deployment.md` |
| RPC, queues, webhooks, serialization | `references/protocols-rpc-messaging.md` |
| Untrusted work on shared resources | `references/resource-exhaustion.md` |
| Multi-tenant stores, export, deletion | `references/data-isolation.md` |
| Desktop, mobile, webview, local IPC | `references/desktop-local-ipc.md` |

Select a companion because reconnaissance found the trust-sensitive
boundary its opening section describes, never because a language or
dependency name appears.

## Pitfalls

- Checklist deviations reported as vulnerabilities.
- Defense-in-depth advice with no reachable boundary violation.
- Live or shared-environment testing where bounded local evidence
  suffices.
- Guessing provider, proxy, browser, identity, or deployment behavior
  that source cannot establish.
- Treating intended same-principal authority or self-impact as a
  cross-boundary result.
- Reporting an effect stronger than observed.
- Prose-only hunter results that cannot be deduplicated or verified.
- Severity on a `needs_validation` record.
- Writing the report before independent verification, or letting prose
  disagree with the records.

## Verification

```bash
python3 -m json.tool <output-dir>/findings.json > /dev/null  # parses
grep -c "severity" <output-dir>/findings.json                # confirmed only
grep -l "source ref" <output-dir>/REPORT.md                  # scope stated
```

Every trace and evidence path in `findings.json` must exist in the target
at the audited ref; every deferred unit appears in `REPORT.md`.

## See also

- `sks-audit` — fleet and org security surface sweeps; this skill audits
  source code.
- `sks-adversarial` — the disposable sandbox bounded local evidence runs
  in.
- `sks-async` — parallel fan-out for large audits.
- `sks-investigate` — single-bug root cause when one defect is already
  known.
