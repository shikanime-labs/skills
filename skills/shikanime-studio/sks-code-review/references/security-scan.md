# Security Scan (added lines only)

Run each against the working-copy diff. Any match = `blocking`.

```bash
jj diff -r @ | grep "^+\" | grep -iE "(api_key|secret|password|token|passwd)\s*=\s*['\"][^'\"]{6,}['\"]"
jj diff -r @ | grep "^+\" | grep -E "os\.system\(|subprocess.*shell=True|\beval\(|\bexec\("
jj diff -r @ | grep "^+\" | grep -E "pickle\.loads?\("
jj diff -r @ | grep "^+\" | grep -E "execute\(f\"|\.format\(.*SELECT"
```

Also check for: hardcoded secrets, SQL/Shell injection, path traversal, XSS
(`innerHTML = userInput`), and missing input validation at trust boundaries.
