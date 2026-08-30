# Relabeling

Distilled from <https://docs.victoriametrics.com/victoriametrics/relabeling/>
Reference: <https://docs.victoriametrics.com/victoriametrics/relabeling/>

## Three stages (order matters)

1. **Service Discovery relabeling** — `relabel_configs` in `-promscrape.config`, during SD before scraping.
   - `global.relabel_configs` → all targets; `scrape_configs[].relabel_configs` → that job.
   - Add/remove/update target labels, or drop targets.
2. **Scraping relabeling** — `metric_relabel_configs` (v1.106.0+), after scraping, on individual metrics.
   - `global.metric_relabel_configs` → all metrics; per-job variant → that job's metrics.
   - Filter/modify series before they hit the TSDB.
3. **Remote Write relabeling** — in vmagent, after metric_relabel, before send to `-remoteWrite.url`:
   - `-remoteWrite.relabelConfig` (all metrics, any source) — view at `http://vmagent:8429/remotewrite-relabel-config`.
   - `-remoteWrite.urlRelabelConfig` (per-destination) — view at `http://vmagent:8429/remotewrite-url-relabel-config`.
   - Useful for routing subsets to different backends (e.g. `env=prod` → prod cluster).

## VM enhancements over Prometheus

- `replacement: "{{label_name}}"` builds values from existing labels (e.g. `{{instance}}-{{job}}`).
- `if: '<series selector>'` — apply action only to matching samples (single or list; OR semantics). e.g. `if: 'node_memory_MemAvailable_bytes{instance="host123"}'` + `action: keep`.
- `regex` may be a multi-line list (auto-OR-combined).
- New actions:
  - `replace_all` — replace all regex matches in `source_labels` with `replacement` (e.g. `-` → `_` in `__name__`).
  - `labelmap_all` — rename labels by regex on label name.
  - `keep_if_equal` — keep entry only if all `source_labels` equal.
  - `keep_metrics` / `drop_metrics` — by metric name regex.

## Tips

- `__`-prefixed labels (e.g. `__meta_*`, `__address__`, `__scheme__`) are temporary; removed after relabeling. Use them as scratch during target relabeling.
- All target labels are added to scraped metrics automatically.
- **Debug**: vmagent `http://vmagent:8429/targets`, `/service-discovery`, `/metric-relabel-debug`; single-node `http://victoriametrics:8428/targets`, `/service-discovery`.
- Dropping too many labels can collide distinct series into one (duplicate/conflicting values) — watch for that.

## When to load this

Load when writing relabel configs (drop labels, route by tenant/env, rename), or debugging why targets/metrics are missing.
