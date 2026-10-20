# Shikanime org conventions

Canonical checkouts live at `~/Source/Repos/github.com/<org>/<repo>` — run GC
from that repo root. Skill-created workspaces are siblings of it
(`../<repo>.<unit>`, `../<repo>.fix`), never subdirectories.

Remote-branch sweep orgs: `shikanime-labs` and `shikanime-studio`. Never
delete the default branch, protected branches, `release/*` tags, or ghstack
role branches of open stacks; `git`-based org repos (manifests, skills) may
enforce gitlint — irrelevant to deletion, but confirm the branch has no open
PR first (`gh pr list --head <branch>`).
