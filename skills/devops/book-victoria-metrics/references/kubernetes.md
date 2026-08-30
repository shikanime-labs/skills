# Kubernetes: Operator & Helm

Distilled from <https://docs.victoriametrics.com/operator/> and the Helm docs.
Reference: <https://docs.victoriametrics.com/operator/> , <https://docs.victoriametrics.com/helm/>

## VictoriaMetrics Operator (vmoperator)

- Classic K8s operator for declarative, GitOps/IaC-style management of all VM components (vmsingle, vmcluster, vmauth, vmagent, vmalert, ...).
- Inspired by prometheus-operator; seamless migration from prometheus-operator (auto-converts Prometheus CRs).
- Features: deploy any number of VM apps; CRD-based config; delegate monitoring config to end-users; integrates vmbackupmanager for backups (VMSingle/VMCluster backup automation); k8s-stack helm chart with ready-made use cases.

### Key concepts

- **Custom resources** (CRDs): `VMSingle`, `VMCluster`, `VMAgent`, `VMAlert`, `VMAuth`, `VMServiceScrape`, etc. See operator/resources.
- **Reconciliation cycle**: operator converges cluster state to declared CRs; subscribes to create/update/delete events; some objects force-resync on `VM_FORCERESYNCINTERVAL`.
- Quick start, setup, security, configuration, HA, auth/exposing components, enterprise docs under operator/.

## Helm charts (no operator required)

- `victoria-metrics-k8s-stack` — full stack (VMCluster/VMSelect/VMInsert/VMStorage, vmagent, vmalert, Grafana) with defaults.
- Individual charts for single-node and cluster versions; plus operator chart.
- Helm repo: github.com/VictoriaMetrics/helm-charts.

## Backup automation in K8s

- Operator integrates vmbackupmanager: VMSingle/VMCluster CRs support `backup` section → scheduled snapshots + remote backups.
- Sidecar `vmbackup` pattern for cluster vmstorage nodes (one per pod).

## When to load this

Load when deploying VM on Kubernetes via Operator CRs or Helm, migrating from prometheus-operator, or automating backups in-cluster.
