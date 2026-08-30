# Helm Controller — HelmRelease

`HelmRelease` (`helm.toolkit.fluxcd.io/v2`): controller-driven install/upgrade/test/
uninstall/rollback + drift correction.

## Chart source — pick ONE

- `.spec.chart` (template) — helm-controller creates a `HelmChart` (name `<ns>-<hr>`,
  same ns as sourceRef) from `.spec.chart.spec.{chart, version, sourceRef, interval}`.
- `.spec.chartRef` — reference existing source: `OCIRepository` | `HelmChart` | `ExternalArtifact`.
- CONSTRAINT: exactly one of `.spec.chart` / `.spec.chartRef` (not both).
- Changing chart name → uninstall+reinstall unless `upgrade.chartNameChangeStrategy: InPlaceUpdate`.
- `OCIRepository` source: version reported as `<ver>+<digest[0:12]>`; digest appended so content change
  triggers upgrade even if Chart.yaml version unchanged (disable via `--feature-gates=DisableChartDigestTracking=true`).

## Key spec fields

- `.spec.releaseName` — Helm release name.
- `.spec.chart.spec.version` — semver range, e.g. `'6.5.*'`, `'>=1.0.0 <2.0.0'`.
- `.spec.values` — chart values (may be decrypted via SOPS if referenced secret is a values file).
- `.spec.interval` / `.spec.timeout`.
- `.spec.install.remediation.retries` / `.spec.upgrade.remediation.retries` — retry counts.
- `.spec.test.enable` — run Helm tests post-install/upgrade.
- `.spec.driftDetection.mode: enabled` + `.spec.driftDetection.ignore[]` (`paths`, `target.kind`) — re-apply on drift.
- `.spec.postRenderers[]` — kustomize/other post-render steps.

## Remediation / failure handling

- `.spec.install.remediation` / `.spec.upgrade.remediation`: `retries`, `strategy`
  (`rollback` | `uninstall` | `requeue` — default `rollback` for install, `uninstall` for upgrade).
- Failure counters reset when `values`/`chart version` change (`.status.lastAttemptedConfigDigest` /
  `.status.lastAttemptedRevision`).

## Wait / health tuning

- `install.disableWait` / `upgrade.disableWait` — skip waiting for resources ready (useful to inspect a failing deploy).
- Health uses standard kstatus + optional `.spec.healthCheckExprs` (CEL, like Kustomization).

## Status

- `.status.helmChart` — generated HelmChart ref.
- `.status.history[]` — chart name/version, config digest, release status, test hooks.
- `.status.lastAppliedRevision` / `.lastAttemptedRevision` / `.lastAttemptedReleaseAction` (install|upgrade).
- Conditions: `Ready`, `Released`, `TestSuccess`, `HistoryApplied`.

## Common errors

- `HelmChart '...' is not ready` — typo in chart name/version/url, or source not Ready (check `flux get sources chart`).
- `install retries exhausted` — a created resource didn't become ready in 5m; describe HR for events, or `disableWait: true`.
- `Request entity too large: limit is 3145728` — chart too big for a Secret; trim `.helmignore`/`.sourceignore`.
- `HelmChart` CRD conflict — on k3s/other bundled Helm controllers, qualify fully: `kubectl get helmcharts.source.toolkit.fluxcd.io` or `flux get source chart`.

## Commands

- `flux create helmrelease <name> --source=HelmRepository/<src> --chart=<c> --version='6.5.*' --export`
- `flux reconcile helmrelease <name>` | `flux debug helmrelease <name>` | `flux suspend/resume helmrelease <name>`.
