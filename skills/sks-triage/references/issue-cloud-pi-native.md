# Cloud-pi-native triage conventions

Load when triaging an issue in the cloud-pi-native/console repository — the
generic procedure in SKILL.md is unchanged; these are the org overrides.

- Default repo: `R=cloud-pi-native/console`. Transfer targets are other
  `cloud-pi-native/*` repos (and, where fitting, `shikanime-labs/*`).
- Artifact language is **French**, close comments included.
- Issue titles carry the template shape: `🐛 [BUG]` → label `bug`,
  `💡 [REQUEST]` → `enhancement`; never set a label outside
  `gh label list`.
- Org projects: `gh project list --owner cloud-pi-native` (Projects v2).
  The main board is `Socle` (project 2); its Status has no `Ready` option —
  the ready equivalent is `To do`. Custom fields worth setting: Epic
  (single-select; e.g. `Migration NestJS`) and two ITERATION fields — `PI`
  (sprints `PI18-2`…) for active cards, `PI-Backlog` (iteration
  `PI-Backlog 18`) for Status=`Backlog` cards. Iterations are set via
  `iterationId` in `updateProjectV2ItemFieldValue`, never
  singleSelectOptionId. Priority (low/medium/high) exists but has no
  derivable default — skip unless asked. When Epic is empty and the title
  carries a clear signal, derive by keyword, most-specific match wins
  (server-nestjs → `Migration NestJS`; rôles/droits/RBAC → `Droits Fins`;
  Grafana/SonarQube → `Observabilité`; OpenCDS → `OpenCDS`;
  test/e2e/recette → `QA`; CI/commitlint/release → `CI/CD`;
  ArgoCD/déploiement → `Gestion des déploiements`); no signal → leave
  empty, never invent. New console issues may auto-land on a
  PI-exploit board in `Backlog` — that card is not the triage target; check
  `gh issue view --json projectItems`, it shows every card.
- A Socle card is a REQUIRED output of issue triage in this org, never a
  skip: when `projectItems` shows no Socle card, add one
  (`gh project item-add`); the generic "skip when ambiguous" exemption does
  not apply — Socle is the unambiguous default board.
- Fallback assignee is the same `yorha-operator` account (see the generic
  `shikanime.md`), still only when it appears in the repo's assignee
  list.
