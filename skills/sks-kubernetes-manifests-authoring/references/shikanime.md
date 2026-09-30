# Shikanime org conventions

Read this when authoring manifests in a shikanime-org repo. The skill body
is generic; these are the org instantiations.

## Hostname zones

- `overlays/<cluster>/` owns `*.i.shikanime.studio`.
- `overlays/<cluster>-tailnet/` owns `*.taila659a.ts.net`.
- Hostnames never duplicate across flavors; the tailnet overlay is the
  flavor overlay for tailnet-only exposure.

## Label set

Tailnet overlays carry the five-key `app.kubernetes.io` label set with
`includeTemplates: true`.

## Monitoring CRDs

The fleet uses VictoriaMetrics CRDs: `vmservicescrape.yaml` for scrape
config and `vmrule.yaml` for alert rules, under `components/monitoring/`.

## Sizing

PVC sizes are taken from measured live-cluster usage before the PR
(`references/live-cross-check.md`); the user sizes from the live cluster.
