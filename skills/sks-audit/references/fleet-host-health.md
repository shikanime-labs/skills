# Fleet Host Health

- Orgs: `shikanime-labs` and `shikanime-studio`.
- Filing repo for fleet findings: `shikanime-labs/manifests`.
- Fleet cluster: nishir. Workstation reads go through
  `kubectl --context nishir-k8s-operator.taila659a.ts.net get --raw` and the
  vmselect service proxy
  (`monitoring-system/vmselect-vmks-victoria-metrics-k8s-stack:8481/proxy/select/0/prometheus`).
- Dedup key: node + unit — one issue per host+unit, updated by later runs.
- Fastlane scope: none — host remediation is operator-side, issue-only.

## Probe mechanics

Enumeration and thresholds stay on the node-exporter path; ssh is a depth
tool for flagged or metrics-absent hosts only. The ssh-degraded host rotates
day to day (nemishi 2026-11-16, fushi 2026-11-17) — an ssh-only enumeration
silently loses whichever host is degraded that day.

Per node, over the vmselect service proxy:

- Root-fs use%: `node_filesystem_avail_bytes{mountpoint="/"} /
  node_filesystem_size_bytes{mountpoint="/"}` — flag >= 90%, naming SD-card
  devices (`/dev/mmcblk0p2`) explicitly. Same-day drift of 15pp was observed
  (nemishi 80.3% → 95%), so the run-time value is the finding, not the last
  baseline.
- Failed units: `node_systemd_unit_state{state="failed"} == 1`, dropping
  `session-*.scope` (logged-out ssh scopes, cosmetic on every host).
- `nixos-upgrade.service` state from the same metric.
- Comin state: `up{job="comin"}` coverage, `comin_last_build_failed`,
  `comin_last_deployment_failed`, `comin_need_to_reboot`.

SSH depth probe (only when flagged or absent from `up{job="comin"}`):
`systemctl is-failed nixos-upgrade.service comin.service`, `comin status`
(generation, commit, build state), `readlink /run/current-system`,
`df -h /`. A banner-exchange timeout on a host that answers ping is
userspace degradation — itself a finding.

## Pitfalls

- `comin_deployment_info` is an info gauge: value always `1`, generation
  identity in the `commit_id` label. Any staleness expression doing
  `time() - <value>` is structurally always-true and fires from the moment
  the series exists (observed: five hosts, identical `2026-11-10T14:30:00`
  start). The shipped `CominDeployStale` rule has this defect — verify a
  DeployStale alert's expression against the live metric shape before
  trusting it.
- Comin never retries a failed build: `comin_last_build_failed == 1` pins
  the host on its old generation until something re-queues the build. The
  observed wedge was a dead remote-builder hop — journal line
  `cannot build on 'ssh-ng://builder@<host>...'` (sd-card nodes build via
  `ssh-ng://builder@nemishi...`, `modules/nixos/profiles/distributed.nix`).
- Hosts pinned to an old generation predate the comin scrape hostname
  relabel: their series collapse into one `instance="127.0.0.1:4243"` bucket
  with multiple hosts' `commit_id`s colliding, hiding per-host state. The
  fix generation carries the relabel but cannot deploy while the build is
  wedged — record the gap, do not trust the bucket.
- Cross-check `NodeSystemdServiceFailed` /
  `NodeFilesystemAlmostOutOfSpace` recording device and mountpoint: kubelet
  CSI globalmounts (`/var/lib/kubelet/plugins/...`) and macOS system volumes
  (`/System/Volumes/*`, workstation hosts) trip the same alertname while the
  host root fs is healthy.
- The comin forgejo remote can 503 on every poll while the github remote
  works — that is client-side evidence of forgejo volume pressure, not a
  comin defect; route it to the storage finding.
