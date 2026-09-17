# Stale `spec.nodeID` pin after a node outage (Longhorn)

## Pattern
A node holding Longhorn volumes goes down (reboot, crash, tailnet blip,
replacement). When it returns, consumer pods that should now run elsewhere sit
`ContainerCreating` forever because Longhorn still believes the volume is
attached to the dead node.

## Reproduction (2026-08-23, forgejo-data)
- Volume `forgejo-data` had `spec.nodeID: manash` while the pod was scheduled to
  `minish`. The only consumer (`forgejo-0`) was `ContainerCreating`.
- attachdetach-controller error (verbatim):
  ```
  AttachVolume.Attach failed for volume "forgejo-data" : rpc error: code = Internal
  desc = volume forgejo-data failed to attach to node minish with attachmentID
  csi-568bc2...: the volume is currently attached to different node manash
  ```
- `status.currentNodeId` was empty (logically detached) but `spec.nodeID` stayed
  pinned to `manash` → Longhorn would not let it attach elsewhere.
- `kubectl longhorn` plugin is NOT installed; the Longhorn CR CLI was unavailable.
- Clearing `spec.nodeID` via plain merge patch did NOT take while the volume was
  in `attached` state.

## Fix that worked
1. Break the stuck attachment confirmation:
   ```bash
   K="kubectl --context nishir-k8s-operator.taila659a.ts.net"
   K -n longhorn-system patch volumes.longhorn.io forgejo-data --type merge \
     -p '{"spec":{"disableAttachmentConfirmation":true}}'
   ```
2. Then clear the pin (this time it took):
   ```bash
   K -n longhorn-system patch volumes.longhorn.io forgejo-data --type merge \
     -p '{"spec":{"nodeID":""}}'
   ```
3. Verify: `spec.nodeID` flips to the live target (`minish`); a fresh
   `VolumeAttachment` to the correct node establishes; pod goes `Running`.

## Safety gate (NON-NEGOTIABLE)
Before breaking a pin, confirm no pod on ANY node is actively using the volume
on the dead node:
```bash
K get pods -A -o wide | grep <vol>
```
Only proceed if the only match is the `ContainerCreating` consumer. Force-
detaching a volume a running pod uses = data corruption / torn writes.

## 2026-08-30 mass variant (manash offline)
After manash returned from an outage, ~13 volumes still carried
`spec.nodeID=manash` (downloads-radarr-data, honcho-postgres-data,
jellyfin-config, mautrix-signal-data, sukebe-doujins-data, sukebe-scenes-data,
timeline-data, etc.). Same fix per volume. Sweep after ANY manash outage:
```bash
K -n longhorn-system get volumes.longhorn.io -o jsonpath='{range .items[*]}{.metadata.name}{" node="}{.spec.nodeID}{"\n"}{end}' | grep manash
```
