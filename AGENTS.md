# skills

Curated catalog of self-improved agent skills for Hermes and compatible agents.

**Language:** Markdown (SKILL.md)

**Structure:** `skills/` — individual skill dirs with `SKILL.md`; `README.md` — install docs

**Commit style:** Plain-text capitalized title, no prefix. Body with labels: `Design:`, `Related:`, `Closes #`.

**Stack:** 1 commit == 1 PR via ghstack. Amend + `ghstack` to resubmit. `ghstack land` on head PR to land stack. Never `gh pr merge`. Never force-push.

**Protect `main`:** 1 review, linear history, signed commits, squash+rebase only.

*Each skill needs valid YAML frontmatter in SKILL.md. Test against target agent*
