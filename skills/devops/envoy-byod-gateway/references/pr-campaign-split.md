# Splitting a mega PR into a per-app stacked PR set

Proven 2026-08-30 in `shikanime-labs/manifests`: one mega migration commit
(152 files, 27 apps) split into 28 stacked PRs (#1953–#1980), each PR one app
(+ one shared-file commit). User preference: campaigns touching many apps are
NEVER one mega PR — split per app so each lands independently.

## Why stacked (not parallel independent branches)

Apps share `configs/…/cert.yaml` and converge on `main`; parallel single-commit
branches would all race on that file. A linear stack means each PR's diff is
exactly its app's files, CI renders the full cumulative state at every rung,
and squash-merging bottom-up shrinks each next PR automatically.

## The workflow (jj)

1. **Keep the mega commit as the source of truth.** Do NOT hand-build per-app
   commits by re-applying files — snapshot/restore + mid-flight abandons caused
   a 117-commit divergence mess. Instead `jj split` the mega commit itself,
   repeatedly, one app per split:
   ```
   export JJ_EDITOR=true   # -m alone would open an editor; JJ_EDITOR=true accepts it
   OUT=$(jj split -r $REM "apps/<app>/overlays/nishir-tailnet" -m "Migrate <app> ...")
   REM=$(echo "$OUT" | grep "Remaining changes" | awk '{print $4}')
   ```
   Semantics: selected files go to a NEW child commit (on top), remainder
   stays at `$REM`. Iterate: each split peels one app out; the remainder
   shrinks. The chain builds under the remainder — final order is
   remainder-first, apps above it. Family dirs split per subdir
   (`apps/mautrix/<name>/…`, `apps/servarr/<name>/…`).
2. **Files that can't be fileset-split** (one shared file, per-app content —
   e.g. a centralized `cert.yaml` with one appended block per app): leave the
   whole file in the final remainder commit and describe it as its own
   "Add …" commit at the TOP of the stack. Per-app cert purity is not worth
   hand-surgery; squash-merge makes it moot.
3. **Verify the split**: `jj diff --from <mega> --to <tip> --summary` must be
   EMPTY (tree identical), and every commit in the chain shows no `conflict`.
4. **Abandon the divergent litter**: repeated abandons/rebases leave parallel
   heads with duplicate descriptions. Find true heads with
   `jj log -r 'heads(<base>::)'`, keep the verified chain, abandon the rest.
5. **Rebase onto fresh main** (`jj git fetch` first — the base PR may have
   merged mid-campaign; `jj rebase -s <chain-root> -d main@origin`), then
   create one bookmark per commit (`migrate/<app>`) and push all with
   `jj git push --remote origin --bookmark migrate/a --bookmark migrate/b …`
   (one `--bookmark` FLAG per ref — you cannot pass `--bookmark a b`).
6. **Open PRs bottom-up**: PR 1 base `main`, PR N base `migrate/<previous>`.
   Every body carries `Closes #<tracking-issue>` (auto-close fires only on the
   last landing — deliberate) plus "Part N of M; base: <branch>". Label all
   `enhancement`+`auto`. Close the superseded mega PR with
   `gh pr close <N> --comment 'Superseded by a per-app PR stack (#…+).'`.
7. **Land in dependency order** (base first). Never launch an auto-merge
   watcher across the stack.

## Pitfalls

- `jj split -r X <fileset>` on an ALREADY-PUSHED commit rewrites published
  history — fine here because the mega PR was being superseded (close it), but
  never do this on a PR someone is reviewing.
- Divergent change-ids (`change/1`, `change/2`) appear after abandons; target
  commits by COMMIT ID (full 40-char when scripting — short ids can collide in
  assembled arg lists), never by change id, during cleanup.
- `jj split -m <msg>` is NOT non-interactive: it forces an editor.
  `JJ_EDITOR=true` is the non-interactive form.
- Check actual disk state before re-dispatching a timed-out subagent — it may
  have done nothing, and redoing its work is cheaper than reconciling partial work.

## Editing files inside PR branches after push (proven loop, 2026-08-30)

To fold a fix into each app's existing PR branch (e.g. correcting a tag on
every `envoyproxy.yaml` after the PRs are open), do NOT trust a scripted
`jj new <bm> → edit → jj squash` loop — mid-loop `jj new` auto-commits stray
working-copy edits into surprise commits, squashes land in the wrong commit,
and divergent bookmark siblings (`bm/0`, `bm/1`) accumulate silently. The
reliable sequence per app:

1. `jj new migrate/<app>@origin` (child of the remote tip)
2. Apply the edit to the file on disk; verify with `git show`/`grep` — not a
   regex-replace fire-and-forget
3. `jj describe -m "<PR commit subject>"` (describes @, the NEW commit)
4. `jj bookmark set migrate/<app> -r @ --allow-backwards`
5. `jj git push --remote origin --bookmark migrate/<app>`
6. **Ground-truth verify against origin**, not local state: `git fetch origin`
   then `git show origin/migrate/<app>:<path>` — `jj file show -r <bm>@origin`
   can show a stale tracking view, and only `git ls-remote`/`git show origin/…`
   prove what reviewers will see.

If a bookmark went divergent (`jj bookmark list` shows `/0`, `/1`), find which
sibling has the wanted content via `jj file show -r <change-id>/<N>`, point the
bookmark at the good commit, and `jj abandon` the stale one before pushing.

## Post-split follow-up campaigns (proven 2026-08-30, second pass)

When a review round demands the SAME structural change in every PR (e.g.
"routes belong in base, overlay only patches parentRefs — syncthing model"),
the per-app edit loop above works but scale it with these hard rules:

- **Name bookmarks, not paths.** For family dirs the bookmark is the SHORT
  name (`migrate/discord`, `migrate/lidarr`) while the file path is
  `apps/mautrix/discord/…` — `jj new migrate/mautrix/discord@origin` fails
  ("Revision doesn't exist"). Build the loop from (path, bookmark) pairs.
- **After ANY scripted multi-app edit, verify every branch on origin** with
  `git fetch && git cat-file -e origin/<branch>:<new-file>` +
  `git show origin/<branch>:<path> | grep <marker>` — cat-file exit 128 means
  the file never made it, regardless of what local `jj` claims. In the proven
  pass, 23 of 27 branches silently lacked the change despite rc=0 loops.
- **`kustomize build` does NOT validate semantic wiring** — a TCPRoute
  `sectionName` pointing at a renamed-away listener still renders exit 0.
  Grep the rendered output for the sectionName/listener pairs you depend on.
- **String-append onto a kustomization without a trailing newline glues lines**
  (`patch-sts.yamlpatches:`) → `yaml: mapping values are not allowed`. Always
  `content.rstrip() + '\n' + block + '\n'`.
- **`gh pr edit --base` may throw generic GraphQL errors**; use REST:
  `gh api repos/<org>/<repo>/pulls/<N> -X PATCH -f base=main`.
- Keep a fix spanning many PRs as ONE stacked commit ONLY if the user accepts
  it. The tags fix first shipped as a single follow-up PR #1982, but the user
  then rejected that ("certain apps doesn't have the right tailscale.com/tags")
  — the tags had to be folded INTO each app's PR. Default: corrections belong
  in each app's own PR; a shared follow-up PR needs explicit user sign-off.
- **CI failures after a scripted edit campaign — three distinct root causes hit
  in one pass, all presenting as CI failure while kustomize renders fine
  locally:** (1) unformatted YAML — Python `yaml.safe_dump` list style ≠ repo
  treefmt style; run `nix fmt` at each branch tip and squash (see
  kustomize-overlay-authoring "CI treefmt gate"). (2) glued kustomization
  lines (`...Policypatches:`) from string-append without a trailing newline.
  (3) markdownlint MD057 — the PR deleted a file the root README still links
  to; grep `README.md` for links to any deleted file before pushing.
- **CodeRabbit review threads on batch PRs are bulk-resolvable** when the fix
  already shipped: GraphQL `resolveReviewThread(input: {threadId})` +
  `addPullRequestReviewThreadReply` with a rationale citing the concrete fix
  (sks-pr-resolve Gate 3). Proven pass: 5 threads across 2 PRs — all
  CodeRabbit majors about the pre-fix state — resolved in one scripted pass.
