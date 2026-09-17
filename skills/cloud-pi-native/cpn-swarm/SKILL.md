---
name: cpn-swarm
description:
  À utiliser quand vous distribuez une tâche cloud-pi-native sur un cluster
  d'agents via A2A — routage par capacité, machine et pression runner.
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
platforms:
  - macos
  - linux
  - windows
metadata:
  hermes:
    tags:
      - swarm
      - a2a
      - multi-agent
      - fan-out
      - delegation
      - resource-aware
      - cloud-pi-native
    related_skills:
      - cpn-async
      - cpn-dev-workflow
---

# CPN Org — Essaim d'agents

Distribuer une tâche sur un cluster d'agents via le protocole A2A Hermes
(<https://hermes-agent.nousresearch.com/docs/user-guide/messaging/a2a>). Router
chaque unité par la capacité requise, la machine cible et la pression ressource
live du runner.

Ce skill est un routeur, pas un transport. Il décide _quoi va où_ ; A2A et
`delegate_task` font la livraison. Il ne les remplace pas.

## When to Use

- Une tâche se fragmente en unités exigeant des capacités différentes (modèle,
  outil, permission) ou des machines différentes (GPU vs CPU, isolé vs partagé).
- Le runner est sous pression ressource et les unités doivent être réparties,
  pas empilées.

## When NOT to Use

- Quelques PR sœurs dans un dépôt → `cpn-async` (workspaces jj, pas de cluster).
- Une unité, une machine → `cpn-stack` ; ne pas lancer d'essaim pour une unité.

## Procedure

1. **Activer A2A sur chaque hôte** qui exécutera une unité. Dans `config.yaml` :
   `gateway.platforms.a2a.enabled: true` et un port via `extra.port` ; lister
   les pairs sous `a2a_agents`. Puis `hermes tools enable a2a` sur chaque hôte.
   Entrant : Agent Card à `GET /.well-known/agent-card.json` et JSON-RPC 2.0 à
   `POST /` (`SendMessage`, `SendStreamingMessage` sur SSE, `GetTask`,
   `ListTasks`, `CancelTask`, `SubscribeToTask`, plus CRUD de notifications
   push). Les tâches s'injectent dans la session gateway live (même
   agent/mémoire/outils), clé par `contextId` pour le multi-tour.

2. **Énumérer les unités** avec leurs exigences — tag de capacité (modèle /
   outil / permission), machine cible, poids ressource approximatif
   (cpu/mem/io). Enregistrer la liste dans l'issue liée avant d'envoyer.

3. **Sonder la pression runner** avant d'assigner. Lire la charge live des
   machines candidates ; une unité dont le poids dépasse la marge d'un hôte doit
   bouger ou attendre. Ne jamais co-localiser deux unités lourdes sur un runner
   chargé. Re-sonder avant chaque (ré)envoi, pas une fois au début.

4. **Router chaque unité** par correspondance de capacité → adéquation ressource
   → hôte éligible le moins chargé. L'hôte cible doit être A2A-appelable
   (vérifier sa carte avec `a2a_discover(url)`). Remplacer l'hôte par défaut
   uniquement avec une raison explicite
   (`# ponytail: placement manuel — <raison>`).

5. **Envoyer sur A2A.** Fan une tâche vers chaque pair annonçant une capacité
   avec `a2a_orchestrate(capability, message, mode?)` — modes `all` (toutes les
   réponses), `first` (premier succès), `best` (réponse réussie la plus longue ;
   un fan-out tout-erreur rapporte les échecs au lieu d'en choisir un). Pour une
   unité ciblée unique, `a2a_call(agent, message, context_id?)` (multi-tour via
   `context_id`) ; `a2a_history(context_id, limit?)` rappelle un échange
   précédent. Le parent re-vérifie la gate de chaque enfant via `terminal` avant
   de faire confiance à l'agrégat — les rapports d'enfants ne sont pas des
   preuves.

6. **Réconcilier.** Collecter les résultats, remonter un enfant bloqué comme
   rapport `BLOCKED:` avec preuve, et ne merger que les unités passées.

## Pitfalls

- Router uniquement par capacité en ignorant la pression live empile les unités
  lourdes sur un runner chaud — mesurer la marge, puis placer.
- Traiter le « done » auto-déclaré d'un enfant comme vérifié — re-exécuter sa
  gate dans le parent avant de promouvoir.
- Lancer un essaim pour une unité — `cpn-stack` est l'outil plus petit et
  correct.
- A2A non authentifié ne lie que `127.0.0.1`. Distant : bearer token _et_
  `A2A_HOST`. `A2A_PEER_TOKENS="name:token,…"` définit l'identité par pair. Le
  texte entrant est filtré contre l'injection et ne peut pas atteindre les
  commandes slash opérateur ; les réponses en forme d'identifiants sont masquées
  ; chaque échange est journalisé dans `~/.hermes/a2a_audit.jsonl`. Plafond de
  tours par contexte (`A2A_MAX_PINGPONG_TURNS`, défaut 5) arrête le ping-pong
  agent↔agent. Stdlib uniquement — pas de `a2a-sdk`.

## Verification

```bash
curl --fail --silent --show-error http://<hôte>:9900/.well-known/agent-card.json
# après envoi : chaque unité a un hôte + tag de capacité enregistrés
# pression : re-sonder les hôtes candidats avant chaque (ré)envoi
# réconcilier : gh issue view <N> --repo cloud-pi-native/console
```

Utiliser `a2a_discover` pour valider la carte d'agent ; curl est un remplacement
rapide quand l'outillage A2A est indisponible.

## A2A API (Hermes Agent-to-Agent, v1.0)

L'essaim roule sur l'outillage `a2a` Hermes / serveur JSON-RPC entrant. Activer
dans `config.yaml` (`gateway.platforms.a2a.enabled: true`, port entrant via
`extra.port` ; pairs sous `a2a_agents`), puis `hermes tools enable a2a`.

**Sortant (appeler d'autres agents) :**

- `a2a_discover(url)` — récupère + résume la carte d'agent d'un pair.
- `a2a_call(agent, message, context_id?)` — envoie une tâche, reçoit la réponse
  ; multi-tour via `context_id`.
- `a2a_list()` — pairs configurés, conversations sauvegardées, métriques.
- `a2a_history(context_id, limit?)` — rappelle une conversation A2A passée.
- `a2a_orchestrate(capability, message, mode?)` — fan une tâche vers chaque pair
  annonçant une capacité. Modes : `all` (toutes les réponses), `first` (premier
  succès), `best` (réponse réussie la plus longue ; un fan-out tout-erreur
  rapporte les échecs au lieu d'en choisir un).

**Entrant (être appelable) :** sert la carte d'agent v1.0 à
`GET /.well-known/agent-card.json` et JSON-RPC 2.0 à `POST /` — méthodes
canoniques `SendMessage`, `SendStreamingMessage` (SSE), `GetTask`, `ListTasks`,
`CancelTask`, `SubscribeToTask`, plus CRUD de notifications push. Les tâches
s'injectent dans la session gateway live, clé par `contextId` pour le
multi-tour.

**Sécurité :** pas de token ⇒ liaison `127.0.0.1` seulement (distant : bearer
token _et_ `A2A_HOST`) ; `A2A_PEER_TOKENS="name:token,…"` donne l'identité par
pair ; le texte entrant est filtré contre l'injection et ne peut pas atteindre
les commandes slash opérateur ; les réponses en forme d'identifiants sont
masquées ; chaque échange est journalisé dans `~/.hermes/a2a_audit.jsonl` ;
plafond de tours par contexte (`A2A_MAX_PINGPONG_TURNS`, défaut 5) arrête le
ping-pong agent↔agent. Stdlib uniquement — pas de `a2a-sdk`.

**Test rapide (depuis un autre agent / machine) :**

```bash
curl http://your-host:9900/.well-known/agent-card.json
curl -X POST http://your-host:9900/ -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -d '{"jsonrpc":"2.0","id":1,"method":"SendMessage",
       "params":{"message":{"messageId":"m1","role":"ROLE_USER",
                 "parts":[{"text":"What tools do you have?"}]}}}'
```

## See also

- `cpn-async` — flux parallèles in-repo quand aucun cluster d'agents n'est
  nécessaire.
- `cpn-stack` — isolation d'une unité (l'outil plus petit pour un flux unique).
- `cpn-dev-workflow` — boucle complète ; gate de validation d'hypothèses AVANT
  tout fan-out.
