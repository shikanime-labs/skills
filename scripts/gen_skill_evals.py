#!/usr/bin/env python3
"""gen_skill_evals.py — emit a per-skill evals/evals.json for every skill.

Writes the agentskills.io evaluating-skills test-case format into each skill
dir. Each case's `prompt` is a REAL user invocation derived from the skill's
own description/sections (prompt testing, not file-edit meta-instructions),
and assertions grade the skill's readiness for that prompt (trigger coverage +
content depth) plus the always-on structural contract (name==dir, license,
headings, no separator artifact) which is the regression gate.

Usage:
  python3 scripts/gen_skill_evals.py [--root .] [--dry-run]
"""
import os
import re
import json
import argparse

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
STOP = set("use when the a an to for with of and or in on by from that this is are be as at it you your via per into not no".split())


def load_desc(path):
    text = open(os.path.join(path, "SKILL.md"), encoding="utf-8").read()
    m = FRONTMATTER_RE.match(text)
    if not m:
        return ""
    desc, in_desc = [], False
    for line in m.group(1).splitlines():
        if line.startswith("description:"):
            in_desc = True
            head = line.split(":", 1)[1].strip().strip('"')
            if head:
                desc.append(head)
        elif in_desc and re.match(r"^\s+\S", line):
            desc.append(line.strip().strip('"'))
        elif in_desc:
            break
    return " ".join(desc)


def keywords(desc):
    toks = re.findall(r"[a-z0-9]+", desc.lower())
    ks = [t for t in toks if t not in STOP and len(t) > 3]
    return ks[:2] if ks else ["skill"]


def find_skills(root):
    out = []
    for dirpath, dirs, files in os.walk(root):
        if "SKILL.md" in files:
            out.append(dirpath)
    return out


def sample_headings(path, n=3):
    """Return up to n non-generic '##' heading strings from the skill body."""
    text = open(os.path.join(path, "SKILL.md"), encoding="utf-8").read()
    fm = FRONTMATTER_RE.match(text)
    body = text[fm.end():] if fm else text
    heads = [h.strip() for h in re.findall(r"^##\s+(.+)$", body, re.M)]
    skip = {"when to use", "see also", "references", "examples", "notes"}
    heads = [h for h in heads if h.lower() not in skip]
    return heads[:n]


def build_cases(skill_dir, name):
    """Prompt tests: 2 specific positive (distinct sections/phrasings) + 2
    negative (boundary/malformed -> structural gate holds; near-miss wrong org
    -> description must not claim the other family's prefix)."""
    desc = load_desc(skill_dir)
    ks = keywords(desc)
    k1 = ks[0]
    heads = sample_headings(skill_dir)
    h1 = heads[0] if heads else "the core procedure"
    trigger = desc.strip()
    if trigger.lower().startswith("use when"):
        trigger = trigger[8:].strip()
    prompt = f"{trigger[0].upper() + trigger[1:] if trigger else 'Help me with ' + name}."

    # negative: a malformed/boundary prompt must NOT crash the contract
    malformed = f"idk how 2 {name} ??? (pls fix my broken config file 🔧)"
    # negative: near-miss from the OTHER org family — description must not claim
    # its prefix (sks- vs cpn-, and vice versa)
    other_prefix = "cpn-" if name.startswith("sks") else "sks-"

    structural = [
        "Frontmatter parses as YAML with a top-level 'name' key",
        f"Frontmatter 'name' equals the directory basename '{name}'",
        "Description starts with 'Use when' and is <= 200 characters",
        "license field is 'Apache-2.0'",
        "Body still contains at least one '##' heading",
        f"Description still contains the token '{k1}'",
        "No '---------' separator artifact appears outside a code fence",
    ]
    return {
        "skill_name": name,
        "evals": [
            {  # positive: the skill's own trigger, section coverage
                "id": 1,
                "prompt": prompt,
                "expected_output": f"The skill answers the '{name}' request: its body covers '{h1}' and stays loadable/well-formed.",
                "files": [],
                "assertions": [
                    f"Description still contains the token '{k1}'",
                    f"Body contains a '## {h1}' heading" if heads else "Body still contains at least one '##' heading",
                ] + structural,
            },
            {  # positive: explicit procedure request
                "id": 2,
                "prompt": f"Show the step-by-step procedure for {name}.",
                "expected_output": "SKILL.md exposes an actionable procedure: enough sections and substance to follow step by step.",
                "files": [],
                "assertions": [
                    "Body has at least 1 '##' section and 800+ characters of body",
                    "Description token recall vs baseline >= 50%",
                    "Body size vs baseline <= 1.30x",
                    f"Frontmatter 'name' equals the directory basename '{name}'",
                ],
            },
            {  # negative: garbled input still yields a well-formed, loadable skill
                "id": 3,
                "prompt": malformed,
                "expected_output": "Even on a malformed request, the skill stays loadable: frontmatter parses, name==dir, no separator artifact.",
                "files": [],
                "assertions": structural,
            },
            {  # negative: a near-miss from the wrong org must not make the
               # description claim the other family's prefix
                "id": 4,
                "prompt": f"I'm in the {('cloud-pi-native' if name.startswith('sks') else 'shikanime')} org, help me with this.",
                "expected_output": f"The '{name}' description does NOT claim the other org's prefix '{other_prefix}'.",
                "files": [],
                "assertions": [
                    f"Description does not contain the substring '{other_prefix}'",
                    f"Frontmatter 'name' equals the directory basename '{name}'",
                ],
            },
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    skills = find_skills(a.root)
    count = 0
    for sd in skills:
        name = os.path.basename(os.path.abspath(sd))
        ej_dir = os.path.join(sd, "evals")
        ej = os.path.join(ej_dir, "evals.json")
        cases = build_cases(sd, name)
        if a.dry_run:
            print(f"{name}: {len(cases['evals'])} cases -> {ej}")
            continue
        os.makedirs(ej_dir, exist_ok=True)
        json.dump(cases, open(ej, "w"), indent=2)
        count += 1
    print(f"wrote evals.json for {count} skills")


if __name__ == "__main__":
    main()
