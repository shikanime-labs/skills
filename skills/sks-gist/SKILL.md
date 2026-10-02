---
name: sks-gist
description:
  Use when a verified command, script, config, or output would be retyped or
  re-derived later — publish it as a gist for DRY reuse and link it from the
  artifact that motivated it.
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - gist
      - github
      - reuse
    related_skills:
      - sks-investigate
      - sks-issue
      - sks-discussion
      - sks-bulk
      - sks-adversarial
      - sks-skill-authoring
platforms:
  - linux
  - macos
  - windows
---

# Gist Reuse

Turn a verified artifact (command sequence, script, config, probe output) into
a secret GitHub gist when it would otherwise be retyped or re-derived, and
link the gist from the issue, discussion, PR, or transcript that produced it.
One-way capture: reusable **content** ships as a gist; a reusable
**procedure** ships as a catalog skill via `sks-skill-authoring` instead.

## When to Use

- An investigation (`sks-investigate`) ends with a runnable script or command
  sequence worth keeping.
- An issue, discussion, or review needs an artifact longer than a comment
  holds (multi-file snippet, log excerpt, config).
- The same snippet is being retyped a second time — that is the DRY trigger.
- A batch run (`sks-bulk`) needs a helper script reachable by URL.

## Procedure

1. **Create** the gist from files; it is SECRET by default — never pass `-p`
   unless reuse requires discoverability:

   ```bash
   gh gist create <file>... -d "<what + when to reuse>" | grep -o '[0-9a-f]\{32\}$'
   ```

2. **Link it** where the motivation lives, full URL: issue or PR comment,
   discussion RFC, or the agent transcript summary. An unlinked gist is
   indistinguishable from a lost one.

3. **Maintain by edit, not re-create** — the URL is stable:

   ```bash
   gh gist edit <id> -a <file>... -d "<updated description>"
   ```

4. **Delete** when superseded (explicit consent required in agent runs):

   ```bash
   gh gist delete <id> --yes
   ```

## Promotion path

- A snippet reused across three or more sessions → author it as a catalog
  skill (`sks-skill-authoring`), grounded in the gist's edit history.
- A one-shot probe → discard instead; a gist nobody links is clutter.

## Pitfalls

- **There is no `--secret` flag** — gists are secret unless `-p`; the
  unknown-flag error is the tell you were about to pass a no-op.
- **Secret means unlisted, not private** — anyone holding the URL reads it.
  Tokens, credentials, and internal hostnames never go into gists.
- **`edit -a` renames the file when the name differs** — a rename changes the
  raw URL any consumer already embeds.
- **`delete` refuses without `--yes`** when stdin is not a TTY — agent runs
  must pass it.
- **`gh search gists` only searches your own gists** and takes no `--limit`;
  it is not a discovery tool.
- The handle in URLs and every subcommand is the full 32-hex id — do not
  shorten it.

## Verification

```bash
gh gist view <id> --files      # file list matches what you published
```

## See also

- `sks-skill-authoring` — promotion path when a snippet becomes a procedure.
- `sks-investigate` — common producer of reusable artifacts.
- `sks-issue` / `sks-discussion` — where gists get linked.
- `sks-bulk` — batch runs consuming a gist-hosted helper.
- `sks-adversarial` — sandbox probes; publish only what survives.
