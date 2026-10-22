---
name: sks-audit
description:
  "Use when auditing fleet or org health - security alerts, redteam, CI
  failures, alerting, Flux readiness, Kubernetes events, SDLC efficiency:
  read the surface, dedup, file findings, fastlane fixes."
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
      - sks-async
      - sks-maintenance
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Audit

Read a fleet or org surface, dedup against the filing repo, file uncovered
findings as issues, and fastlane small fixes. Read-only posture: an audit
never closes, dismisses, silences, acks, resolves, or re-triggers anything — resolution
is an operator decision.

Org targets (orgs in scope, filing repos, cluster context, endpoints) live in
`references/shikanime.md`; read it before the first sweep and when a target
moved.

## Procedure

1. **Read the surface section**, including its pitfalls and fastlane scope.
   Deepen a read you cannot trust, or a path the feeds do not model, in a
   disposable sandbox per `sks-adversarial`, fanning out independent trials
   with `sks-async`: promote findings, never the sandbox.

2. **Enumerate** with the surface's command and record its listed fields.
   Every section names its completion check, and a quiet read is not a clean
   surface.

3. **Noise-filter conservatively.** Drop a class only when its section says
   so, and record the drop with its reason; an unexplained drop is a finding.
   Crashloops, probe failures, evicted pods, secret-scanning alerts, and
   cluster-level failures keep their item no matter how routine they look.

4. **Dedup** against the filing repo: `gh issue list -R <repo> --state open`,
   matching on object identity (repo+alert, object+reason, namespace/name),
   never on message text — flapping sources re-file every sweep otherwise.
   Tracked findings are listed in the report, never re-filed.

5. **File each new finding** via `sks-issue`: free-text title, bug label,
   plus `security` only when the repo has it. Assign per repo policy where
   eligible. One issue per stable object, updated by later runs — never one
   issue per occurrence.

6. **Fastlane small fixes** in the surface's eligible scope through the
   `sks-fastlane` gate, which applies in full. Ineligible or checks pending
   leaves the PR open, never waits.

7. **Note resolutions.** Findings resolved since the last sweep are listed;
   the audit closes nothing automatically.

8. **Memory loop.** Before reporting: honcho_search this surface's audit and
   honcho_context for recurring context (findings that recur, remediations in
   flight, known flappers), re-verifying the top open items instead of
   rediscovering them. After reporting: honcho_conclude one line per durable
   lesson.

## Surfaces

### GitHub security alerts

`gh api /orgs/<org>/code-scanning/alerts --paginate` — same for
`/secret-scanning/alerts` and `/dependabot/alerts`, per org in scope. Keep
`state=="open"`; record alert type, repo, severity, CVE or rule id, html_url
and created_at, ranking critical and high first, with secret-scanning always
urgent and dependabot by manifest reachability when evidenced. Cross-check
the perimeter surface before filing; already-proven findings are referenced,
not re-filed. Fastlane scope: dependency bump, config hardening flag.

Completion check: every org × alert-type pair enumerated. Pitfalls: org-level
endpoints need ownership scopes, so a 404/403 is permission rather than zero
alerts; dependabot's endpoint is the flakiest of the three, so a truncated
page looks like a clean repo — reconcile repo counts when the run matters.

### Perimeter redteam

Depth-1 clone of the fleet manifests for public endpoints, Envoy Gateway
routes and TLS hostnames, plus open TCP surfaces, exposed dashboards,
container registries, and the GitHub attack surface (branch protection, CI
secrets, webhooks). Probes are read-only: `openssl s_client` for TLS posture,
`curl -sI` for headers, auth-bypass checks, anonymous API access, registry
tag listability. Record command and output excerpt per finding; a finding
whose only proof is a tool's claim is re-verified by hand before filing.
Read-only: never exploit past proof, never modify or delete anything, and
never touch secrets. Fastlane scope: header addition, rate limit,
cipher policy.

Completion check: every declared public hostname has a probe result.
Pitfalls: a bare `000` on an mTLS-gated endpoint is the gateway working,
never a finding; HEAD hides body-level leaks, so follow a passing header
check with a ranged GET; header findings rot fast, so re-check the exact
route and port before re-filing; a repo can read as exposed because its
classic protection endpoint 404s while rulesets still protect it; stopping at
CVE or advisory absence is blind, not clean — audit the sweep's own path.

### CI failures

`gh repo list <org> --limit 100 --json nameWithOwner` per org, then per repo
`gh run list -R <repo> --status failure --created ">$(date -d '-24 hours' '+%Y-%m-%d')"`.
Excludes renovate PR checks (owned by `sks-maintenance`:
`references/renovate.md`), draft-PR CI skips, and flakes that passed on
rerun. Record run URL, failing job, first error lines and head sha; a
scheduled failure with zero code changes is an infra finding, not a code
bug. Fastlane scope: trivial CI fixes — yaml fix, action pin,
typo.

Completion check: every repo enumerated, every trailing-window failure
recorded. File one issue per repo+workflow pair.
Pitfalls: `--created` filters on creation, so a failure that started 25h ago
vanishes from the window — sweep the union of creation time and `updatedAt`
when precision matters; `--log-failed` returns empty while sibling jobs still
run, so fall back to `gh api repos/<repo>/actions/jobs/<id>/logs`;
`--limit 100` silently truncates bigger orgs, so page with `--paginate`.

### Alertmanager alerts

`curl -s <alertmanager>/api/v2/alerts`, parsed with python3; record
alertname, labels, annotations and startsAt, filtering on
`status.state == "active"` because the API also returns recently-resolved
alerts. Fastlane scope: values bump, threshold.

Completion check: every active alert has a recorded line. Pitfalls: Grafana's
HTTP API is a different surface — when it is OIDC-only with no API-key path,
read the vm* APIs instead, never scraping dashboards.

### Flux readiness

`kubectl get kustomizations.kustomize.toolkit.fluxcd.io -A -o json` and
`kubectl get helmreleases.helm.toolkit.fluxcd.io -A -o json`; list every
object whose Ready condition is False with message and source revision.
Deliberately suspended objects are reported separately, never counted as
failures, never touched, resumed or annotated. Fastlane scope: image pin,
timeout, single-overlay manifest patch.

Completion check: every Ready=False object has a recorded line. Pitfalls: a
Ready=True object with stale `lastAttemptedRevision` is not healthy, so read
conditions rather than the summary column; a bare `kubectl get flux` noun
errors, so use the CRD plural or the flux CLI's server-side print; fastlane
patches target the source overlay, never rendered output.

### Kubernetes warning events

`kubectl get events -A --field-selector type=Warning -o json`, parsed with
python3; group by involvedObject kind, namespace, name and reason, recording
count, lastTimestamp and a one-line message per group. Filter client-side
because a second server-side selector silently drops events on some API
servers. Fastlane scope: probe timing, resource requests.

Completion check: every warning group has a line. Pitfalls: events expire
(~1h), so a quiet read is not a healthy cluster — cross-check CrashLoopBackOff
pods and restart counts before reporting clean; aggregated counts reset when
the event object rotates, so `count` is current pressure rather than lifetime
totals; cluster-level failures (node down, storage recovery, volume trouble)
are issue-only, never a PR from an audit run.

### SDLC efficiency

Process metrics over the orgs' issues and PRs. Census: `gh api
"search/issues?q=org:<org>+is:open+type:issue" --jq .total_count` and the
same with `type:pr`. Untriaged: open items missing derivable metadata,
computed against what each repo supports. Latency: over merged PRs in the
window, time to first review and time to merge, with bot-authored PRs in a
separate row. Residue: issues still open whose linked PR already merged,
read per PR from Development links. Stalls: open PRs with `reviewDecision`
CHANGES_REQUESTED or REVIEW_REQUIRED, or `mergeStateStatus` BLOCKED or
BEHIND, older than 7 days. Stale branches: heads merged or behind the
default branch older than 7 days. Record every number before drawing any
conclusion, and re-measure in-session — a previous run's numbers are the
baseline, never the current value. Completion check: census, untriaged,
latency, residue, stalls, and stale branches each carry a recorded value
per org, with the median reported beside any p90. Cross-check the residue
count per PR, never by repo-wide text search. Findings from this surface
are proposals: file issues only, no fastlane PR.

## Verification

```bash
gh issue list -R <repo> --state open --search "<object identity>"
```

Report states: surface(s) read, findings found, drops with reasons, issues
filed (links), PRs left open, resolutions since last sweep, top open items
re-verified.

## See also

- `sks-issue` — issue body shape for filed findings.
- `sks-fastlane` — the full eligibility gate referenced by step 6.
- `sks-adversarial` — disposable sandbox for uncertain reads (step 1).
- `sks-maintenance` (`references/renovate.md`) — owns renovate PR checks; the
  CI surface drops them.
