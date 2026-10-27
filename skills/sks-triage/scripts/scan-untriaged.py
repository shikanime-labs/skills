#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3
"""List open issues and PRs whose triage metadata is incomplete.

Computed against what the repo or its org actually supports: a class with
no supported values is never a gap. Milestones are not a triage class —
sks-plan / sks-milestone own their assignment. Assignment follows the
triage doctrine: machine-routable work gets an assignee, human-only work
stays unassigned — an unassigned item is never a gap. One paginated call
per repo. Output: TSV number, kind, missing classes.

Usage:
    scan-untriaged.py OWNER/REPO
    scan-untriaged.py --self-check
"""

import json
import subprocess
import sys


def _gh(*args: str) -> str:
    """Run gh, return stdout; raises CalledProcessError on failure."""
    return subprocess.run(
        ["gh", *args], check=True, capture_output=True, text=True
    ).stdout


def _supported(repo: str, owner: str) -> tuple[int, int]:
    """(enabled issue types, org issue fields); an absent endpoint means 0."""
    try:
        types = [
            t
            for t in json.loads(_gh("api", f"repos/{repo}/issue-types"))
            if t.get("is_enabled")
        ]
    except subprocess.CalledProcessError:
        types = []
    try:
        fields = json.loads(_gh("api", f"orgs/{owner}/issue-fields"))
    except subprocess.CalledProcessError:
        fields = []
    return len(types), len(fields)


def gaps_for(item: dict, types: int, fields: int) -> list[str]:
    """Missing triage classes for one issue/PR API object."""
    kind = "pr" if "pull_request" in item else "issue"
    gaps = []
    if kind == "issue" and types and not item.get("type"):
        gaps.append("type")
    if not item.get("labels"):
        gaps.append("labels")
    if kind == "issue" and fields and not item.get("issue_field_values"):
        gaps.append("fields")
    return gaps


def scan(repo: str) -> int:
    """Print the untriaged TSV; return how many rows it carried."""
    owner = repo.split("/")[0]
    types, fields = _supported(repo, owner)
    print(f"# classes: type={types} fields={fields}")
    issues = json.loads(
        _gh("api", "--paginate", f"repos/{repo}/issues?state=open&per_page=100")
    )
    untriaged = 0
    for item in issues:
        gaps = gaps_for(item, types, fields)
        if gaps:
            untriaged += 1
            kind = "pr" if "pull_request" in item else "issue"
            print(f"{item['number']}\t{kind}\t{','.join(gaps)}")
    return untriaged


def _self_check() -> None:
    pr = {"number": 1, "pull_request": {}, "labels": [], "assignees": []}
    issue = {
        "number": 2,
        "type": {"name": "Bug"},
        "labels": [{"name": "bug"}],
        "assignees": [{"login": "a"}],
        "issue_field_values": [],
    }
    assert gaps_for(pr, 1, 1) == [
        "labels"
    ]  # no type/fields on PRs; assignee never a gap
    assert gaps_for(issue, 1, 0) == []  # fields unsupported → not a gap
    assert gaps_for(dict(issue, issue_field_values=None), 1, 1) == ["fields"]
    stripped = dict(issue, labels=[], assignees=[], type=None)
    assert gaps_for(stripped, 0, 0) == ["labels"]  # unassigned is not a gap
    print("self-check: pass")


def main(argv: list[str]) -> int:
    if "--self-check" in argv:
        _self_check()
        return 0
    if len(argv) != 2 or not argv[1]:
        print(__doc__)
        return 2
    try:
        scan(argv[1])
    except subprocess.CalledProcessError as e:
        print(e.stderr, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
