# Commute-aware rental reranker (recipe)

Depth for building a daily sweep/cron that reranks rental listings by commute.
SKILL.md carries the gates; this carries the machinery.

## Architecture (agent/script split)

1. Agent step: `web_extract` each portal search page (trovit slugs), distill
   EVERY listing into JSON:
   `[{"price":int,"rooms":int,"area":float,"addr":"street + postal + city","meuble":bool,"url":str,"title":str}]`.
   Skip colocation / location de vacances / bail civil. Validate postal codes
   (93xxx / 92240 — reject 974xx overseas twins).
2. Script step (deterministic, no LLM): geocode each addr → QPV
   point-in-polygon → commute estimate per destination → weighted score →
   dedupe against a persistent seen-list → print top-N digest. Agent
   sanity-checks top rows and formats the post.

Reason: prices with narrow spaces ("1 140 €") and prose addresses break naive
regex; the LLM is the better parser, the script the better calculator.

## Geocoding

- Primary: BAN `https://api-adresse.data.gouv.fr/search/?limit=1&q=<addr>`.
  DNS to data.gouv hosts can flap — retry ×3 with backoff, then fall back to
  Nominatim (`format=json&countrycodes=fr`). Fallback returns fuzzier
  matches: prefer BAN when it answers.
- Station coordinates: from Wikipedia/wikidata P625 only (see pitfall in
  SKILL.md). Keep a hardcoded dict
  `{'m12_FrontPop': (48.90694, 2.36583), ...}` with a comment naming the
  source.

## QPV (priority-quartier) filter

- Dataset zip (extract only the `*WGS84*` member; lambert-93 members are
  useless for lat/lon point-in-polygon):

  ```text
  https://static.data.gouv.fr/resources/quartiers-prioritaires-de-la-politique-de-la-ville-qpv/20260115-204323/qpv-2024-geojson.zip
  ```text

- Filter features to the region's department prefixes once and save the
  subset (IDF subset ≈ 1 MB vs 8 MB national) next to the script in
  `~/.hermes/cron/state/`.
- Ray-casting point-in-polygon over Polygon/MultiPolygon outer rings is
  sufficient at city scale. `insee_com` may hold comma-joined codes for
  multi-commune zones — match by name or geometry, never equality.

## Commute model

For each destination, minimize over stations within ~1600 m walk:
`total = walk_m/75 + changes × 4 + ride_min` (+2 min station-to-door buffer
per destination).
Ride profiles per line are lookup tables, e.g. toward a line-6/12
destination: m12 direct ≈ 23 min, m6 direct ≈ 12, m13 = +1 change at
Montparnasse ≈ 27, m14 = 2 changes ≈ 30. Calibrate ride times once per
corridor from the transit authority's journey planner, then hardcode.
Banned line: list its station coords; if a listing's banned-line station is
the nearest realistic entry, subtract a penalty and flag the listing in the
digest.

## Scoring (weights that encode user priorities)

- Budget tiers: ≤ceiling +40, ≤ceiling+100 +25, ≤ceiling+200 +10, above −20
  (outliers allowed only if exceptional: ≥70 m², zero fees, DPE A/B, or
  perfect commute).
- Rooms: T4 +35, T3 +28, smaller = outlier class +5.
- Area: `min(area, 95)/3` (caps the bonus).
- QPV hit: −50 (hard drop unless genuinely exceptional — say why if kept).
- Daily commuter's total: ≤25 min +45, ≤30 +35, ≤35 +20, ≤40 +8, else −5;
  zero-transfer +8.
- Occasional commuter (e.g. weekly): ≤30 +15, ≤35 +8, else +2 — LOW weight
  by design.
- Banned-line dependency −10; furnished +3.

## Cron wiring

- Schedule daily off-peak (e.g. `30 7 * * *`), deliver to the originating
  thread, restrict toolsets to web+terminal.
- Dedupe key: `(price, rooms, round(area), normalized addr[:70])` persisted
  as JSON list of lists in `~/.hermes/cron/state/` (tuples aren't
  JSON-native — coerce on load).
- Script prints `SWEEP_DONE new=N duplicates_skipped=M` + ranked rows; agent
  posts only if N>0 (or a one-line nothing-new note).
- Feed a synthetic inbox of known addresses through the script BEFORE
  scheduling: verify ranking sanity, QPV hits on known zones, and that a
  rerun prints NOTHING_NEW — that validates geocoding, dedupe and scoring in
  one shot.
