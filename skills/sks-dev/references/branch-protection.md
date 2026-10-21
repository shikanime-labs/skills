# Branch protection detection (rulesets, not classic)

Loaded by `sks-dev` when probing whether `main` is protected, or a push or
merge is rejected by protection:

- The classic endpoint
  `gh api repos/<org>/<repo>/branches/main/protection` returns 404 on
  ruleset-backed repos, which misleadingly reads as "not protected". Detect
  via RULESETS instead — and the list endpoint omits the rules, so fetch
  each ruleset id:

  ```bash
  gh api repos/<org>/<repo>/rulesets -q '.[] | "\(.id)  \(.name)"'
  gh api repos/<org>/<repo>/rulesets/<id> -q '.rules[]'
  ```

- A `pull_request` rule with `require_code_owner_review` (an org
  "Landing protections" ruleset — org examples: `sks-context`) blocks
  self-approval — that is what forces
  `gh pr merge --squash --admin` once approval is given (org approval
  practice: `references/shikanime.md` when operating in a shikanime org).
- Gitlint-enforced repos (org classes: `references/shikanime.md` when
  operating in a shikanime org): CC1 rejects any commit without
  `Signed-off-by` (full envelope:
  `references/manifests-git-commit-pitfalls.md`).
