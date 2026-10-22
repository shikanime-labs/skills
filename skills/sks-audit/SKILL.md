---
name: sks-audit
description:
  "Use when auditing fleet or org health — GitHub security alerts, perimeter
  redteam, CI failures, alerting, Flux readiness, Kubernetes events: read the
  surface, dedup, file new findings as issues, fastlane small fixes."
version: 1.0.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - audit
      - triage
      - security
      - github
      - kubernetes
      - flux
      - monitoring
    related_skills:
      - sks-issue
      - sks-fastlane
      - sks-adversarial
      - sks-renovate-sweep
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Audit

Read a fleet or org surface, dedup against the filing repo, file uncovered
findings as issues, and fastlane small fixes. Read-only posture: an audit
never closes, dismisses, silences, acks, or re-triggers anything — resolution
is an operator decision.

Org targets (orgs in scope, filing repos, cluster context, endpoints) live in
`references/shikanime.md`; read it before the first sweep and when a target
moved.

## Procedure

1. **Pick the surface section** below and read its org targets. When a read
   returns something unexpected — a new failing class, state that contradicts
   the last sweep — deepen the discovery before trusting it: probe further in
   a disposable sandbox per `sks-adversarial` (promote findings, never the
   sandbox).

2. **Read the source** with the surface's command. Record the fields listed;
   every section names its completion check. A quiet read is not a clean
   surface — each section lists its cross-check before reporting healthy.

3. **Noise-filter conservatively.** Drop a class only when its section says
   so, and record the drop with its reason; an unexplained drop is a finding.
   Crashloops, probe failures, evictions, secret-scanning alerts, and
   cluster-level failures keep their item no matter how routine they look.

4. **Dedup against the filing repo.** `gh issue list -R <repo> --state open`;
   match on object identity (repo+alert, object+reason, namespace/name),
   never on message text — flapping sources re-file every sweep otherwise.
   Tracked findings are listed in the report, never re-filed.

5. **File each new finding** via `sks-issue`: free-text title, bug label,
   plus `security` only when the repo has it. Assign per repo policy where
   eligible. One issue per stable object (repo+workflow, object+reason),
   updated by later runs — never one issue per occurrence.

6. **Fastlane small fixes.** Scope per surface (dependency bump, CI yaml,
   action pin, values bump, threshold, image pin, probe timing, small
   one-overlay manifest patch). Must pass the `sks-fastlane` gate in full.
   Ineligible or checks pending: leave the PR open; never wait.

7. **Note resolutions.** Findings resolved since the last sweep are listed;
   the audit closes nothing automatically.

8. **Memory loop.** Before reporting: honcho_search this audit's topic and
   honcho_context for recurring context (findings that recur, remediations
   already in flight, known flappers); re-verify the top open items instead
   of rediscovering them. After reporting: honcho_conclude one line per
   durable lesson.

## Surfaces

### GitHub security alerts

`gh api /orgs/<org>/code-scanning/alerts --paginate` — same for
`/secret-scanning/alerts` and `/dependabot/alerts`, per org in scope. Keep
`state==\"open\"`; record alert type, repo, severity, CVE or rule id,
html_url, created_at. Rank critical and high first; secret-scanning alerts
are always urgent; dependabot ranks by manifest reachability when evidenced.
Completion check: every org × alert-type pair enumerated. Cross-check
redteam findings before filing; already-proven findings are referenced, not
re-filed.

### Perimeter redteam

Depth-1 clone of the fleet manifests for public endpoints, Envoy Gateway
routes, TLS hostnames; plus open TCP surfaces, exposed dashboards, container
registries, and the GitHub attack surface (branch protection, CI secrets,
webhooks). Probe read-only: `openssl s_client` for TLS posture, `curl -sI`
for headers, auth-bypass checks, anonymous API access, registry tag
listability. Record command + output excerpt per finding; a finding whose
only proof is a tool's claim is re-verified by hand before filing.
Completion check: every declared public hostname has a probe result.

### CI failures

`gh repo list <org> --limit 100 --json nameWithOwner` per org, then per repo
`gh run list -R <repo> --status failure --created \">$(date -d '-24 hours'
'+%Y-%m-%d')\"`. Drop renovate PR checks (owned by `sks-renovate-sweep`),
draft-PR CI skips, and flakes that passed on rerun. Record run URL, failing
job, first error lines (`gh run view <run> --log-failed`), head sha.
Completion check: every repo scanned, every in-window failure recorded. A
scheduled failure with zero code changes is an infra finding, not a code bug.

### Alertmanager alerts

`curl -s <alertmanager>/api/v2/alerts`, parse with python3; record alertname,
labels, annotations, startsAt. Filter on `status.state == \"active\"` — the
API also returns recently-resolved alerts. Completion check: every active
alert has a recorded line. Grafana's HTTP API is a different surface; when it
is OIDC-only with no API-key path, read the vm* APIs instead, never scrape
dashboards.

### Flux readiness

`kubectl get kustomizations.kustomize.toolkit.fluxcd.io -A -o json` and
`kubectl get helmreleases.helm.toolkit.fluxcd.io -A -o json`; list every
object whose Ready condition is False with message and source revision.
Suspended objects are reported separately, never counted as failures, never
resumed or annotated. Completion check: every Ready=False object has a
recorded line.

### Kubernetes warning events

`kubectl get events -A --field-selector type=Warning -o json`, parse with
python3; group by involvedObject kind, namespace, name, reason — record
count, lastTimestamp, one-line message per group. Filter client-side; a
second server-side selector silently drops events on some API servers.
Completion check: every warning group has a line. Events expire (~1h): cross
-check CrashLoopBackOff pods and restart counts before reporting clean.

## Pitfalls

- Org-level alert endpoints need org ownership scopes; a 404/403 on one
  alert class is permission, not zero alerts — verify before reporting clean.
- Dependabot's org endpoint is the flakiest of the three; a truncated page
  looks like a clean repo — reconcile repo counts when the run matters.
- A bare TLS probe returning `000` on an mTLS-gated endpoint is the gateway
  working — do not file it.
- `curl -sI` (HEAD) hides body-level leaks; when a header check passes but
  the endpoint matters, follow with a ranged GET and diff the bodies.
- Security-header findings rot fast: re-check the exact route and port
  before re-filing anything a previous run flagged.
- Branch protection reads differently through rulesets — a repo whose
  classic protection endpoint 404s may still be ruleset-protected.
- `gh run list --created` filters on creation, not conclusion — a failure
  that started 25h ago vanishes from the window; sweep the union of creation
  time and `updatedAt` when precision matters.
- `--log-failed` returns empty while sibling jobs still run; fall back to
  `gh api repos/<repo>/actions/jobs/<id>/logs`.
- Repo enumeration with `--limit 100` silently truncates bigger orgs; page
  with `--paginate` or reconcile against a known count.
- Flapping and looping sources re-file every sweep when dedup matches
  message text — dedup on the stable object only.
- Events expire and aggregated counts reset on rotation; `count` is current
  pressure, not lifetime totals — phrase findings accordingly.
- A Ready=True object with stale `lastAttemptedRevision` is not healthy —
  read conditions, not the summary column.
- Fastlane patches target the source overlay, never rendered output;
  rendered manifests often exclude generated material.
- `kubectl get kustomizations` needs the CRD plural or the flux CLI's
  server-side print — a bare `kubectl get flux` noun errors.
- Cluster-level failures (node down, storage recovery, volume trouble) are
  issue-only, never a PR from an audit run.

## Verification

```bash
gh issue list -R <repo> --state open --search \"<object identity>\"
```

Report states: surface(s) read, findings found, drops with reasons, issues
filed (links), PRs left open, resolutions since last sweep, top open items
re-verified.

## See also

- `sks-issue` — issue body shape for filed findings.
- `sks-fastlane` — the full eligibility gate referenced by step 6.
- `sks-adversarial` — disposable sandbox for uncertain reads (step 1).
- `sks-renovate-sweep` — owns renovate PR checks; the CI surface drops them.
