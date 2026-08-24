#!/usr/bin/env python3
"""run_skill_eval.py — skill-edit evals per agentskills.io/evaluating-skills.

The doc's model (prompt + expected_output + assertions, run with/without the
skill, graded with evidence into grading.json, aggregated into benchmark.json)
adapted to skill AUTHORING: the "output" of a skill edit is the edited file
tree, so assertions are checked programmatically (parsing, name==dir, token
recall, size ratio) rather than by an LLM. The doc itself recommends scripts
over LLM judgment for mechanical checks.

Each skill carries its own evals/evals.json (doc: "Store test cases in
evals/evals.json inside your skill directory"). This harness grades a skill
against that contract and writes the doc's workspace artifacts.

Workspace layout (doc spec), under <skill>-workspace/iteration-N/:
  <case>/with_skill/{outputs,timing.json,grading.json}
  <case>/old_skill/{...}            # baseline = previous version (optional)

Usage:
  python3 evals/run_skill_eval.py --skill <dir> [--baseline <dir>] [--iteration 1]
  python3 evals/run_skill_eval.py --selftest
Exit nonzero if any assertion fails.
"""
import sys
import os
import re
import json
import argparse
import tempfile

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
TOKEN_RE = re.compile(r"[a-z0-9]+")
STOP = set("use when the a an to for with of and or in on by from that this is are be as at it you your via per into not no".split())


def load_skill(path):
    p = os.path.join(path, "SKILL.md")
    text = open(p, encoding="utf-8").read()
    fm = {}
    body = text
    m = FRONTMATTER_RE.match(text)
    if m:
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
                in_desc = False
                if ":" in line and not line.startswith((" ", "\t")):
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"')
            elif ":" in line and not line.startswith((" ", "\t")):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
        if desc:
            fm["description"] = " ".join(desc)
        body = text[m.end():]
    headings = re.findall(r"^##\s+(.+)$", body, re.M)
    return {"path": path, "fm": fm, "headings": headings, "body": body,
            "chars": len(body), "name": fm.get("name", "")}


def assert_one(text, s, baseline=None):
    """Return (passed, evidence). s = loaded skill under test."""
    t = text.lower()
    if t.startswith("frontmatter parses"):
        ok = bool(s["fm"])
        return ok, ("keys: " + ", ".join(sorted(s["fm"]))) if ok else "no frontmatter parsed"
    if "directory basename" in t:
        base = os.path.basename(os.path.abspath(s["path"]))
        ok = s["name"] == base
        return ok, f"name='{s['name']}' dir='{base}'"
    if "description starts with 'use when'" in t:
        d = s["fm"].get("description", "")
        # cpn skills are authored in French, so the imperative trigger phrase
        # there is "À utiliser quand" — same contract, other language.
        starts = d.startswith(("Use when", "À utiliser quand"))
        ok = starts and len(d) <= 200
        return ok, f"desc={len(d)}c use_when={starts}"
    if "license field is" in t:
        lic = s["fm"].get("license", "")
        m = re.search(r"'([^']+)'", t)
        want = m.group(1) if m else "Apache-2.0"
        ok = lic.lower() == want
        return ok, f"license='{lic}' want='{want}'"
    if "at least one '##' heading" in t:
        ok = bool(s["headings"])
        return ok, f"{len(s['headings'])} headings"
    if "does not contain the substring" in t:
        sub = re.search(r"substring '([^']+)'", t).group(1).lower()
        d = s["fm"].get("description", "").lower()
        ok = sub not in d
        return ok, f"substring '{sub}' absent={ok}"
    if "token '" in t:
        tok = re.search(r"token '([^']+)'", t).group(1).lower()
        d = s["fm"].get("description", "").lower()
        ok = tok in TOKEN_RE.findall(d)
        return ok, f"'{tok}' in {' '.join(TOKEN_RE.findall(d))}"
    if "separator artifact" in t:
        in_fence = False
        for line in s["body"].splitlines():
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if re.match(r"^-{7,}\s*$", line):
                return False, "found '---------' outside a code fence"
        return True, "no separator artifact"
    if ("sections and" in t or "section and" in t) and "characters of body" in t:
        # "Body has at least N '##' sections and M+ characters of body"
        nsec, nchar = (int(x) for x in re.findall(r"\d+", t)[:2])
        ok = len(s["headings"]) >= nsec and s["chars"] >= nchar
        return ok, f"{len(s['headings'])} sections, {s['chars']} chars (need {nsec}/{nchar})"
    if "heading" in t and "'##" in t:
        # OR form: "Body contains a '## Steps' heading OR a '## Procedure' heading"
        if " or " in t and t.count("'##") >= 2:
            wants = re.findall(r"'##\s*([^']+)'", text)
            ok = any(any(w.strip().lower() == h.strip().lower() for h in s["headings"]) for w in wants)
            return ok, f"any of {wants} present={ok}"
        want = re.search(r"'##\s*([^']+)", text)
        if want:
            ok = any(want.group(1).strip().lower() == h.strip().lower() for h in s["headings"])
            return ok, f"heading '## {want.group(1)}' present={'yes' if ok else 'no'}"
        # generic "contains a '##' heading" form
        ok = bool(s["headings"])
        return ok, f"{len(s['headings'])} headings"
    if "heading for every heading present in" in t:
        src = re.search(r"in ([a-z0-9/_-]+)", t).group(1)
        srcdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), src)
        try:
            base_s = load_skill(srcdir)
        except Exception as ex:
            return False, f"cannot load source {src}: {ex}"
        missing = [h for h in base_s["headings"] if h not in s["headings"]]
        return not missing, ("missing: " + ", ".join(missing)) if missing else "all source headings present"
    if "description token recall vs baseline" in t:
        if not baseline:
            return True, "no baseline — skipped"
        bt = set(TOKEN_RE.findall(baseline["fm"].get("description", "").lower()))
        nt = set(TOKEN_RE.findall(s["fm"].get("description", "").lower()))
        recall = len(bt & nt) / len(bt) if bt else 1.0
        m = re.search(r">=\s*([\d.]+)", t)
        thr = float(m.group(1)) if m else 0.5
        return recall >= thr, f"recall={recall:.0%} thr={thr:.0%}"
    if "body size vs baseline" in t:
        if not baseline:
            return True, "no baseline — skipped"
        m = re.search(r"<=\s*([\d.]+)x", t)
        ratio = float(m.group(1)) if m else 1.30
        ok = s["chars"] <= baseline["chars"] * ratio
        return ok, f"{s['chars']}c vs base {baseline['chars']}c (<= {ratio}x)"
    return False, f"UNKNOWN ASSERTION: {text}"


def grade_case(case, skill_dir, baseline_dir, out_root):
    s = load_skill(skill_dir)
    baseline = load_skill(baseline_dir) if baseline_dir else None
    results = []
    for a in case.get("assertions", []):
        passed, ev = assert_one(a, s, baseline)
        results.append({"text": a, "passed": passed, "evidence": ev})
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    grading = {
        "assertion_results": results,
        "summary": {"passed": passed, "failed": total - passed, "total": total,
                    "pass_rate": (passed / total) if total else 0.0},
    }
    ws = os.path.join(out_root, f"eval-{case['id']}", "with_skill")
    os.makedirs(os.path.join(ws, "outputs"), exist_ok=True)
    timing = {"total_tokens": None, "duration_ms": None,
              "note": "skill-edit eval: mechanical check, no agent run"}
    open(os.path.join(ws, "grading.json"), "w").write(json.dumps(grading, indent=2))
    open(os.path.join(ws, "timing.json"), "w").write(json.dumps(timing, indent=2))
    # skill-creator eval-viewer schema: eval_metadata.json + a real outputs/ file
    open(os.path.join(ws, "eval_metadata.json"), "w").write(json.dumps(
        {"prompt": case.get("prompt", ""), "eval_id": case["id"]}, indent=2))
    ev = ["# Eval evidence", "", f"Prompt: {case.get('prompt', '')}", "", "## Assertions"]
    for r in grading["assertion_results"]:
        ev.append(f"- [{'PASS' if r['passed'] else 'FAIL'}] {r['text']} — {r['evidence']}")
    open(os.path.join(ws, "outputs", "evidence.md"), "w").write("\n".join(ev) + "\n")
    if baseline_dir:
        bws = os.path.join(out_root, f"eval-{case['id']}", "old_skill")
        os.makedirs(os.path.join(bws, "outputs"), exist_ok=True)
        open(os.path.join(bws, "grading.json"), "w").write(json.dumps(grading, indent=2))
    return grading


def run_eval(skill_dir, baseline_dir, iteration, workspace_root):
    ej = os.path.join(skill_dir, "evals", "evals.json")
    if not os.path.isfile(ej):
        print(f"no evals.json in {skill_dir}")
        return 0
    data = json.load(open(ej))
    out_root = os.path.join(workspace_root, f"iteration-{iteration}")
    os.makedirs(out_root, exist_ok=True)
    bench = {"skill_name": data.get("skill_name", os.path.basename(skill_dir)),
             "iteration": iteration, "cases": []}
    any_fail = False
    for case in data["evals"]:
        g = grade_case(case, skill_dir, baseline_dir, out_root)
        bench["cases"].append({"id": case["id"], "summary": g["summary"]})
        any_fail |= g["summary"]["failed"] > 0
        print(f"[eval {case['id']}] {g['summary']['passed']}/{g['summary']['total']} passed")
        for r in g["assertion_results"]:
            if not r["passed"]:
                print(f"    FAIL: {r['text']} — {r['evidence']}")
    open(os.path.join(out_root, "benchmark.json"), "w").write(json.dumps(bench, indent=2))
    return 1 if any_fail else 0


def selftest():
    d = tempfile.mkdtemp()
    good = '''---
name: demo-skill
description: "Use when demoing the eval harness gates."
license: Apache-2.0
---
# Demo
## When to Use
Do the thing.
## Verification
Run the check.
'''
    p = os.path.join(d, "demo-skill")
    os.makedirs(os.path.join(p, "evals"))
    open(os.path.join(p, "SKILL.md"), "w").write(good)
    open(os.path.join(p, "evals", "evals.json"), "w").write(json.dumps({
        "skill_name": "demo-skill",
        "evals": [{"id": 1, "prompt": "trim it", "expected_output": "still loadable",
                   "assertions": ["Frontmatter parses as YAML with a top-level 'name' key",
                                  "Frontmatter 'name' equals the directory basename 'demo-skill'",
                                  "Description starts with 'Use when' and is <= 200 characters",
                                  "license field is 'Apache-2.0'",
                                  "Body still contains at least one '##' heading",
                                  "No '---------' separator artifact appears outside a code fence"]}]}))
    assert run_eval(p, None, 1, os.path.join(d, "ws")) == 0

    bad = good.replace("name: demo-skill", "name: wrong").replace("# Demo", "# Demo\n---------")
    pb = os.path.join(d, "bad-skill")
    os.makedirs(os.path.join(pb, "evals"))
    open(os.path.join(pb, "SKILL.md"), "w").write(bad)
    open(os.path.join(pb, "evals", "evals.json"), "w").write(json.dumps({
        "skill_name": "bad-skill",
        "evals": [{"id": 1, "prompt": "trim it", "expected_output": "still loadable",
                   "assertions": ["Frontmatter 'name' equals the directory basename 'bad-skill'",
                                  "No '---------' separator artifact appears outside a code fence"]}]}))
    assert run_eval(pb, None, 1, os.path.join(d, "ws2")) != 0
    print("selftest OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", help="skill dir with evals/evals.json")
    ap.add_argument("--baseline", help="previous-version skill dir (old_skill)")
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--workspace", default=None, help="workspace root (default: <skill>-workspace)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        sys.exit(0)
    if not a.skill:
        print("need --skill <dir> (or --selftest)")
        sys.exit(2)
    ws = a.workspace or (a.skill.rstrip("/") + "-workspace")
    sys.exit(run_eval(a.skill, a.baseline, a.iteration, ws))
