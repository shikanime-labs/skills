# CPN Discussion — GraphQL details

Load lazily from SKILL.md as needed.

## House structure (French)

Match sibling discussions (#2467, #2474):

```markdown
## Contexte

<1-2 sentences of context; name the PR/issue with a #NNNN link, not a raw URL>

## <Section header>

- bullet points / open questions

## PR liée

#2411
```

A discussion is an **opening**, not a tracked ticket: context + open questions
only. Do NOT add "Décision attendue" / "Définition du fini" — that scaffolding
belongs on issues (cpn-issue). Keep it short.

## Update a discussion body

`gh api graphql --input /tmp/disc_input.json` where `/tmp/disc_input.json` is:

```graphql
mutation ($id: ID!, $body: String!) {
  updateDiscussion(input: { discussionId: $id, body: $body }) {
    discussion {
      number
      title
    }
  }
}
```

Variables via `--input`: `{"id": "D_kwDOHpbzm84AoamW", "body": "..."}`

## Create a discussion

`createDiscussion` requires `repositoryId`, `categoryId`, `title`, `body`:

```graphql
mutation {
  createDiscussion(
    input: { repositoryId: $r, categoryId: $c, title: $t, body: $b }
  ) {
    discussion {
      number
    }
  }
}
```
