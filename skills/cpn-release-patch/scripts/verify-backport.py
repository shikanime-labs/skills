#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3 jujutsu git
"""Verify a rebuilt hotfix chain: exact commit count, zero conflict markers,
and a tree that reconstructs main's source (release-please files may
differ). Exit 0 when clean; exit 1 and print what failed otherwise.
"""

import argparse
import re
import subprocess
import sys

# ponytail: release-please noise filter copied from the shell era; extend
# when a new generated file class lands in the console repo
RELEASE_FILES = re.compile(
    r"package\.json|CHANGELOG\.md|\.release-please-manifest\.json"
)


def sh(*cmd: str) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return r.stdout


def verify(base_tag: str, tip: str, expected: int) -> int:
    rng = f"{base_tag}..{tip}"
    commits = [c for c in sh("jj", "log", "-r", rng, "--no-graph",
                             "-T", "commit_id").splitlines() if c]
    conflicts = [c for c in sh("jj", "log", "-r", rng, "--no-graph",
                               "-T",
                               'if(conflict, description.first_line(), "")'
                               ).splitlines() if c]
    diff = [f for f in sh("git", "diff", "--name-only", tip, "main"
                          ).splitlines() if f and not RELEASE_FILES.search(f)]

    fail = 0
    if len(commits) != expected:
        print(f"FAIL: chain has {len(commits)} commits, expected {expected}",
              file=sys.stderr)
        fail = 1
    if conflicts:
        print(f"FAIL: {len(conflicts)} conflict markers in {rng}", file=sys.stderr)
        fail = 1
    if diff:
        print(f"FAIL: tree differs from main: {' '.join(diff)}", file=sys.stderr)
        fail = 1
    if not fail:
        print(f"OK: {len(commits)} commits, no conflicts, tree matches main")
    return fail


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("base_tag", help="base release tag, e.g. v9.24.4")
    ap.add_argument("tip", help="commit id of the chain tip")
    ap.add_argument("expected_count", type=int, help="exact commit count")
    args = ap.parse_args()
    return verify(args.base_tag, args.tip, args.expected_count)


if __name__ == "__main__":
    sys.exit(main())
