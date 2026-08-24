# Review Doctrine

Shared review doctrine for `sk-code-review` and `cpn-code-review`.

## The standard

Approve when the change definitely improves overall code health, even if not
perfect. There is no perfect code, only better code. Never approve a change that
worsens code health; never block for days seeking polish. Technical facts and
data overrule opinions and personal preferences. Design decisions are almost
never "just style" — weigh them on principles; if the author can show two
approaches are equally valid, accept the author's. Otherwise the fallback is
consistency with the existing codebase.

## What to look for, in priority order

1. **Design** — do the pieces interact sensibly; does the change belong here or
   in a library; is now the right time.
2. **Functionality** — does it do what the author intended, and is that good for
   users; think edge cases and concurrency (races/deadlocks are found by
   reading, not running).
3. **Complexity** — "too complex" = cannot be understood quickly, or invites
   bugs when modified. Over-engineering (speculative generality,
   future-proofing) is a defect: solve the problem that exists now. Classic
   smells: parameter sprawl, leaky abstractions, nested conditionals,
   stringly-typed code, redundant state.
4. **Tests** — added in the same change; will they actually fail when the code
   breaks; simple, useful assertions; tests are maintained code too — no
   complexity pass for tests.
5. **Naming** — long enough to communicate, short enough to read.
6. **Comments** — explain why, not what; if code needs a what-comment, simplify
   the code instead.
7. **Good things** — say what was done well; praise with a why is mentoring, and
   reinforces the practices you want repeated.

## Comment mechanics

- Be kind; comment on the code, never the developer.
- Explain why; balance pointing out problems with giving direction — but fixing
  is the author's job, not the reviewer's.
- Label severity on every comment (Nit / Optional / FYI or the label table) so
  authors can prioritize; unlabeled comments read as mandatory.
- An explanation that lives only in the review tool helps nobody — ask for
  clearer code or a why-comment in the code itself.
- Approval-with-comments is legitimate when remaining comments are minor,
  optional, or trusted to be addressed.
- Prefer questions over verdicts when unsure ("What happens if `items` is
  empty?" beats "This will fail on empty input"), and suggestions over commands
  ("async/await might read cleaner — thoughts?" beats "You must use
  async/await").

## Automation boundary

Never spend human review on what a tool owns: formatting, import order, lint
violations, typos — route those to the linter and say nothing. Review budget
goes to logic, security, design, tests, and naming. If a formatting rule is
missing, fix the config, not the PR.

## Reviewer discipline

- Read-only review: never mutate the working tree or commits to review; use
  `jj diff`/`jj log`/`jj show`, or a separate workspace.
- One review seat: the reviewer does not dispatch further reviewers; if the diff
  is large, review in passes and say so.
- Plan alignment first: implementation vs stated intent; flag deviations
  explicitly; if the plan itself is wrong, say that.
- Calibration: not everything is critical; acknowledge strengths before issues;
  be specific (file:line); never review code you did not read; always give a
  clear verdict.
- Tests verify real behavior, not mocks; check production readiness — migration
  strategy on schema change, backward compatibility.

## Speed

Respond within one business day; fast individual responses matter more than fast
total processing. Ask for large changes to be split into a stack rather than
reviewing one huge diff (rule of thumb: over ~400 changed lines, request a
split). Never trade standards for imagined velocity.
