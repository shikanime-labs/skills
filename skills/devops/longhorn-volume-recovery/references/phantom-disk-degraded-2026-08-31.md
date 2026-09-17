# Phantom replica diskIDs — perpetual degraded (2026-08-31)

## Symptom
A volume (e.g. `sukebe-doujins-data`) stays `robustness=degraded` with one
`running` replica + a 2nd replica `currentState=stopped` on a node, even though
the storageClass `diskSelector` tag (e.g. `nearline`) IS present on real disks
on all nodes. The session handoff attributed it to "no `nearline` disk is
tagged" — that premise was FALSE.

## Detection
Disk IDs `e35af170-6a73-44d0-a3dd-14a912bd66e1` (ashira) and
`316df5ad-c652-47d7-9181-8934e95b4c7e` (nalsha) appear as `spec.diskID` on
replicas but exist in NO node's `spec.disks`/`status.diskStatus`. Fleet scan
found 15 replicas on these two phantom disks across 8 degraded volumes:
`sukebe-doujins-data`, `shows-data`, `sukebe-videos-data`, `forgejo-data`,
`staging-data`, `sync-data`, `timeline-data`, `sukebe-games-data`.
(`movies-data` was healthy — proof the `nearline` selector itself works.)

## What did NOT work (do not loop on these)
- Deleting the phantom replica + `patch volume … replicaAutoBalance:
  best-effort` → Longhorn rescheduled the new replica onto the SAME phantom
  disk ID. No heal.
- Editing the StorageClass `diskSelector` (`nearline`→`standard`) → only affects
  newly-provisioned volumes; the bound degraded volume is unchanged.

## Root cause (likely)
A disk removed upstream in the **NixOS machines repo** (the source of truth for
node disk config). The manifests-repo StorageClass selector is a red herring.
The phantom disk IDs are stale references Longhorn keeps reusing for new
replicas.

## Reproduction recipe
See the fleet scan in the SKILL.md "Phantom replica diskIDs" pitfall
(reports every replica whose `spec.diskID` is absent from all nodes'
`spec.disks`).
