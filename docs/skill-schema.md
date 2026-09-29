# Skill Schema

<!-- owner: shikanime-labs | zone: internal | purpose: the SKILL.md frontmatter contract every catalog skill follows -->

Every `skills/*/SKILL.md` opens with an identical frontmatter block. All
34 skills declare all fields.

## Frontmatter fields

| Field | Value in this catalog |
| --- | --- |
| `name` | Skill identifier, matches the directory name and the `sks-` prefix convention. |
| `description` | One `Use when ...` sentence: the trigger condition first, then the scope. This is what a model matches against. |
| `version` | Semver of the skill itself, bumped on behavior change. |
| `author` | `Hermes Agent`. |
| `license` | `Apache-2.0`. |
| `metadata.hermes.tags` | Free-form lowercase keywords used for search. |
| `metadata.hermes.related_skills` | The dependency edges — see below. |
| `platforms` | Runtime constraints (OS, tools) when they apply. |

## `related_skills` — the dependency edges

Each entry names a skill that continues or serves this one's flow. Edges are
direct hand-offs only: declare the next step, not the whole transitive
chain. The rendered graph lives in
[skill-graph.md](skill-graph.md).

### External references

An edge may point outside the catalog only when the target is:

- a Hermes built-in skill (for example `requesting-code-review`,
  `github-code-review`, `github-workflow-generation`), or
- a well-known library skill (the `caveman-*` and `ponytail-*` families).

Currently referenced:

- `caveman-compress`
- `caveman-review`
- `github-code-review`
- `github-workflow-generation`
- `ponytail-audit`
- `ponytail-review`
- `requesting-code-review`

Anything else belongs in this catalog or should not be an edge.
