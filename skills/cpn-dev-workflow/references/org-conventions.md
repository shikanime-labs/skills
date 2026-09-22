# cpn-dev-workflow — conventions d'org (cloud-pi-native / console)

À lire quand vous travaillez dans le dépôt console cloud-pi-native.

## Checkout et layout

- Checkout local : `~/Source/Repos/github.com/cloud-pi-native` ; dépôt
  `console` ; commandes lancées depuis `console/`.
- `console/README.md` — overview, architecture, ports, run modes.
- `console/CONTRIBUTING.md` — scope, backend target, quality gates.
- `console/package.json` — workspace scripts : lint, test, build, docker.
- `console/.github/PULL_REQUEST_TEMPLATE.md` — sections de PR requises.
- `console/apps/server-nestjs` — backend cible actuel ; `console/apps/server` —
  historique, **ne pas modifier** (frozen ; contributions rejetées, y compris
  bug fixes).
- `console/misc/plugins.md` — cycle de vie des plugins ;
  `console/playwright/README.md` — e2e Playwright.

## Toolchain et commandes

- Docker >= 27 (compose >= 2.35, buildx), Node.js >= 24, pnpm >= 10.
- Install/build/generate : `pnpm install`, `pnpm build`,
  `pnpm --filter @cpn-console/server-nestjs run db:generate`.
- Lancer : local+remote → `pnpm run dev` puis
  `pnpm --filter @cpn-console/server-nestjs run dev` +
  `pnpm --filter @cpn-console/client run dev` ; full containerisé →
  `pnpm run docker:dev` ; intégration → `pnpm run docker:integ` ou
  `pnpm run integ`.
- Checks avant soumission : `pnpm lint`, `pnpm test`, `pnpm playwright:test`
  si un parcours est touché.

## Identité et PR

- Author identity des commits :
  `William Phetsinorath <william.phetsinorath-open@interieur.gouv.fr>`,
  signés SSH.
- Origin-only : push `origin` (`cloud-pi-native/*`), PR avec
  `--head cloud-pi-native:<branch>`.
- Husky `pre-push` lance `vitest` : les tests unitaires doivent passer avant
  `jj git push`.
