# nixpkgs release calendar

Live source of truth — re-read every cycle, dates move:

- NixOS 26.11 release schedule: <https://github.com/NixOS/nixpkgs/issues/567567>

## Snapshots

| Release | Code name | Ship date  | Branch-off |
| ------- | --------- | ---------- | ---------- |
| 26.05   | Yarara    | 2026-05-30 | shipped    |
| 26.11   | Zokor     | 2026-11-23 | 2026-11-16 |

26.11 gates already passed at snapshot time: breaking changes restricted to
Release Critical packages (2026-10-12); all breaking changes restricted from
2026-10-26. 26.05 is the last release supporting `x86_64-darwin` (EOL end of
2026).

## Reading the cycle

- Milestone `due_on` = the release date (26.11 → `2026-11-23T12:00:00Z` —
  midday UTC anchor; midnight anchors a day early in western timezones,
  GitHub keeps the date only).
  Work that must ride the release lands before branch-off — treat branch-off
  as the real freeze for module-carrying repos (machines, manifests).
- Cadence: two releases a year (`YY.05` / `YY.11`), named release managers
  per cycle; the next cycle's schedule issue opens with the feature-freeze
  discussion, ~8 weeks before ship.
- After branch-off, upstream fixes ride the `release-26.11` backport
  workflow; a flake bump past branch-off targets the NEXT release.
