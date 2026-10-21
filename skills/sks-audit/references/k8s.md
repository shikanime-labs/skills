
# Kubernetes Events Audit

Audit the warning events of a Kubernetes fleet: group events by affected
object, filter known noise, file uncovered findings as issues, and fastlane
small manifest fixes. Crashloops, probe failures, and evictions keep their
item regardless of how routine they look.

Org-specific targets (cluster context, filing repo) live in
`references/k8s-shikanime.md`; read it when operating in a shikanime org.

## When to Use

- "Triage the cluster's warning events" / "what is unhealthy in the fleet".
- A recurring events sweep: read, group, dedup, file.
- One noisy object reported by a human — same grouping and gate rules.

## Procedure

1. **Read warning events.** `kubectl get events -A --field-selector
   type=Warning -o json`. Parse with python3. Group by involvedObject kind,
   namespace, name, and reason; record count, lastTimestamp, and a one-line
   message per group. Completion check: every warning group has a line.

2. **Noise filter, conservatively.** Drop a node-level kubelet event
   (FailedSync, short FailedMount on well-known paths) ONLY when the object is
   otherwise healthy. Every crashloop, probe failure, and evicted pod keeps
   its item even when counts are high. When in doubt, keep the item.

3. **Dedup against the filing repo.** `gh issue list -R <repo> --state open`;
   skip objects already covered by an open issue (match namespace/name and
   reason). Covered groups are listed in the report, never re-filed.

4. **File each new finding.** One issue per object+reason: object, namespace,
   reason, count, first-seen (eventTime), message, and a `kubectl describe`
   excerpt. Assign per repo policy where eligible.

5. **Fastlane small manifest fixes.** Eligible scope: probe timing, resource
   requests, image pin — a small patch within one overlay. Must pass the
   `sks-fastlane` gate in full. Ineligible or checks pending: leave the PR
   open; never wait.

6. **Escalate cluster-level failures to issues only.** Node down, storage
   recovery, or volume-level trouble never becomes a PR from an audit run.

## Pitfalls

- Events expire (default ~1h in most clusters): a quiet read is not a healthy
  cluster — cross-check pods in CrashLoopBackOff or with high restart counts
  before reporting clean.
- Aggregated counts reset when the event object rotates; `count` is evidence
  of current pressure, not lifetime totals — phrase findings accordingly.
- One issue per object+reason, updated by later runs — dedup on the object,
  never on message text, or a looping event re-files every sweep.
- `--field-selector type=Warning` runs server-side; adding a second selector
  on `involvedObject.kind` silently drops events on some API servers — filter
  client-side in python3 instead.

## Verification

```bash
kubectl get events -A --field-selector type=Warning -o json | python3 -c \
  "import json,sys; evs=json.load(sys.stdin)['items']; \
print(len(evs), 'warning events')"
gh issue list -R <repo> --state open --search "<namespace>/<name>"
```

Report states: events read, groups after filtering, drops with reasons, issues
filed (links), PRs left open.

## See also

- `sks-issue` — issue body shape for filed findings.
- `sks-fastlane` — the full eligibility gate referenced by step 5.
- `references/flux.md` — the companion GitOps-health audit.
- `references/grafana.md` — the companion alerting audit.
