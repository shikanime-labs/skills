#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3 gh jujutsu
"""Discover GC candidates in a shikanime jj repo: dangling bookmarks (not on
trunk, no open PR) and skill-created workspaces (<repo>.<unit> or
<repo>-fix), with the dirty working-copy guard. Dry-run only — never forgets
or removes. Default REPO_DIR is the cwd; run from the repo root.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

TRUNK_NAMES = ("main", "trunk", "master")


def sh(*cmd: str, cwd: str | None = None) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, check=False)
    return r.stdout


def discover(repo_dir: str) -> None:
    repo = Path(repo_dir).resolve()
    if not (repo / ".jj").exists():
        raise SystemExit(f"Error: {repo} has no .jj/ — run from a jj repo root.")

    # protected names: trunk + any bookmark with an open PR
    open_prs = {
        p["headRefName"]
        for p in json.loads(
            sh("gh", "pr", "list", "--state", "open", "--limit", "200",
               "--json", "headRefName", cwd=str(repo)) or "[]"
        )
    }

    print("== dangling bookmarks (not trunk, no open PR) ==")
    # jj 0.43: template the name alone and dedupe; trunk() resolves the
    # configured trunk so the revset works beyond main-named repos.
    bookmarks = sh(
        "jj", "bookmark", "list", "-r", "bookmarks() & ~::trunk()",
        "--color", "never", "-T", 'name ++ "\\n"', cwd=str(repo),
    ).split()
    for bm in sorted(set(bookmarks) - set(TRUNK_NAMES) - open_prs):
        print(bm)

    print("== skill workspaces (<repo>.<unit> or <repo>.fix) ==")
    # jj 0.43: default `workspace list` has no path column — template it
    repo_name = repo.name
    for line in sh("jj", "workspace", "list", "--color", "never",
                   "-T", 'name ++ "\\t" ++ root ++ "\\n"',
                   cwd=str(repo)).splitlines():
        name, _, path = line.partition("\t")
        # skill workspaces are <repo>.<unit> or <repo>-fix (dash: fix only)
        if not (name.startswith(f"{repo_name}.")
                or name.startswith(f"{repo_name}-fix")):
            continue
        # canonical repo-named workspace is never a candidate
        status = sh("jj", "-R", path, "status", "--color", "never")
        if "has no changes" in status:
            print(f"CLEAN {name} {path}")
        else:
            print(f"DIRTY {name} {path}   # skip: uncommitted changes (data loss)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "repo_dir", nargs="?", default=".",
        help="jj repo root (default: current directory)",
    )
    args = ap.parse_args()
    discover(args.repo_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
