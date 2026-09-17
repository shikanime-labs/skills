# Tailnet route patch layout — PR chain #2079–#2081 (2026-09-02)

Conventions that govern `apps/**/overlays/nishir-tailnet/` route patches after
the JSON6902 inline refactor.

## Final layout (post-#2081)

- nishir overlays: strategic-merge `patch-httproute.yaml` (may be multi-doc,
  no `target:` block) + `patch-sts.yaml`/`patch-pvc.yaml` — UNCHANGED.
- nishir-tailnet overlays: NO per-route patch files. All JSON6902 ops are
  inline in `kustomization.yaml`:

  ```yaml
  patches:
    - patch: |-
        - op: add
          path: /spec/hostnames/-
          value: bazarr.taila659a.ts.net
        - op: replace
          path: /spec/parentRefs
          value:
            - name: bazarr
              sectionName: https
      target:
        kind: HTTPRoute
        name: bazarr
  ```

- One inline entry per targeted route. Hostnames APPEND (scalar `add /-/`),
  parentRefs REPLACE (they must point at the tailnet gateway).

## The scalar-append rule (#2080)

`op: add` on `/spec/hostnames/-` appends the VALUE as one array element.
`value: [host]` (list) appends a nested list — rendered output becomes
`- - host`, build exits 0, hostname is garbage. Two hostnames = two ops.

Detection: render the overlay, flag any hostname list item whose text starts
with `- `.

## Multidoc findings (tested, kustomize 5.8.1) — #2081 rejected shapes

1. `{patch, target}` multidoc file → `unable to parse SM or JSON patch`
   in all three wiring forms (patches+target, path-only, patchesJson6902).
2. Multidoc ops-list + one entry per route → renders, but pairing is
   ORDER-DEPENDENT: swapped entry order made both targets consume doc 1 and
   silently dropped doc 2 (verified by A/B render). Unsafe.
3. Single ops list kind-only target → impossible; ops differ per route.

Conclusion: one file per route WAS mandatory for file-form JSON6902, hence
the inline refactor.

## RFC 6902 add semantics worth remembering

- add on existing object member == replace. Member-form `add /spec/hostnames`
  with a list value is the CREATE-safe variant for routes with no `hostnames:`
  member at all (e.g. slack base routes) — it both creates and would replace.
- append form `add /spec/hostnames/-` requires the member to exist.

## Synapse matrix-redirect latent bug (fixed in #2081)

The synapse tailnet kustomization was already inline at origin/main and so
escaped the #2080 scalar sweep — it carried
`value: [matrix.taila659a.ts.net, matrix-discord-media.taila659a.ts.net]`
on an append. Split into two scalar ops. Lesson: the list-append bug class
hides in ANY already-inline patch too; sweep by grep, not by file type.

## hermes-agent api-server port regression (fixed in #2082)

A route-split PR removed a `containerPort` from one component's patch-sts
without the destination component re-adding it; probes referencing the port
NAME then fail `strconv.Atoi` and the pod pins at 1/2. Rule: a component
referencing a named port must declare that containerPort in the same patch.
Details: `references/probe-port-name-drop.md`.

## Post-#2081 fleet state (structural audit 2026-09-02)

- All 30 tailnet overlays are inline; authelia tailnet kustomization is the
  SOLE remaining `op: replace` on `/spec/hostnames` (member form, replaces the
  whole list — violates the append directive; app not deployed so latent).
  Sweep pattern: `op: replace` immediately followed by `path: /spec/hostnames$`.
- 27 orphaned tailnet `patch-netpol.yaml` files exist (envoy+vmagent ingress
  template, unwired). Working netpol patterns in-repo: syncthing/llama-cpp
  full `netpol.yaml` in overlay resources; lldap wired `patches:` entry with
  `target:`. Full classification + deletion checklist:
  `references/structural-audit.md`.

```bash
# all 36 tailnet overlays render; every HTTPRoute hostname is a clean FQDN
for d in apps/*/overlays/nishir-tailnet apps/*/*/overlays/nishir-tailnet; do
  kustomize build "$d" | awk '/kind: HTTPRoute/{f=1} f&&/hostnames:/{h=1;next}
    h&&/^  [a-z]/{h=0} h&&/- /{print FILENAME": "$0}' FS=: FILENAME="$d"
done | grep -- '- -'   # must be empty
```

Plus: `nix fmt` before commit (treefmt normalizes the inline block indent);
commit trailers Signed-off-by + Co-authored-by per repo .gitlint CC1.
