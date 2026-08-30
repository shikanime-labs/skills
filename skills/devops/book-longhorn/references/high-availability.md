# High Availability (Longhorn 1.12.1)

## Data locality

Modes (global default or per-Volume / StorageClass `dataLocality`):

- `disabled` (default) — replicas anywhere; accessible from any node.
- `best-effort` — try to keep one replica on the workload's node; volume keeps running even
  if impossible (e.g. disk full, tag mismatch).
- `strict-local` — ONLY one replica, forced onto the workload's node (higher IOPS/lower
  latency). **Incompatible with RWX.** Requires replica count 1.

Use case: distributed apps (databases) where HA is app-level; prevents two identical
replicas landing on one node.

## Node failure handling

Timeline after a node fails:

- ~1 min: `kubectl get nodes` shows `NotReady`.
- ~5 min: pods show `Unknown` / `NodeLost`. StatefulSet pods are NOT force-deleted (stable
  identity); Deployment pods with RWO get stuck `ContainerCreating` (volume still on dead node).
- Longhorn Pod Deletion Policy When Node is Down can force-delete terminating pods so the
  volume detaches and a replacement pod spins up elsewhere.

Recovery: if node returns within 5–6 min, k8s remounts but Longhorn must detach/reattach to
restore engines (device gone). If down longer, pods `Terminating`; on return, detach/reattach

- VolumeAttachment cleanup (1–7 min) — automatic.

## Volume recovery mechanisms

1. **Automatic Workload Pod Deletion** (setting `Automatically Delete Workload Pod when The
   Volume Is Detached Unexpectedly`): deletes controller-managed pods (Deployment/STS/DaemonSet)
   on unexpected detach / salvage / RWX share-manager error; controller restarts pod, k8s
   reattaches. Does NOT delete pods without a controller (manual restart needed).
2. **Automatic Volume Remounting** (no setting): checks global mount point every 10s; if
   filesystem went read-only (network drop / high disk latency), remounts to read-write.
   Fails if device write-protected (e.g. engine crash) → relies on mechanism 1.

## Replica auto-balance

Options: `disabled` (default) / `least-effort` (minimal redundancy) / `best-effort` (even).
Per-volume `volume.spec.replicaAutoBalance` overrides global (default `ignored` = inherit).

- `best-effort` + `Replica Auto Balance Disk Pressure Threshold (%)` migrates replicas within
  a node when disk usage hits threshold. Balances node/zone first, then disk.
- Only runs for **Healthy** volumes; Unhealthy/Detached volumes are skipped by design
  (manual intervention required).

## RWX fast failover

Experimental setting `RWX Volume Fast Failover`: direct heartbeat to the NFS server; on
unresponsive server, spawns a new one faster and shortens recovery grace from **90s to 30s**.
