#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3
"""Print every triage-relevant metadata value the repo or its org offers.

Labels, projects, assignees, enabled issue types, and org issue fields.
Triage must only set values that appear here. One section per metadata
class; a missing section means that class stays empty. Milestones are not
a triage class — sks-plan / sks-milestone own their assignment.

Usage:
    discover-metadata.py REPO
"""

import json
import subprocess
import sys


def _gh_json(*args: str, default=None):
    """Run gh, parse stdout as JSON; default on failure (absent endpoint)."""
    try:
        out = subprocess.run(
            ["gh", *args], check=True, capture_output=True, text=True
        ).stdout
    except subprocess.CalledProcessError:
        return default
    return json.loads(out) if out.strip() else default


def discover(repo: str) -> int:
    owner = repo.split("/")[0]
    for label in _gh_json(
        "label",
        "list",
        "--repo",
        repo,
        "--limit",
        "200",
        "--json",
        "name,description",
        default=[],
    ):
        print(f"{label['name']}\t{label.get('description') or ''}")
    print("== milestones ==")
    print("not a triage class — assigned by sks-plan / sks-milestone")
    print("== projects (owner) ==")
    try:
        out = subprocess.run(
            ["gh", "project", "list", "--owner", owner, "--format", "json"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        envelope = json.loads(out) if out.strip() else {}
        projects = (
            envelope.get("projects", []) if isinstance(envelope, dict) else envelope
        )
    except subprocess.CalledProcessError:
        projects = None
    if projects is None:
        print("no accessible projects (needs project scope)")
    for p in projects or []:
        print(f"{p['number']}\t{p['title']}")
    print("== assignees ==")
    sys.stdout.flush()
    subprocess.run(
        ["gh", "api", "--paginate", f"repos/{repo}/assignees", "--jq", ".[].login"],
        check=False,
    )
    print("== issue types (enabled) ==")
    for t in _gh_json("api", "--paginate", f"repos/{repo}/issue-types", default=[]):
        if t.get("is_enabled"):
            print(t["name"])
    print("== org issue fields ==")
    fields = (
        _gh_json("api", "--paginate", f"orgs/{owner}/issue-fields", default=[]) or []
    )
    if not fields:
        print("no org issue fields")
    for f in fields:
        opts = ",".join(o["name"] for o in f.get("options") or [])
        print(f"{f['id']}\t{f['name']}\t{f['data_type']}\t{opts}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not argv[1]:
        print(__doc__)
        return 2
    try:
        return discover(argv[1])
    except subprocess.CalledProcessError as e:
        print(e.stderr, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
