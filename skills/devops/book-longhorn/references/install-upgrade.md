# Install & Upgrade (Longhorn 1.12.1)

## Install methods

Rancher Catalog, kubectl, **Helm**, Helm Controller, Fleet, **Flux**, ArgoCD, airgap.
All Longhorn CRs/pods live in namespace `longhorn-system`.

## Common node requirements (V1 + V2)

- Container runtime (Docker ≥1.13, containerd ≥1.3.7).
- Kubernetes **≥ v1.25** (`kubectl version`).
- RWX needs NFSv4 client on every node.
- `bash`, `curl`, `findmnt`, `grep`, `awk`, `blkid`, `lsblk` installed.
- Mount propagation enabled (Rancher v2.0.7+ default-on).
- Longhorn workloads must run as **root / privileged**; host paths accessed:
  `/dev`, `/proc` (ro), `/var/lib/longhorn`, `/boot` (ro), `/etc` (ro), `/lib/modules`, `/sys`.

## V1 Data Engine extras

- `open-iscsi` or `iscsiadm` installed.

## V2 Data Engine extras

- Kernel modules: `vfio_pci`, `uio_pci_generic`, `nvme_tcp`.
- Local **NVMe SSDs** strongly recommended; AMD64 with **SSE4.2**.
- Kernel ≥ **5.19** for NVMe/TCP; ≥ **6.7** for stability (avoids SPDK #3116 memory issue).
- Huge pages: **1024 × 2 MiB** pages (≈2 GiB) reserved per node for SPDK.
- IOMMU group isolation: NVMe must not share an IOMMU group with a PCIe bridge (else
  `failed to bind NVMe disk` / error -22 → use AIO driver).

## longhornctl (preflight helper)

```bash
ARCH=amd64
curl -LO "https://github.com/longhorn/cli/releases/download/v1.12.1/longhornctl-linux-${ARCH}"
curl -LO "https://github.com/longhorn/cli/releases/download/v1.12.1/longhornctl-linux-${ARCH}.sha256"
echo "$(cat longhornctl-linux-${ARCH}.sha256 | awk '{print $1}') longhornctl-linux-${ARCH}" | sha256sum --check
sudo install longhornctl-linux-${ARCH} /usr/local/bin/longhornctl
longhornctl version
# V1 check:  longhornctl check preflight
# V2 check:  longhornctl --kubeconfig ~/.kube/config --image longhornio/longhorn-cli:v1.12.1 check preflight --enable-spdk
# install:   longhornctl --kubeconfig ~/.kube/config --image longhornio/longhorn-cli:v1.12.1 install preflight [--enable-spdk]
```

## Helm install

```bash
helm repo add longhorn https://charts.longhorn.io && helm repo update
helm install longhorn longhorn/longhorn --namespace longhorn-system --create-namespace --version 1.12.1
kubectl -n longhorn-system get pod
```

Verify pods: `longhorn-manager`, `longhorn-ui`, `longhorn-driver-deployer`,
`longhorn-csi-plugin` (2/2), `csi-*`, `instance-manager-*`, `engine-image-*`.

## Flux install

```bash
kubectl create ns longhorn-system
flux create source helm longhorn-repo --url=https://charts.longhorn.io --namespace=longhorn-system --export > helmrepo.yaml
flux create helmrelease longhorn-release --chart=longhorn --source=HelmRepository/longhorn-repo \
  --chart-version=v1.12.1 --namespace=longhorn-system --export > helmrelease.yaml
kubectl apply -f helmrepo.yaml helmrelease.yaml
flux get helmrelease longhorn-release -n longhorn-system
```

Enable V2: set `defaultSettings.v2DataEngine: true` in Helm values (or the `longhorn-system`
setting after install).

## Upgrade

- **Supported path: only v1.11.x → v1.12.1.** Other versions must step to v1.11.x first.
- V1 engine live-upgrade supported; **V2 engine live-upgrade NOT supported — detach first.**
- Pre-upgrade job (Helm/Rancher) blocks unsupported paths; logs reason, can rollback.
- Set `spec.failurePolicy: abort` (NOT `reinstall`) on HelmChart/HelmRelease upgrades.

```bash
# kubectl
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.12.1/deploy/longhorn.yaml
# Helm
helm upgrade longhorn longhorn/longhorn --namespace longhorn-system --version 1.12.1
# Flux: set spec.chart.spec.version: v1.12.1 in HelmRelease
```

- **Always back up volumes before upgrading.** Do not modify the default StorageClass
  parameters (provisioner change is Forbidden; delete deprecated SC first).
