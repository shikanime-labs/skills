# Example commit (repo: shikanime-labs/skills)

```text
Document the gh-stack PR seed mapping in sks-pr

Encode what `gh stack submit` copies from the commit into the PR title/body
so the sks-pr body rule stays in parity.

Design: skills/shikanime-studio/sks-pr/SKILL.md
Related: https://github.com/shikanime-labs/skills/issues/123
Signed-off-by: Shikanime Deva <william.phetsinorath@shikanime.studio>
Change-Id: I8d3af00example000000000000000000000000example
```

`Signed-off-by` and `Change-Id` are appended by jj config and signing on push —
do NOT add them by hand (duplicate trailers). 80-col wrap; `nix fmt` before
shipping.
