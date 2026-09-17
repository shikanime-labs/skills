# Bisect evidence: nameReference silently skipped with mid-layer namespace

Observed 2026-08-28 on kustomize v5.8.1 while removing
`disableNameSuffixHash` from `apps/catbox/overlays/nishir-tailnet/kustomization.yaml`.

## Symptom

`kustomize build apps/catbox/overlays/nishir-tailnet` rendered:

- Secret: `name: catbox-sops-key-5dgcftgggf` (hashed, correct)
- VirtualMachine volume: `secretName: catbox-sops-key` (plain, NOT rewritten)

No error, exit 0. Configurations file was present and syntactically valid
(`configurations: [namereference.yaml]`), and the identical namereference
shape works for jellyfin (`Certificate` → `passwordSecretRef`).

## Minimal repro chain (all in /tmp/nrtest)

1. Flat build (secret + VM in one dir, generator + configurations) — **works**.
2. Nested build (VM in `base/`, generator in `overlay/`) — **works**.
3. Two-level chain (`base/` → `mid/` → `overlay/`, namespace in `mid/`) — **fails**.
4. Same chain, namespace removed from `mid/` — **works**.
5. Single-level, namespace in the top overlay — **works**.
6. Two-level, namespace in both `mid/` and top — **works** (catbox final fix,
   matches jellyfin nishir-tailnet which sets `namespace: shikanime` in both
   nishir and nishir-tailnet).

## Conclusion

`namespace:` set ONLY in an intermediate kustomization between the referenced
resource (base) and the generator (top overlay) disables nameReference
rewriting. Duplicate `namespace:` at the top overlay to fix.

## Red herrings ruled out during the bisect

- Array path syntax (`volumes/secret/secretName`): works fine in flat builds.
- `group`/`version` in the fieldSpec: not needed, and adding them did not fix.
- GVK mismatch for the custom kind (`kubevirt.io/v1 VirtualMachine`): ruled out
  when the flat build with the same kind rewrote correctly.
- `labels:`/`patches:` sections: ruled out by toggling them in the repro.
- One corrupt repro (printf overwrote the whole kustomization, dropping the
  secretGenerator) briefly suggested the Secret vanished — re-run cleanly.

## Catbox fix (final state)

- `apps/catbox/overlays/nishir-tailnet/kustomization.yaml`: removed
  `options.disableNameSuffixHash`, added `namespace: shikanime` +
  `configurations: [namereference.yaml]`.
- New `apps/catbox/overlays/nishir-tailnet/namereference.yaml`:
  `Secret` → `VirtualMachine` at `spec/template/spec/volumes/secret/secretName`.
- Base `apps/catbox/base/vm.yaml` untouched; rewrite happens at render time.
- Verified: overlay build rewrites to `catbox-sops-key-5dgcftgggf`;
  `kustomize build clusters/nishir/overlays/tailnet` renders clean
  (catbox wired via `clusters/nishir/overlays/tailnet/ks.yaml`).
