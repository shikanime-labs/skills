---
name: book-longhorn
description: Distilled Longhorn 1.12.1 documentation knowledge base.
version: 0.1.0
author: Hermes
license: CC-BY-4.0
metadata:
  hermes:
    tags: [Longhorn, Kubernetes, Storage, CSI, V1, V2, Backup, DR]
---

# Longhorn Documentation (1.12.1)

Distilled, on-demand reference for Longhorn — the CNCF distributed block storage
system for Kubernetes. Source material is the official `longhorn.io/docs/1.12.1`
corpus (architecture, install/upgrade, volumes, backups/DR, high availability,
nodes/disks, V2 data engine, security, monitoring, troubleshooting).

This is NOT a substitute runbook for a specific cluster. It does not contain
fleet secrets, contexts, or live cluster state — pair it with the
`longhorn-volume-recovery` skill for nishir-specific incident procedures. The
body below holds the central mental models and a reference index; each topic
lives in its own `references/` file and costs nothing until you load it.

All content is distilled structure (definitions, defaults, decision rules,
verbatim parameter/port names) — not a copy of the docs.

## When to Use

- "What does Longhorn setting X do / what is its default?"
- "How do I configure StorageClass parameter Y for Longhorn?"
- "How does Longhorn V1 vs V2 behave for feature Z?"
- "How do I set up a backup target, recurring job, or DR volume?"
- "What are the install prerequisites for V1 or V2 data engine?"
- "How do node drain / graceful removal / disk eviction work?"
- "Which ports does Longhorn use for NetworkPolicy?"
- "How do I interpret Longhorn metrics / generate a support bundle?"

## Prerequisites

- Target Longhorn version is **1.12.1** (docs are version-specific; do not apply
  to other releases without re-checking).
- Cluster namespace for all Longhorn CRs and pods: `longhorn-system`.
- CSI driver name / StorageClass provisioner: `driver.longhorn.io`.
- Helm chart repo: `https://charts.longhorn.io` (chart name `longhorn`).
- Optional CLI helper: `longhornctl` (linux amd64/arm64) for preflight checks.

## How to Run

Load a specific topic on demand with `skill_view`:

```text
skill_view(name="book-longhorn", file_path="references/<file>.md")
```

For a verbatim doc page not covered below, fetch via `web_extract`:
`https://longhorn.io/docs/1.12.1/<path>/`. Use the GitHub tree
(`longhorn/website` → `content/docs/1.12.1/`) to discover page paths.

## Quick Reference

- Components: Longhorn Manager (DaemonSet, control plane), Longhorn Engine
  (per-volume data plane), Instance Manager (lifecycles engines/replicas),
  CSI plugin + sidecars, Share Manager (RWX NFS), UI.
- Data engines: **V1** (Linux process, sparse files, iSCSI), **V2** (SPDK,
  huge pages, block devices, NVMe). Enable only one per cluster unless needed.
- Access modes: RWO (default), RWOP (single pod), RWX (NFS share-manager).
  ROX not supported.
- Default replica count: **3**. Tolerate up to N-1 replica failures.
- Key ports: Manager 9500/9501/9502/9503, Instance Mgr 8500-8504 + 10000-30000,
  iSCSI 3260, Share Mgr NFS 2049. See `references/security.md`.
- Backupstore: NFS / SMB / S3-compatible; backups are 2 MiB blocks by default.
- System upgrade: only v1.11.x → v1.12.1 supported; engine live-upgrade V1 only.

## Procedure

1. Identify the topic from the Reference Index below.
2. Load that `references/<file>.md` via `skill_view`.
3. Apply the parameter names / defaults / commands verbatim from the file.
4. For live cluster state, use `kubectl -n longhorn-system get <cr>` against the
   CRDs (volume, engine, replica, node, disk, backup, systembackup, recurringjob,
   shardgroup, shard).

## Pitfalls

- Docs are version-locked: 1.12.1 settings/ports differ from older releases.
- V1 and V2 have different prerequisites, disk types, and feature parity — never
  mix assumptions.
- `allowedTopologies` + `dataLocality: strict-local` conflict (immutable PV
  nodeAffinity vs Longhorn pinning).
- V2 `sharded` layout drops backup/clone/backing-image/DR/live-migration.
- Over-provisioning is allowed by default (`StorageOverProvisioningPercentage`
  default 100); disk-full can wedge scheduling.
- Support bundle generation is not concurrent-safe (overwrites in progress).

## Verification

A skill load is verified by successfully retrieving the requested topic file:
`skill_view(name="book-longhorn", file_path="references/<file>.md")` returns
the chapter. For live config, confirm against the cluster:
`kubectl -n longhorn-system get settings.longhorn.io -o name`.

## Reference Index

- `references/architecture-concepts.md` — Manager/Engine/CSI model, V1 vs V2,
  replicas, snapshots, backups, terminology. Load for "how does X work".
- `references/install-upgrade.md` — install methods (Helm/Flux/kubectl),
  V1/V2 node prerequisites, `longhornctl`, upgrade paths, failure recovery.
- `references/config-reference.md` — StorageClass parameters, Helm values, and
  high-signal global settings with verbatim defaults.
- `references/volumes-operations.md` — RWO/RWX/RWOP, create, expansion, trim,
  encryption wiring, V2 volume specifics.
- `references/backup-dr.md` — backup target, incremental/full backup, recurring
  jobs, restore, DR volumes, system backup/restore.
- `references/high-availability.md` — data locality, node-failure handling,
  auto-balance, automatic recover-volume, RWX fast failover.
- `references/nodes-disks-maintenance.md` — filesystem vs block disks, disk
  scheduling, graceful node removal, drain policies, eviction.
- `references/v2-data-engine.md` — V2 requirements, huge pages, sharding /
  erasure coding, NVMe/AIO/VirtIO drivers.
- `references/security.md` — volume encryption, mTLS, NetworkPolicy ports.
- `references/monitoring-troubleshooting.md` — metrics catalog, support bundle,
  common issues, data recovery (corrupted replica, restore-without-system).
