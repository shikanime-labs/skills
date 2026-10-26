# Branch protection is ruleset-based, not classic

Classic endpoint returns 404 on ruleset-backed repos.
1. `gh api repos/<org>/<repo>/rulesets` → id + name.
2. `gh api repos/<org>/<repo>/rulesets/<id>` → `.rules[]` array.
Gates to read: `pull_request.required_approving_review_count`, `required_status_checks` (list), `required_signatures`, `required_linear_history`, `merge_queue` (merge_method), `deletion`.
