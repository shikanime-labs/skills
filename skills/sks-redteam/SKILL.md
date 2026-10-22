---
name: sks-redteam
description:
  "Use when probing a fleet's perimeter for exposed surface: read-only checks
  of TLS posture, security headers, auth on dashboards, and anonymous API
  access, plus adversarial path exploration."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - security
      - redteam
      - perimeter
      - audit
    related_skills:
      - sks-issue
      - sks-fastlane
      - sks-adversarial
      - sks-async
      - sks-security-audit
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Perimeter Redteam

Read-only offensive probe of the perimeter reachable from the auditing host:
public endpoints and routes from the fleet manifests, TLS posture, security
headers, dashboard auth, anonymous API access, registry and GitHub attack
surface. Findings become issues; small hardening patches may fastlane. Never
exploit past proof, never modify anything.

Org-specific scope (manifests source, hosts, filing repo) live in
`references/shikanime.md`; read it when operating in a shikanime org.

## When to Use

- "Probe the perimeter" / "what's exposed" / a recurring offensive sweep.
- Validating that a hardening change landed (re-check the specific surface).
- Cross-referencing an exposure rumor from an external report.
- Chained paths to probe (a route reached only through another route, a
  pivot, a trust path) that a single-shot probe cannot cover.

## Procedure

1. **Scope the surface.** Enumerate public endpoints and TLS hostnames from a
   depth-1 clone of the fleet manifests; plus open TCP surfaces, exposed
   dashboards, container registries, and the GitHub org attack surface
   (branch protection, CI secrets exposure, webhook configs). Completion
   check: every declared public hostname has a recorded probe result.

2. **Probe read-only.** Per surface: TLS validity and cipher posture
   (`openssl s_client`), security headers (`curl -sI`), authentication bypass
   checks on dashboards, anonymous API access, registry tag listability.
   Record evidence (command, output excerpt) per finding.

3. **Explore uncertain paths in a sandbox.** Surface checks prove the
   perimeter's front door; longer attack paths — a chain from a low-trust
   endpoint to a privileged one, a pivot through a misconfigured route, a
   trust path between two services — are uncertain results, not known ones.
   Explore them as disposable trials: shape the trial per `sks-adversarial`,
   run independent paths as parallel `sks-async` workspaces (one per trial,
   dot-qualified names `<repo>.<trial>`), and record the repro command with
   each result. A trial that survives becomes a filed finding (step 6);
   read-only still holds inside the sandbox — no exploit past proof, no
   modification, no secrets. A finding whose only existence proof is a
   sandbox run stays in the report as unverified until a direct probe
   confirms it.

4. **Audit the sweep's own path.** Before filing, self-audit the surface and
   path list you just built: which declared hostnames got no probe result,
   which chained paths were assumed unreachable without a trial, which
   checks were skipped. An audit that stops at CVE feeds and the GitHub
   security advisory tab is blind, not clean — absence from those sources is
   not evidence of absence on your perimeter. Close the gap: run the missed
   probe, open the trial for the assumed-unreachable path. Log the audited
   path list with the sweep report.

5. **Dedup before filing.** Check the tracker (`gh issue list -R <repo>
   --state open`) and prior-run memory for findings already tracked or already
   proven; those are listed, never re-filed. Re-verify the top open items
   instead of rediscovering them.

6. **File new findings** via `sks-issue`: free-text title, bug label, plus
   `security` only when the repo has it. Assign per repo policy where
   eligible.

7. **Fastlane small hardening only.** Eligible scope: a header addition, a
   rate limit, or a cipher policy. Must pass the `sks-fastlane` gate in full.
   Ineligible or checks pending: leave the PR open; never wait.

8. **Memory loop.** Before reporting, honcho_reasoning "Which attack paths
   from previous probes remain unpatched?" and re-verify the top open items;
   honcho_conclude one line per durable lesson.

## Hard rules

- Read-only: never exploit past proof of the finding, never modify or delete
  anything, never touch secrets.
- Probes target the declared perimeter only — no lateral movement, no
  credential guessing, no scanning beyond the fleet's own hostnames.
- A finding whose only proof is a tool's claim gets re-verified by hand before
  filing; tool output is evidence, not a conclusion.

## Pitfalls

- A bare TLS probe returning `000` with no HTTP status on an mTLS-gated
  endpoint is the gateway WORKING — mutual TLS rejection, not an outage; do
  not file it.
- `curl -sI` (HEAD) can hide body-level leaks; when a header check passes but
  the endpoint matters, follow with a ranged GET and diff the bodies.
- Security-header findings rot fast: re-check the exact route and port before
  re-filing anything a previous run flagged, or you file stale evidence.
- Branch-protection findings read differently through rulesets — a repo whose
  classic protection endpoint 404s may still be ruleset-protected; check
  rulesets before claiming exposure.

## Verification

```bash
curl -sI https://<host>/ | head -20
gh issue list -R <repo> --state open --search "redteam:"
```

Report states: surfaces probed, findings with evidence, issues filed (links),
PRs left open, top open items re-verified.

## See also

- `sks-issue` — issue body shape for filed findings.
- `sks-fastlane` — the full eligibility gate referenced by step 7.
- `sks-adversarial` — sandbox shape for path-exploration trials (step 3).
- `sks-async` — per-trial fan-out used by step 3.
- `sks-security-audit` — the defensive counterpart: GitHub alert surfaces.
- `sks-edit` references/kubernetes-manifests/guide.md — authoring the Gateway
route patches findings point at.
