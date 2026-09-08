# sks-dev-workflow — Pitfalls

## Dual-clone discipline (`.hermes/skills` vs `~/Source/Repos`)

The shikanime-labs/skills repository exists in two working clones:

- **Operational clone** — `~/.hermes/skills/` (read by `skill_view`, `skills_list`,
  and the live agent at runtime). This is what Hermes loads when you invoke a
  skill.
- **Source-of-truth clone** — `~/Source/Repos/github.com/shikanime-labs/skills/`
  (the canonical git repo where PRs are opened).

**Editing the wrong clone silently no-ops**: changes made in
`~/Source/Repos/...` are invisible to the running agent until they are either
pushed and pulled into `.hermes/skills`, or copied across. The reverse is also
true — local edits in `.hermes/skills` are lost on the next fetch/pull cycle.

Always verify which clone `skill_view` resolves to (check the `_source_path`
field in its output) before patching a skill's SKILL.md or evals. After editing
the source-of-truth clone, copy modified files to the operational clone (or push

- pull) so the agent sees the change immediately.

## Reused branch names land on wrong `@`

Reusing branch names across isolation sessions can land commits on the wrong
revset (`@`), especially when a previous session's working tree was not fully
cleaned. Before staging/committing: verify
`git branch --show-current` and `git log --oneline -5` against `origin/main`.
`git checkout` can silently switch between branches when working trees overlap.
Re-isolate (`jj reset --hard origin/main`) if the target is wrong.

## `git checkout <path>` wipes untracked new files

In a jj-repo, `git checkout origin/main -- .` reverts tracked files but also
destroys any untracked files that were committed in a prior session. Use
`jj reset --hard origin/main` followed by targeted file restoration instead.

## Uncommitted working-copy clutter from prior sessions

In jj repos, working copies can accumulate changes from interrupted sessions,
parallel agents, or formatters that ran on files outside scope. When starting
a new task in an existing working copy, run `jj status` first. Uncommitted
changes that are NOT part of the current task risk being accidentally included in
a `jj squash` or `jj describe`, polluting the commit with unrelated files.

The correct isolation pattern for a new task in a dirty working copy:

1. `jj log --limit 3` — confirm current bookmark and parent.
2. `jj diff --stat` — see what's dirty.
3. If the dirty files are from prior sessions (e.g. `.github/workflows/*.yaml`
   from a `ef8ebb2a` pinact formatter commit), apply ONLY your task's files via
   targeted `jj restore` / file write; do NOT `jj squash` the working copy
   into the parent — that merges everything.
4. Verify: `jj diff --name-only` shows only task-scoped files before committing.

## `jj squash` into an immutable branch

`jj squash` fails with "commit is immutable" when the parent (e.g. `main`)
is protected or immutable. The correct recovery:

1. Move the bookmark to the working copy commit: `jj bookmark set <branch> -r @`.
2. Set the commit description: `jj desc -r <hash> -m "<message>"`.
3. Push: `jj git push --remote origin --bookmark <branch>`.

Do NOT abandon the old commit if it's already pushed — that creates divergence
on the remote. The moved bookmark covers the intent.

## jj working-copy → bookmark mismatch after squash-abandon

`jj squash` into a parent that was itself an ancestor of a previously-abandoned
bookmark can orphan the bookmark. After `jj abandon` of a commit that had a
bookmark, the next `jj squash` into the parent may silently move that bookmark
to the working copy instead of the intended target. Verify bookmark location
with `jj bookmark list` before and after every push.

## Recovering working-copy state after `jj abandon`

When a commit with important working-copy changes is accidentally abandoned
(e.g. `jj abandon -r <commit>` without recording the hash first), the changes
are NOT lost immediately — they remain accessible via the git reflog. Recovery:

1. Find the abandoned commit hash: `git reflog --all | grep <description>`
   or check `jj log --limit 5` (abandoned commits remain visible briefly).
2. Restore from it: `jj restore --from <hash>`
   This re-applies the tree state from that commit into the current working copy.
3. Commit with explicit file list using `jj commit <file1> <file2> ...`
   to avoid picking up foreign files from prior sessions or parallel agents.
4. Set the bookmark: `jj bookmark create <branch> -r @`

The explicit-file-list commit pattern is safer than `jj squash` when the
working copy may contain files from parallel agents — it commits only the
intended files regardless of what's dirty.

## GitHub additions count is real — never call it "context"

A PR's `+N` additions figure is actual added lines, not GitHub diff padding.
When a user reports `+380-27` on a PR you called "clean", recheck instead of
defending: `jj diff -r @ --git --stat` (vs base, not vs the old branch) and
`git diff base...head --stat`, then compare the changed-file list against the
PR's stated intent. A large rewrite of one file (e.g. a 49-line config growing
to 402) inside a PR titled for a small change is scope creep — split it out
with a revert PR that keeps only the intended hunks. The `configuration.nix`
machine-template migration rode along this way and needed a revert after merge.

## Bash aliases in prose (`$K`, `jj`, etc.)

Shell aliases defined in `AGENTS.md` or the user's shellrc (e.g. `$K` for
`kubectl --context nishir-k8s-operator.taila659a.ts.net`) are expanded by
the shell in code fences, but NOT in raw prose. When writing a PR body or
commit message with code examples, use the full command or a clear note that
the alias must be substituted. Prefer expanded commands — they are more
readable for reviewers who do not share the alias definition.

Example (body prose — should be expanded):

```text
Use `$K -n longhorn-system get pods` to check pod health.
```

→ use:

```text
Use `kubectl --context nishir-k8s -n longhorn-system get pods` to check pod
health. (Context shortened here; the rule is: spell out the full command.)
```

Code fences are fine with `$K` — the alias is expanded by the shell at run time.
Prose is NOT — it is shown as literal text to the reader.

## Recovering from missing CLI tools (brew on macOS)

A `command not found` error on macOS is almost always a missing Homebrew
package. The recovery pattern (verified on `honcho`, `gh`, `jj`, etc.):

1. **Identify the package:** `brew search <tool>` (e.g. `brew search honcho`)
or `which <tool> 2>/dev/null` to confirm absence.
2. **Install:** `brew install <package>` — the formula name is usually the tool
name (e.g. `honcho`, `gh`, `jj` for `jj` on macOS). Some tools use formula
names that differ from the binary (e.g. `git` → `git` package; check
`brew info` for the exact formula name when ambiguous).
3. **Verify:** `<tool> --version` or `which <tool>`.

On Linux, try `apt list --installed 2>/dev/null | grep <tool>` or
`which <tool> 2>/dev/null`; if absent, `sudo apt install <package>`.

**Do NOT add installation instructions to skill bodies or session memory.**
Environment-dependent failures (missing binaries, fresh-install errors,
post-migration path mismatches, unconfigured credentials) are transient
and per-machine. A skill that teaches "if X is missing, install Y" hardens into
a persistent self-imposed constraint that breaks when the environment changes
or the tool is pre-installed. The recovery recipe is already short enough to
run each time — document the pattern in pitfalls or a session note, not a
skill instruction.

## `gh pr create` stdout is empty when PR is created

`gh pr create` with `--body` as a JSON argument (e.g. via `json.dumps()`) may
return empty stdout while the PR is created successfully. The graphql error
"A pull request already exists" can also appear as the only output.

- If `gh pr list` confirms the PR was created despite empty stdout, the
  operation succeeded. Do not retry.
- For CI-triggered PRs (e.g. `manifests` repo where CI does not auto-trigger
  on PR open), after `gh pr create` confirm CI runs via
  `gh run list --branch <branch> --repo <org>/<repo>`. If empty, trigger
  manually: `gh workflow run Integration --ref <branch>` then
  `gh run watch --exit-status`.

## GitHub issue/PR bodies are free text — never 80-column wrap

The user corrected a recurring defect: agents wrapped issue/PR body text at
~80 columns (hard line breaks every N chars), producing awkward GitHub bodies.

Root cause: the global "wrap Markdown at 80 columns" rule in `AGENTS.md` and
the `sks-dev-workflow` Formatting section reads as applying to ALL markdown,
including GitHub bodies. It does NOT — committed repo Markdown (SKILL.md, docs,
README) wraps at 80; GitHub issue/PR bodies are free text.

Escape (per `sks-issue`, `sks-pr`, `cpn-issue`, `cpn-pr`):

- Write issue/PR bodies as natural prose paragraphs — no line wrapping, no hard
  line breaks at a column width. A blank line separates paragraphs; everything
  else renders as-is.
- Never run `nix fmt` / `mdformat` over a body; those tools enforce an
  80-column wrap that does not belong on GitHub.
The `## What`/`## Why`/`## References` (PR) and `## Problem`/`## Acceptance`
(issue) headings are the only structure; the paragraph text under them stays
unwrapped.

## Kustomize ConfigMap/Secret not found — generator not in active overlay

An overlay references a ConfigMap/Secret by name (volume mount, `envFrom`,
`valueFrom`) but the `configMapGenerator`/`secretGenerator` producing it
lives in a DIFFERENT overlay. When overlays stack (`base → nishir →
nishir-tailnet`), generators in a parent are invisible to the child unless
the child redeclares them. The pod fails:

```text
MountVolume.SetUp failed for volume "X" : configmap "Y" not found
```

Diagnosis: (1) which overlay does Flux reconcile (`ks.yaml` → `path:`)?
(2) find the reference in the render (`kubectl kustomize <path>`); (3) grep
that overlay chain's kustomizations for a generator with that name; (4) if
absent, add one in the ACTIVE overlay. Generators in a parent produce
`<name>-<hash>` names a child cannot reference by short name — generate in
the same overlay that consumes, or rewrite the reference via patch. Pin the
image while there:

```yaml
configMapGenerator:
  - name: <name>                    # matches the Deployment's volume/secretRef
    files:
      - <config-file>
images:
  - name: <image-name>
    newName: <registry>/<repo>
    newTag: <tag>@sha256:<digest>
```

## Two `patches:` blocks in a kustomization (app overlays)

App overlay kustomizations often carry TWO separate `patches:` entries — one
for routing (`patches-httproute.yaml`), one for network policy
(`patches-netpol.yaml`). Do NOT merge them into one block: two map keys
named `patches:` is a YAML duplicate-key error. Correct shape:

```yaml
resources:
  - ../nishir
  - gatewayclass.yaml
namespace: shikanime
patches:
  - path: patches-httproute.yaml
patches:
  - path: patches-netpol.yaml
    target:
      name: <app>
      kind: NetworkPolicy
```

(This is distinct from a single `patches:` entry in other files; the pitfall
is app overlays where routing and networking patches coexist.)
