---
name: fr-rental-listing-search
description:
  "Use when hunting French rental or property listings: portal access map,
  budget/commute gates, QPV check, and a deterministic rerank pipeline."
version: 2.0.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags: [real-estate, france, web-scraping, research]
    related_skills: [blocked-page-recovery, grounded-citations]
platforms: [linux, macos, windows]
---

# French Rental Listing Search

## When to Use

Searching French property portals for rentals or sales on someone's behalf —
budget/commute constraints, shortlists with links, recurring daily sweeps.
Not for price-monitoring products or news digests.

## Before searching (gates)

- Pin budget semantics FIRST: per-person vs combined, charges comprises (CC)
  vs hors charges (HC). "700€ for 2 persons" can mean 700 total or 700 each
  — a 2x swing flips the viable product class (studio vs T2). Ask or state
  the assumption before the first scrape.
- Do geography before listings: map the destination to metro/RER lines, then
  pick communes on a DIRECT line (no transfer). Employer given by name, not
  address: verify via SIRENE
  (`curl "https://recherche-entreprises.api.gouv.fr/search?q=<name>"`);
  0 hits means ask for the street address, never guess one.
- Multiple commuters: pin who commutes DAILY vs who is remote/occasional
  before choosing a zone — the daily commute anchors the commune, the
  occasional one tolerates a transfer. When priorities change mid-search,
  re-anchor the whole shortlist to the new line.
- Get a market anchor before judging listings: aggregator commune pages
  often print average price per room-count (e.g. "2 pièces moyen 864€") —
  sanity-check the budget against it in the same reply.

## Portal access map (anti-bot reality)

- immo.trovit.fr — best first target: web_extract works (direct curl fails
  from the agent host); aggregates leboncoin/seloger/agency listings with
  price, m², room count, detail URLs. Slug pattern:
  `location-appartement-<N>-pieces-<commune>`.
- leboncoin.fr — blocks curl and often web_extract on search pages. Working
  paths: web_search snippets (price/m²/quartier/ad-URL) and web_extract on a
  single ad `/ad/locations/<id>` (deposit, DPE, charges split). Treat as
  best-effort redundancy beside an aggregator that carries its inventory.
- seloger.com — web_extract intermittent, curl 403, sometimes "410 Gone" —
  retry a URL variant (add `/pas-cher`) instead of giving up.
- bienici.com — JS shell (identical byte size across query params = no
  data). Don't mine it; the guessed internal API 404s.
- le-partenaire.fr — web_extract works; carries DPE per ad. URL shape:
  `/immobilier/location/appartement/<commune>/<cp>` (the longer
  region/dept/…-pieces shape 404s).
- vizzit.fr — web_extract works; `/louer/<commune>/appartement` aggregates
  agency descriptions with transit notes.
- pap.fr — web_extract works; particulier-à-particulier = zero agency fees.
  Prices use dot thousands (`1.300 €`); skip coloc/parking ads;
  neighboring-commune ads bleed in — postal filter catches them.
- Keyless-blocked portals' inventory still flows through the aggregator
  above — probe the aggregator rather than fighting the block.

## Procedure

1. web_search `"<type> location <commune> <budget> euros <portals>"` —
   snippets yield prices + quartiers + ad URLs immediately.
2. web_extract the aggregator search pages for the structured list of the
   target room-count class; parse to a clean JSON array
   (price/rooms/area/addr/meublé/url/title).
3. Deterministic rerank: geocode (BAN + nominatim fallback) → QPV-2024
   point-in-polygon → commute estimate (best station per destination) →
   score → seen-list dedupe. Recipe:
   `references/commute-reranker.md`.
4. Present per listing: price, m², quartier, transit line + travel time,
   direct link. Flag honoraires, DPE E/F/G, bail civil, Pinel caps.
5. Recurring sweep (cron): agent fetches via web_extract and distills to
   JSON; the script does all deterministic math. Failure policy: per-source
   isolation — one dead source never sinks the run, and no listing is ever
   invented.
6. Persist a multi-week hunt in a tracking repo structured like
   enhancement-proposal catalogs: an authoritative criteria section
   (e.g. the repo's `AGENTS.md`), numbered candidate directories
   (`<NNNN>-<slug>/` with a yaml frontmatter file + README per
   proposition, status taxonomy, nothing deleted), `research/` (market
   anchors, transport facts, traps), `visits/`, `decision.md`,
   `automation.md` (job id, sources, pipeline, state paths). The repo,
   not the chat, is the memory. When criteria change, file them in that
   criteria section first, then mirror into the sweep script/prompt.

## Pitfalls

- Ask about quartier reputation? Don't answer on vibes: geocode each
  address, then point-in-polygon against the official ANCT QPV-2024 layer
  (WGS84 file from data.gouv.fr; QPV = state-designated priority quartier).
  State the caveat: QPV is socio-economic, not a crime map — cross-check
  with recent resident reports and visit finalists at night. The WGS84 file
  stores multi-commune codes comma-joined — match by commune name or
  point-in-polygon, not code equality.
- Hard exclusions (banned commune, banned rail line) arrive mid-hunt and
  must live in code, not just the prompt: postal AND commune-name check for
  a banned place; drop listings whose nearest transit is a banned line's
  station — retest with a must-vanish fixture after every change.
- Budget figures drift mid-search (per-person vs total, the ceiling itself
  revised 3x in one thread). Re-confirm the number AND the semantics right
  before presenting a final shortlist, then re-run the cut math.
- Filter by postal code: "Saint-Denis" returns La Réunion (974xx) mixed
  with Saint-Denis 93200 near Paris — same trap for any commune with an
  overseas twin. Always validate the 5-digit code.
- bail civil listings ("bail civil uniquement") cannot legally be the
  résidence principale — exclude even when price and size fit.
- Pinel units carry a statutory tenant income ceiling on N-2 resources —
  check eligibility before shortlisting.
- Many listings require a VISALE/Cautioneo guarantee before a visit — VISALE
  is free via Action Logement; set it up early, it unblocks doors.
- Never geocode metro/RER stations by name: general geocoders return wrong
  features and a 2 km station error silently corrupts every commute
  estimate. Take station coordinates from Wikipedia (fr+en cross-check) or
  wikidata P625, hardcode them in the script.
- Estimate commutes with the best station PER destination, not the single
  nearest station. Sum walk (≈75 m/min) + 4 min per transfer + ride time,
  min over candidate stations within a sane walk cap (~1600 m).
- A line ban is geometric, not textual: encode the banned line's station
  coordinates and test nearest-transit — never string-match itinerary text.
- Split parsing duties: the AGENT reads fetched pages and emits structured
  JSON; the SCRIPT does regex-free deterministic math. Regex-parsing portal
  HTML in python fails silently to `score=None`.
- Cron-job state (seen-lists, geojson subsets, scripts) lives under
  `~/.hermes/cron/state/`, never scratch — scratch is pruned after 24 h.
- Scoring one-off finds through the deterministic ranker outside the
  scheduled run pollutes the dedupe state — back up the seen-list, run,
  restore.
- A hard exclusion judged on a centroid is provisional: street-less
  listings geocode to the commune center, so banned-line drops fire on the
  wrong point. Park centroid-dropped entries for re-check with the exact
  street instead of discarding silently.
- A recurring sweep's digest uses a fixed output contract (title+status,
  Result checkboxes, Evidence one-liners + the raw script summary line,
  References = source URLs) embedded in the cron prompt — free-form digests
  are unreadable across weeks.
- Plan/listing photos shared as chat attachments may not reach the agent:
  pull the CDN URL from the thread, download with curl; if the vision model
  is rate-limited, park the file durably and schedule a one-shot cron just
  after the quota reset.
