# Route audit: hostname dupes, hostname split, forbidden annotations

Run from the manifests repo root (adjust REPO below). Python 3, stdlib only.
Detects, across all gateway route/annotation YAML:

1. Duplicate hostname entries inside a single hostnames list (survives
   `kustomize build` — real defect).
2. Hostname split violations: `overlays/nishir/` patches must carry only
   `i.shikanime.studio`; `overlays/nishir-tailnet/` only `taila659a.ts.net`.
3. Forbidden annotations (e.g. `tailscale.com/auth` added without intent).

```python
import re, subprocess, collections

REPO = "."  # manifests repo root
out = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                     cwd=REPO).stdout.splitlines()
problems = []
for f in out:
    if not f.endswith(".yaml"):
        continue
    try:
        text = open(f"{REPO}/{f}").read()
    except Exception as e:
        problems.append(f"{f}: unreadable ({e})")
        continue
    if "tailscale.com/auth" in text:
        problems.append(f"{f}: tailscale.com/auth present")
    if "taila659a" not in text and "i.shikanime.studio" not in text:
        continue
    for i, doc in enumerate(text.split("\n---")):
        hosts = re.findall(
            r"^\s+- ([\w.-]+\.(?:taila659a\.ts\.net|i\.shikanime\.studio))\s*$",
            doc, re.M)
        dupes = [h for h, c in collections.Counter(hosts).items() if c > 1]
        if dupes:
            problems.append(f"{f} doc{i}: duplicate hostnames {dupes}")

for f in out:
    if not f.endswith("patch-httproute.yaml"):
        continue
    text = open(f"{REPO}/{f}").read()
    nf = "/" + f  # git ls-files paths carry no leading slash
    if "/overlays/nishir/" in nf and "taila659a.ts.net" in text:
        problems.append(f"{f}: tailnet hostname in nishir overlay")
    if "/overlays/nishir-tailnet/" in nf and "i.shikanime.studio" in text:
        problems.append(f"{f}: public hostname in nishir-tailnet overlay")

print("AUDIT CLEAN" if not problems else "\n".join(problems))
```

## Batch dedupe of repeated hostname lines

Same-file fix for the dupes above — collapse two consecutive identical
hostname lines into one:

```python
import re, subprocess
out = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.splitlines()
pat = re.compile(r"^(    - [\w.-]+\.taila659a\.ts\.net)\n\1\n", re.M)
for f in out:
    if f.endswith("patch-httproute.yaml") and "nishir-tailnet" in f:
        text = open(f).read()
        new, n = pat.subn(r"\1\n", text)
        if n:
            open(f, "w").write(new)
            print(f, "deduped", n)
```

Always follow with `kustomize build` on every touched overlay and a fresh
audit run before pushing.
