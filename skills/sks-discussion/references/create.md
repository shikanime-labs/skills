# Discussion create / update detail

Create or update via the `--input` envelope — **NOT** `-F variables=@file`
(fails: `invalid value`):

```json
{
  "query": "mutation($r:ID!,$c:ID!,$t:String!,$b:String!){createDiscussion(input:{repositoryId:$r,categoryId:$c,title:$t,body:$b}){discussion{number}}}",
  "variables": { "r": "...", "c": "...", "t": "...", "b": "..." }
}
```

Body shape: short — context, the open question(s), affected repos. No acceptance
criteria, no tasklist (that is issue scaffolding). A discussion is a clean
conversation for any reader — human or another agent — not the agent's notebook:
post the open question and the context it needs, never raw reasoning or status
chatter. Interim comments may be deleted once the thread converges.

## Edit / pitfalls

- **Disabled repo → creation 404s.** Probe first (SKILL.md); do not assume
  parity with `cloud-pi-native/console`.
- `-F variables=@file.json` fails; always the `--input` envelope.
- No `gh discussion edit`; body edits go through the `updateDiscussion` mutation
  with the discussion's node `id`.
- Do not write the solution in the discussion — solutions belong to issue
  comments after the issue exists.
- A discussion must NOT be faked as an issue — that collapses the RFC stage into
  the ledger stage.
