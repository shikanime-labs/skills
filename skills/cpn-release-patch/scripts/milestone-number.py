#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 gh jujutsu
"""Print the milestone number for the given title on REPO (OWNER/REPO),
or exit non-zero when the milestone is absent or closed. The number feeds
fetch-backport-set.py and the issue query in Step 2.
"""

import argparse
import json
import subprocess
import sys


def gh_api(path: str) -> list[dict]:
    r = subprocess.run(
        ["gh", "api", "--paginate", path],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        raise SystemExit(f"Error: gh api {path} failed: {r.stderr.strip()}")
    return json.loads(r.stdout)


def milestone_number(repo: str, title: str) -> int:
    for ms in gh_api(f"repos/{repo}/milestones?state=open"):
        if ms.get("title") == title:
            return ms["number"]
    raise SystemExit(f"Error: milestone '{title}' is absent or closed on {repo}.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", help="OWNER/REPO, e.g. cloud-pi-native/console")
    ap.add_argument("milestone_title", help="exact milestone title, e.g. 9.24.5")
    args = ap.parse_args()
    print(milestone_number(args.repo, args.milestone_title))
    return 0


if __name__ == "__main__":
    sys.exit(main())
