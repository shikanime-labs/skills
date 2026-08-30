# Security (Longhorn 1.12.1)

## Volume encryption

- Linux `dm_crypt` + `cryptsetup` + Kubernetes Secret. Reqs: `dm_crypt` module loaded,
  `cryptsetup` installed on worker nodes. Backups of encrypted volumes are also encrypted.
- Secret in `longhorn-system`: `CRYPTO_KEY_VALUE` (passphrase), `CRYPTO_KEY_PROVIDER: secret`,
  `CRYPTO_KEY_CIPHER: aes-xts-plain64`, `CRYPTO_KEY_HASH: sha256`, `CRYPTO_KEY_SIZE: 256`,
  `CRYPTO_PBKDF: argon2i`, `CRYPTO_PBKDF_FORCE_ITERATIONS: 200000`, `CRYPTO_PBKDF_MEMORY: 0`.
- StorageClass: `encrypted: "true"` + the four `csi.storage.k8s.io/*-secret-name` and
  `-namespace` (provisioner, node-publish, node-stage, node-expand). PVC stays `Pending` until
  secret retrievable by external-provisioner. Supports global or per-volume (`${pvc.name}` /
  `${pvc.namespace}`) secrets.

## mTLS (control plane <-> data plane gRPC)

- Disabled by default. Enable by creating `longhorn-grpc-tls` Secret (type `kubernetes.io/tls`)
  in `longhorn-system` BEFORE deploy; contains `ca.crt`, `tls.crt`, `tls.key`. Restart
  manager/instance-managers afterward. Manager has non-TLS fallback for mixed old/new.
- `tls.crt` CN = `longhorn-backend`; SANs include `longhorn-backend`,
  `longhorn-frontend`, `longhorn-engine-manager`, `longhorn-replica-manager`, `longhorn-csi`
  (+ `.longhorn-system`, `.svc` variants) and `127.0.0.1`. Generate CA with `openssl`/`cfssl`,
  sign `tls.crt` with it (enables rotation without interruption). `echo -n` when base64-encoding.
- Available since **v1.3.0**.

## NetworkPolicy ports

Helm values: `networkPolicies.enabled` (false — UI ingress; needs `type` k3s/rke2/rke1),
`networkPolicies.restrictInternalTraffic` (true — internal components only).
Key ports (TCP):

- Longhorn Manager: ingress 9500 (mgr/UI/CSI/recurring/driver-deployer), 9501 (conversion
  webhook), 9502 (admission webhook), 9503 (recovery backend). Egress to Instance Mgr
  8500–8504, Backing Image Mgr 8000, k8s API, external backupstore.
- Instance Manager: ingress 8500–8504 (from Mgr), 10000–30000 (other IMs), 3260 (iSCSI, node),
  8002 (backing image data source). Egress 10000–30000, 8002, backupstore.
- Share Manager: ingress 2049 (NFS, node). Egress none.
- CSI plugin: egress 9500 (Mgr) only; sidecars talk to k8s API + `csi.sock` UDS at
  `<kubelet-dir>/plugins/driver.longhorn.io/csi.sock`.
- Backing Image Mgr: 8000 (Mgr/other BIM); Egress 10000–30000, 8000.
- UI: egress 9500 (Mgr).
- Recurring job pod: egress 9500 (Mgr).
- `networkPolicies.restrictInternalTraffic` applies to mgr/IM/BIM/data-source/webhook/recovery.
- CNI must support NetworkPolicy (not all do — e.g. K3s+Traefik delay can fail recurring jobs
  briefly on apply).
