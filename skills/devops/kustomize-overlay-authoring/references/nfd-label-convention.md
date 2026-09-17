# NFD feature-label convention (manifests repo)

Node Feature Discovery (NFD) is deployed via `infrastructure/node-feature-discovery`.
It emits BOTH built-in standard labels and (formerly) custom `NodeFeatureRule`s.
Do NOT re-introduce custom `NodeFeatureRule`s unless a genuinely non-standard
feature must be derived — prefer the labels NFD emits natively.

## Standard PCI label (Intel iGPU / QSV)

NFD's PCI source emits, per PCI device, a label of the form:

```
feature.node.kubernetes.io/pci-<class>_<vendor>.present
```

- class `0300` = display controller (GPU/iGPU)
- vendor `8086` = Intel
- Therefore the Intel Quick Sync iGPU label is:

```
feature.node.kubernetes.io/pci-0300_8086.present
```

Live-confirmed present on `nalsha` (beelink-eq14) with value `true`. This is the
authoritative label for scheduling immich/jellyfin/immich-ml onto the QSV nodes;
the historical custom `feature.node.kubernetes.io/qsv.enabled` rule
(`configs/node-feature-discovery/nfr.yaml`, `intel-quicksync-video`) was a
redundant re-derivation and was removed (PR #1847, merge `c87a8268`).

## Built-in GPU label (AMD)

NFD's `gpu` source emits the built-in label:

```
feature.node.kubernetes.io/amd-gpu
```

No custom rule required. AMD GPU workloads (llama-cpp `deepseek-flash`,
`deepseek-flash-rpc`, `qwen-27b`, `qwen-embedding` in `apps/llama-cpp/`) consume
this directly. The `minisforum-ms-s1` instance-type selector was migrated off
this to the `amd-gpu` label in an earlier PR and no longer exists in the tree.

## Migration note (qsv.enabled → pci-0300_8086.present)

Keep `operator: In`, `values: ["true"]` unchanged when swapping the key:

```yaml
- key: feature.node.kubernetes.io/pci-0300_8086.present
  operator: In
  values:
    - "true"
```

Consumers migrated in #1847: `apps/immich-ml/overlays/nishir/patch-deploy.yaml`,
`apps/immich/overlays/nishir/patch-sts.yaml`,
`apps/jellyfin/overlays/nishir/patch-sts.yaml`.

Do NOT touch `accel: qsv` inside immich server config (`config.enc.yaml`) — that
is the ffmpeg transcoder acceleration type, not a node label.
