#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3
"""Contrastive probe: grade an old and a new skill body over the SAME
assertion set and diff the pass/fail flips.

A true-to-false flip is a regression (fix the body before shipping);
false-to-true flips are the measured gain. An assertion with no checkable
content is reported ungraded, never silently passed.

Usage:
    probe.py OLD_BODY.md NEW_BODY.md evals.json
    probe.py --self-check
"""

import hashlib
import json
import re
import sys

# assertion metalanguage: verbs and connectives that describe the body but
# never appear in it; content words are what remains after stripping these
_STOP = {
    "body",
    "frontmatter",
    "mentions",
    "contains",
    "word",
    "requires",
    "keeps",
    "yaml",
    "parses",
    "heading",
    "starts",
    "characters",
    "description",
    "license",
    "field",
    "equals",
    "least",
    "during",
    "still",
    "also",
    "must",
    "should",
    "every",
    "only",
    "never",
    "presents",
    "mines",
    "delegates",
    "merges",
    "lands",
    "ranks",
    "treats",
    "names",
    "states",
    "routes",
    "frames",
    "forbids",
    "distinguishes",
    "restricts",
    "refreshing",
    "reporting",
    "along",
    "into",
    "using",
    "same",
    "other",
    "first",
    "last",
    "more",
    "most",
    "less",
    "much",
    "many",
    "some",
    "will",
    "would",
    "than",
    "then",
    "when",
    "while",
    "where",
    "which",
    "them",
    "they",
    "their",
    "there",
    "those",
    "these",
    "have",
    "has",
    "been",
    "being",
    "were",
    "with",
    "that",
    "this",
    "from",
    "over",
}


def _frontmatter(body: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", body, re.DOTALL)
    return m.group(1) if m else ""


def _content_words(assertion: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z]{4,}", assertion) if w.lower() not in _STOP]


def grade(body: str, assertion: str) -> bool | None:
    """Case-insensitive literal containment, frontmatter special cases.

    Returns None when the assertion has no checkable content.
    """
    b, a = body.lower(), assertion.lower()
    if "frontmatter parses" in a and "'name' equals" in a:
        name = re.search(r"'name' equals '?([a-z0-9-]+)'?", a)
        return bool(name) and f"name: {name.group(1)}" in _frontmatter(body).lower()
    if "frontmatter" in a and "license" in a:
        return "license:" in _frontmatter(body).lower()
    if "description" in a and "characters" in a:
        d = re.search(
            r"^description:\s*'?(.*?)'?\s*$", _frontmatter(body), re.MULTILINE
        )
        limit = re.search(r"(\d+)", a)
        return bool(d) and bool(limit) and len(d.group(1)) <= int(limit.group(1))
    lits = re.findall(r"'([^']+)'", assertion)
    if lits:
        return all(l.lower() in b for l in lits)
    words = _content_words(assertion)
    if not words:
        return None  # no checkable content: ungraded, never a fake pass
    return all(w.lower() in b for w in words)


def probe(old: str, new: str, assertions: list[str]) -> dict:
    """The contrastive step: same assertions, two harness states, flip diff."""
    rows = []
    reg = gain = old_pass = new_pass = 0
    for a in assertions:
        o, n = grade(old, a), grade(new, a)
        if o is None or n is None:
            rows.append({"assertion": a, "old": o, "new": n, "flip": "ungraded"})
            continue
        old_pass += o
        new_pass += n
        if o and not n:
            reg += 1
            flip = "REGRESSION"
        elif n and not o:
            gain += 1
            flip = "gain"
        elif n:
            flip = "pass"
        else:
            flip = "fail"
        rows.append({"assertion": a, "old": o, "new": n, "flip": flip})
    fp = hashlib.sha1(
        (old + "\0" + new + "\0" + "\0".join(assertions)).encode()
    ).hexdigest()[:16]
    verdict = "REGRESSION - fix the body before shipping" if reg else "clean"
    return {
        "fingerprint": fp,
        "note": "result is bound to this fingerprint; never reuse it after either input changes",
        "assertions": len(assertions),
        "old_pass": old_pass,
        "new_pass": new_pass,
        "regressions": reg,
        "gains": gain,
        "verdict": verdict,
        "rows": rows,
    }


def _self_check() -> None:
    g = grade
    assert (
        g("judges are provenance-blind", "Body requires 'provenance-blind' judges")
        is True
    )
    assert g("no blindness here", "Body requires 'provenance-blind' judges") is False
    assert g("whatever", "Body") is None
    old = "keep step one and the safety gate here"
    new = "keep step one only"
    r = probe(old, new, ["Body keeps 'safety'"])
    assert r["regressions"] == 1 and r["verdict"].startswith("REGRESSION")
    r2 = probe(old, old, ["Body keeps 'safety'"])
    assert r2["verdict"] == "clean" and r2["old_pass"] == r2["new_pass"] == 1
    print("self-check: pass")


def main(argv: list[str]) -> int:
    if "--self-check" in argv:
        _self_check()
        return 0
    if len(argv) != 4:
        print(__doc__)
        return 2
    with open(argv[1]) as f:
        old = f.read()
    with open(argv[2]) as f:
        new = f.read()
    with open(argv[3]) as f:
        ev = json.load(f)
    assertions = [a for e in ev["evals"] for a in e["assertions"]]
    r = probe(old, new, assertions)
    print(
        f"{r['old_pass']}->{r['new_pass']}/{r['assertions']} "
        f"regressions={r['regressions']} gains={r['gains']} "
        f"ungraded={sum(1 for x in r['rows'] if x['flip'] == 'ungraded')} "
        f"verdict={r['verdict']} fingerprint={r['fingerprint']}"
    )
    for row in r["rows"]:
        if row["flip"] in ("REGRESSION", "fail", "ungraded"):
            print(f"    {row['flip']}: {row['assertion']}")
    return 1 if r["regressions"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
