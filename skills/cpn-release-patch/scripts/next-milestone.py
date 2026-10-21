#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3
"""Print the next patch milestone for a base tag: v9.24.4 -> 9.24.5.

Pure derivation — no network. The hotfix/<milestone> branch name derives
from this value.
"""

import argparse
import sys

TAG_RE = r"v?(\d+)\.(\d+)\.(\d+)"


def next_milestone(base_tag: str) -> str:
    import re

    m = re.fullmatch(TAG_RE, base_tag)
    if not m:
        raise SystemExit(
            f"Error: '{base_tag}' is not a vMAJOR.MINOR.PATCH tag (e.g. v9.24.4)."
        )
    maj, min_, pat = (int(g) for g in m.groups())
    return f"{maj}.{min_}.{pat + 1}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("base_tag", help="base release tag, e.g. v9.24.4")
    args = ap.parse_args()
    print(next_milestone(args.base_tag))
    return 0


if __name__ == "__main__":
    sys.exit(main())
