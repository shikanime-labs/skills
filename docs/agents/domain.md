# Domain Model

The durable substrate for maintainers, humans, and other agents. Keeps
terminology sharp and records the decisions behind the code. `bootstrap`
confirms this layout per-repo; this is the default.

## Layout

Most repos have a single context. ADRs live in `docs/adr/` — one file per
decision:

```text
/
├── CONTEXT.md              ← ubiquitous language / glossary
├── docs/
│   ├── adr/                ← ADR-NNNN-*.md, one file per decision
│   └── agents/             ← domain.md, issue-tracker.md, workflow.md
└── src/
```

If `CONTEXT-MAP.md` exists at the root, the repo has multiple bounded contexts
and the map points to where each `CONTEXT.md` lives.

Create files lazily — only when there is something to write. First resolved term
→ create `CONTEXT.md`. First decision that needs recording → add an ADR in `docs/adr/`.

## CONTEXT.md — the glossary

A canonical term per concept, defined precisely enough that two people can't
mean two things by it. When someone uses a term that conflicts with the
glossary, or a vague/overloaded term, sharpen it and write the resolution down
immediately.

## ADRs — architectural decision records (`docs/adr/`)

One ADR per decision, one file per ADR, in `docs/adr/`: context, the decision,
and consequences. Number files sequentially (`ADR-NNNN-*.md`). An ADR is
immutable once accepted; supersede it with a new ADR file rather than editing
it.

```markdown
# NNNN. <short decision title>

- Status: accepted | superseded by NNNN
- Date: YYYY-MM-DD

## Context

<the forces at play>

## Decision

<what we decided>

## Consequences

<what follows, good and bad>
```

## Consumer rule

Every workflow skill reads `CONTEXT.md` for vocabulary and respects the ADRs in
the area it touches. Specs, tickets, and code use the glossary's terms — not
synonyms invented on the spot.

## Strategic documentation duty

`to-spec` must keep these docs current as the first authoring step, not as an
afterthought: a feature that isn't documented in the glossary and (when
non-obvious) an ADR is not "ready-for-agent". This is what makes the repo
maintainable for future humans and other agents without re-deriving intent from
code.
