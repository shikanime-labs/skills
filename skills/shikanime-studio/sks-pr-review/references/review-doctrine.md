# Review Doctrine (independent verdict)

The reviewer never verifies its own work. Two layers, both fail-closed:

1. **Self-review checklist** (the agent that wrote the diff) — a fast pre-scan
   before an independent pass. Caught issues are fixed by the author, not the
   reviewer.
2. **Independent reviewer subagent** — `delegate_task` with ONLY the diff +
   scan results. No shared context. Returns JSON; unparseable = FAIL.

## Self-review checklist

- [ ] No hard-coded secrets, API keys, credentials (see `security-scan.md`)
- [ ] Input validation at trust boundaries
- [ ] SQL/queries parameterized; no f-string/`.format` interpolation
- [ ] File ops validate paths (no traversal)
- [ ] External calls have error handling (I/O, network, DB)
- [ ] No leftover debug `print`/`console.log`
- [ ] No commented-out code
- [ ] Tests live with the owning unit (config in config specs, transport in
      client specs, domain in service specs); names describe behavior/ownership
- [ ] No AI-marker comments; commit/license/Nix/Go conventions honored
- [ ] Auth/JWT bound to client+audience; JWKS has timeout + cache strategy

## Independent reviewer contract

Dispatch with the diff inline and the static-scan results. Fail-closed rules:

- `security_concerns` non-empty -> `passed` must be false
- `logic_errors` non-empty -> `passed` must be false
- diff unparseable -> `passed` must be false
- only `passed=true` when BOTH lists empty

```json
{
  "passed": true,
  "security_concerns": [],
  "logic_errors": [],
  "suggestions": [],
  "summary": "one-sentence verdict"
}
```

SECURITY (auto-FAIL): hard-coded secrets, backdoors, data exfiltration, shell
injection, SQL injection, path traversal, `eval()`/`exec()` on user input,
`pickle.loads()`, obfuscated commands.

LOGIC ERRORS (auto-FAIL): wrong conditional, missing error handling for
I/O/network/DB, off-by-one, race conditions, code contradicts intent.

SUGGESTIONS (non-blocking): missing tests, style, performance, naming.

## Verdict mapping

`passed` + no blocking -> the human approves. Any blocking -> `REQUEST_CHANGES`.
The agent posts the review; it never clicks approve/merge on its own authority
beyond what `sks-pr-resolve` permits.
