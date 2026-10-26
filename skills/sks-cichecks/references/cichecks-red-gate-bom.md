# cichecks-red-gate-bom.md

Flaky-red CI gate whose failing job log is a single line:
`invalid character '\ufeff' looking for beginning of value` (Go's
`encoding/json` parse of a BOM-prefixed file).

## When to Use
- A `gh pr checks` / `gh run` gate is `failure` (not `skipped`) and the first
  failing job's log is exactly `invalid character '\ufeff' ...` — a Go
  `encoding/json` parse on a BOM-prefixed file.

## Pattern to apply
1. Byte-scan the checkout: count files whose first 3 bytes are `EF BB BF`
   (UTF-8 BOM). A clean checkout is 0.
2. If the count is 0, the BOM lives in the nix/CI build state (cached flake
   input, devdev shell, generated JSON in the store) — not in any PR file.
3. Classify as a pre-existing/infra failure.

## Fix
1. Clear / regenerate the nix store or a cached flake input.
2. Re-run the gate.
3. If it still fails, trace the dependency that actually failed (downstream
   job is a symptom).

## Classification
- JSON parse on a BOM = infra/pre-existing failure. Do not diff against, or
  code-fix, the PR.