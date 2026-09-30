---
name: sks-github-text-authoring
description:
  "Use when writing any GitHub text in the target org's repos — commit message,
  issue or PR body, discussion RFC, review or issue comment. Owns all shared
  prose rules; surface skills handle procedure."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - prose
    related_skills:
      - sks-commit
      - sks-issue
      - sks-pr
      - sks-discussion
      - sks-dev
platforms:
  - linux
  - macos
  - windows
---

# GitHub Text Authoring

Single home for the prose rules every GitHub surface repeats: body
formatting, mention escaping, link hygiene, evidence style, template
detection, and the org identity envelope. `sks-commit` (commit message),
`sks-issue` (issue body/comments), `sks-pr` (PR body), and `sks-discussion`
(RFC) own their surface's structure and procedure; they hand the writing
rules to this skill instead of restating them.

## When to Use

- Writing or editing ANY GitHub text in the org: commit, issue, PR,
  discussion, review or issue comment.
- Reviewing an existing draft against the org's prose rules.

## Universal prose rules (every surface, every repo)

- **Language**: per the org's convention; org specifics (the shikanime
  family's English-everywhere rule and the French console twin) live in
  `references/shikanime.md`.
- **Free text, never wrapped**: GitHub bodies and messages render as-is.
  Never insert hard line breaks at a column width; write natural paragraphs,
  a blank line separates them. NEVER run `nix fmt` / `mdformat` over a body
  or message — those tools enforce an 80-column wrap that does not apply to
  GitHub text. Exception: some orgs' repos require an 80-col wrapped
  commit body — a repo-enforced override, see below.
- **Mention escaping**: a bare `@name` in prose pings that user/team. Wrap
  any literal `@` — NestJS `@Inject(x)`, decorators, config keys — in a code
  span or fenced block; only code disables mention parsing.
- **Full URLs, never `#N`**: bare `#XXXX` and `owner/repo#XXXX` are broken
  on GitHub. Write `https://github.com/<org>/<repo>/issues/N`; cross-repo
  links carry their own owner. One URL per line. A body that leaks a bare
  `#N` is a defect — reject and rewrite before posting.
- **Terse, conclusion first**: lead with the conclusion, back it with cited
  evidence, stop. No nested parentheticals — an aside becomes its own
  sentence. Asides that recur become sections; asides that don't, get cut.
- **Evidence over narration**: cite concrete proof — the exact `- old` →
  `+ new` diff lines, or command output through a fenced block — never a
  prose summary of what the output "shows".
- **Mermaid**: encourage a diagram (`flowchart TD` and friends) when a
  visual aids the reader — GitHub renders Mermaid inline in issue and PR
  bodies. It reinforces the prose, never substitutes for it.
- **Tooling discipline**: NEVER pass a body inline via `--body "..."` /
  `-m "..."` with shell expansion — backticks and `$` get mangled and bodies
  silently truncate or empty. Write to a file, pass `--body-file`, then
  re-read the stored body to verify what landed.

## Per-surface structure (the shape, not the prose)

| Surface       | Owner          | Shape                                                        |
| ------------- | -------------- | ------------------------------------------------------------ |
| Commit        | `sks-commit`   | Plain-English imperative title + trailers                    |
| Issue body    | `sks-issue`    | `# Problem` / `## Acceptance` / `## References` (or template) |
| Issue comment | `sks-issue`    | One subject per comment; findings, not status chatter        |
| PR body       | `sks-pr`       | `# Why` / `## What` / `## References`                       |
| Discussion    | `sks-discussion` | Context + open questions; no acceptance criteria           |

Standard shapes apply when no repo template exists; a template replaces
them and is filled with its own headings verbatim.

Structure is owned by the surface skill. This skill never merges shapes —
an issue body never borrows the PR template and vice versa; that leak is a
defect.

## Templates: detect, then conform

Probe for a repo template before writing any body:

```bash
gh api repos/<org>/<repo>/contents/.github --jq '.[].name' \
  | grep -iE 'issue_template|pull_request_template'   # empty = no template
```

Template found → fetch its content (`gh api ... --jq` + `base64 -d`), fill
every section it defines, keep its headings verbatim, and place the surface's
content (acceptance tasklist, `Related:` links) inside the sections it
offers — never add headings it lacks. No template → the surface skill's
default shape.

## Comment etiquette (issues and PRs)

- One subject per comment; split unrelated findings into separate comments.
- The body stays stable: issue bodies hold the problem statement; findings,
  root-cause, and candidate solutions go in comments. Interim comments are
  deletable after convergence — the conversation ends clean.
- Review-thread replies follow the same rules: address pertinent points in
  the diff, discard non-pertinent ones with a one-line comment, never
  silently.

## Org envelope

- Language per the org's convention; org-specific language rules live in
  `references/shikanime.md`.
- Agent-assisted commits and squash merges carry exactly ONE org co-author
  trailer (the value is an org fact — for shikanime, read
  `references/shikanime.md`); never a self `Co-authored-by:`, never a
  duplicate `Signed-off-by:`.
- `Signed-off-by: <user>` only where a hook/ruleset requires DCO — detect
  per repo; hooks always win.
- Repo-enforced overrides (gitlint, commitlint, PR templates) beat every
  default above. Detect first:

```bash
ls .gitlint .commitlintrc* commitlint.config.* 2>/dev/null
grep -rl "Signed-off-by" .github/ 2>/dev/null
```

## Pitfalls

- A body pasted through a formatter arrives hard-wrapped — reflow before
  posting; GitHub renders the breaks literally.
- `gh pr merge` `-m` flags concatenate, they don't replace: a squash-merge
  message must be passed as ONE clean block (subject + body + trailers) or
  jj `*` bullets and `---------` separators leak into the landed commit.
- Mention pings fire on edit too — escaping `@` after posting is too late
  for the notification, only for the rendered text.
- Auto-generated blocks (CodeRabbit release notes) appended to a body are
  not yours to edit around — write above them, never restructure them.

## Verification

Re-read the stored body/message after every write:

```bash
gh issue view <N> --repo <org>/<repo> --json body -q .body
gh pr view <N> --repo <org>/<repo> --json body -q .body
jj log -r @ --no-graph -T description
```

Confirm: no hard wraps, no bare `#N`, no unescaped `@`, one co-author
trailer, template headings verbatim.

## See also

`sks-commit`, `sks-issue`, `sks-pr`, `sks-discussion` — surface owners.
`sks-dev` — drafting invariants (lifecycle-level).
