---
name: sks-release
description:
  "Use when cutting a release of the skills catalog: verify green main, bump
  manifest versions, signed tag, published notes, RC pre-release when
  unproven."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - release
      - tags
    related_skills:
      - sks-dev
      - sks-commit
      - sks-land
      - sks-milestone
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Release Cut

Cut a release of this catalog: gate on green main, bump the manifest version,
tag signed, publish notes. An RC pre-release covers the case where main is
ahead but validation is still wanted before the final cut.

Org facts — the release repo, the signed-tag convention's origin, previous
cuts — live in `references/shikanime.md`; read it when operating in the
shikanime org.

## When to Use

- "Cut a release" / "ship v2.1.0" — main is ahead of the last tag and green.
- "Give me a release candidate" — same, but final validation is unproven.
- A milestone just shipped (`sks-milestone`) and the release plane follows it.
- Not for milestone provisioning or item assignment — that is `sks-milestone`.

## Procedure

### 1. Gate: green main at the remote tip

```bash
jj git fetch
gh pr list -R <org>/skills --state open --json number -q 'length' \
  # 0 or accounted for
gh api repos/<org>/skills/commits/main/check-runs \
  --jq '.check_runs[] | "\(.name) \(.conclusion)"'                  # all success
```

Red or pending checks stop the cut — a gate doing its job, never `--admin`
past it.

### 2. Pick the version from the tag range

```bash
git tag -l | sort -V | tail -1        # previous cut
git log --oneline <prev>..main        # the mine for notes and the version
```

Minor (`v2.1.0`) when the range adds skills or features; patch (`v2.0.1`)
when it only fixes. Never a major without an explicit user call.

### 3. Bump the manifests in a landed commit

Both `skills.json` and `package.json` carry a top-level `version` equal to
the last tag. Bump both to the new version, land via the normal loop
(`sks-commit` → PR → `sks-land`). The tag must point at a main whose
manifests already read the new version — tagging first ships a release whose
install metadata disagrees with its tag.

### 4. Tag signed, push via plain git from the main checkout

```bash
cd <main checkout> && git pull --ff-only
git tag -s vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

jj trips `pre_receive` on signed annotated tags (a repo-level convention —
see `references/shikanime.md` when operating in the shikanime org) — plain
git from the main checkout, never jj and never the isolation
workspace, which has no git remote.

### 5. Publish the release with notes from the range

Notes are mandatory: v2.0.0 shipped an empty body — that is the defect
this step exists to prevent. Never a raw 150-line commit dump — distill the
mined log into the changelog template (shape after Longhorn/Kubernetes
release notes: highlights up front, themed groups, linked refs):

```markdown
## What's new

<one-paragraph summary of the release theme>

### Highlights

- <user-visible change> (#PR)

### New skills

- `sks-<name>` — <one-line trigger> (#PR)

### Enhancements

- <change> (#PR)

### Fixes

- <fix> (#PR)

### Deprecations

<only when something was removed or renamed — else drop the section>
```

```bash
gh release create vX.Y.Z -R <org>/skills \
  --target main --verify-tag \
  --title "vX.Y.Z" --notes-file /tmp/notes.md
gh release view vX.Y.Z -R <org>/skills --json body -q '.body | length'   # > 0
```

Body prose rules: `sks-edit` references/github-text/guide.md (file, never
free
inline;
text, never wrapped).

### 6. Milestone close-off

Sweep and close the release milestone via `sks-milestone` — this skill never
restates its provisioning plane.

## RC pre-release

Main ahead of the last tag but validation unproven — cut `vX.Y.Z-rc.N`:

```bash
git tag -s vX.Y.Z-rc.N -m "Release vX.Y.Z-rc.N"
git push origin vX.Y.Z-rc.N
gh release create vX.Y.Z-rc.N -R <org>/skills \
  --target main --verify-tag --prerelease \
  --title "vX.Y.Z-rc.N" --notes-file /tmp/notes.md
```

`--prerelease` is not optional: without it the RC hijacks Latest. Iterate N
per validation round; promote by running the full procedure at the final
version — a fresh tag and release, never editing the RC into one.

## Pitfalls

- **Empty release body.** `gh release create` without notes succeeds
  silently — v2.0.0 proves it. The body-length readback in step 5 is the
  gate.
- **Tag before the version bump lands.** The release then advertises the
  previous version in its own manifests. Order is bump → land → tag.
- **jj refuses the signed tag push** with `pre_receive` — recover by pushing
  the same tag object from the main checkout with plain git.
- **An RC without `--prerelease` becomes Latest** and every
  `skills.sh`/installer consumer pins it. Same failure editing a published
  RC's tag — delete the release object first, never move a pushed tag.
- **Notes from a stale fetch** miss the last landed commits — `jj git fetch`
  (or `git pull`) in step 1 is what makes the range honest.

## Verification

```bash
git tag -v vX.Y.Z                          # signature verifies
gh release view vX.Y.Z -R <org>/skills \
  --json isLatest,body -q '"\(.isLatest) \(.body | length)"'
python3 -c "import json; assert json.load(open('skills.json'))['version'] \
  == json.load(open('package.json'))['version'] == 'X.Y.Z'"
```

Done when: tag verifies signed, release is Latest with a non-empty body, and
both manifests read the released version on main.

## See also

- `sks-milestone` — the release plane this cut closes out.
- `sks-land` — landing the version-bump commit.
- `sks-edit` references/github-text/guide.md — notes prose and tooling discipline.
- `sks-commit` — the bump commit's envelope.
