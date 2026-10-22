#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 gh jujutsu
"""Print (or write to OUTFILE, default /tmp/sks_ms_ids.txt) the ordered
(oldest->newest) merge commit SHAs of a milestone's merged PRs. One SHA per
line. The milestone is the authoritative backport set — NOT a BASE_TAG..main
diff (that over-counts next-minor dev commits).
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


def fetch_backport_set(repo: str, milestone: int, out: str) -> int:
    # Phase 1: the milestone's PR numbers, oldest merged first. The issues
    # endpoint honors the milestone filter but returns null merge_commit_sha.
    issues = gh_api(
        f"repos/{repo}/issues?milestone={milestone}&state=closed&per_page=100"
    )
    prs = sorted(
        (i["pull_request"]["merged_at"], i["number"])
        for i in issues
        if i.get("pull_request") and i["pull_request"].get("merged_at")
    )
    # Phase 2: merge_commit_sha per PR (only the pulls endpoint returns it).
    shas = []
    for _, number in prs:
        pull = gh_api(f"repos/{repo}/pulls/{number}")
        shas.append(pull["merge_commit_sha"])
    with open(out, "w") as f:
        f.write("\n".join(shas) + "\n" if shas else "")
    return len(shas)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", help="OWNER/REPO, e.g. cloud-pi-native/console")
    ap.add_argument("milestone", type=int, help="milestone number")
    ap.add_argument(
        "outfile",
        nargs="?",
        default="/tmp/sks_ms_ids.txt",
        help="output path (default: /tmp/sks_ms_ids.txt)",
    )
    args = ap.parse_args()
    n = fetch_backport_set(args.repo, args.milestone, args.outfile)
    print(f"wrote {n} commits to {args.outfile}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
