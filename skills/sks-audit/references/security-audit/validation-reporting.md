# Validation and Reporting

Read this before the validation phase and again before writing reports.
It carries the verifier prompt contract, the findings shape, and the
report structure.

## Candidate Validation

Give each unique fingerprint to a fresh verifier that did not hunt it.
Its job is to refute the candidate:

1. Verify every trace location, line, scope, and description; the first
   entry must be a real lower-trust entrypoint and the last the claimed
   sink or boundary effect.
2. Reconstruct the strongest source-visible validation, identity,
   authorization, normalization, lifecycle, and containment controls on
   the path — not just the ones the hunter cited.
3. Independently reproduce the minimum observed result when possible:
   inputs, interface shape, conditions, affected dummy principal. Do not
   infer a stronger result or continue past it.
4. Check that likelihood, impact, confidence, and the proposed fix match
   only what the evidence establishes.
5. For a `needs_validation` proposal, decide whether the blocker is
   genuinely outside source and local observation. Source refuting the
   trace rejects it; a still-decisive missing fact keeps it, with exact
   local and owner-observed plans.
6. Preserve the fingerprint for the same source-derived root cause across
   every state.

A verifier promotes `needs_validation` to `confirmed` only after
independently establishing the complete path and bounded observed result;
demotes a proposed confirmation when a specific deployment or runtime
fact remains unknown; rejects when source, local behavior, a visible
control, missing meaningful impact, or an impossible prerequisite refutes
the claim. `needs_validation` is never a parking place for a speculative
idea.

A material replacement — a stronger verdict, a changed root cause, trace,
input, observed result, impact, or severity — is applied only after
another fresh verifier accepts it; if independence or budget is
unavailable, the disputed record leaves `findings.json` and its unit
stays an unresolved candidate with the run recorded incomplete. Wording
and line-number corrections apply directly.

## Findings Shape

`findings.json` is an array of records, one per fingerprint, sorted by
fingerprint. Each record carries `fingerprint`, `title`, `description`,
`verdict`, and repository-relative `trace` and `evidence` paths, plus the
fields its verdict contract in the skill body requires. Validation-plan
`deployment` steps are owner-observed checks, never requests to probe a
live target. Keep prose and JSON in agreement: the report is derived from
the records, never the reverse.

## Report Structure

`REPORT.md`, derived only from the final records and the coverage plan:

1. Scope header: run profile, source ref, execution statement, prior-run
   use, deferred and out-of-scope coverage. A scoped, quick, or
   incomplete run states plainly that it is a partial pass; an incomplete
   run lists every unvalidated fingerprint.
2. One short security posture summary.
3. A confirmed-findings table: severity, title, boundary, one-line
   observed result.
4. Each confirmed finding: source location, lower-trust principal,
   target-native reproduction, conditions, actual result, impact,
   priority rationale, smallest source fix.
5. A separate needs-validation table: title, trace, exact blocker,
   bounded local next step, safe owner-observed check — no severity, not
   called vulnerabilities.
6. Hardening notes and positive source patterns.
7. Coverage summary: unit counts by status, important exclusions, critic
   result.

Rejected records are never findings; mention a fingerprint only when it
explains a prior disagreement or coverage decision. HTTP is one possible
native interface, not the default — a library finding uses a function
call, a parser a fixture, a CLI a command, infrastructure a rendered
policy. Keep the report proportional to the evidence: a clean run has
zero confirmed records and says so without inventing low findings.
