---
name: sks-sops-secrets-authoring
description:
  "Use when editing sops-encrypted files: decrypt-and-edit workflow,
  re-encryption guards, and sops-nix secret plumbing."
version: 0.3.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - sops
      - sops-nix
      - secrets
      - encrypted-yaml
    related_skills:
      - sks-commit
      - sks-dev
      - sks-pr
      - sks-pr-review
      - sks-delegate
platforms:
  - linux
  - macos
  - windows
---

# sops Secret Editing

Edit sops-encrypted files (`*.enc.yaml`, `*.enc.env`, `*.enc.conf`) in the
org repo without losing encryption coverage or corrupting the wire format
so `sops-nix` / Flux can still consume it on the target.

For org-specific conventions (repo names, recipient keys, commit trailers),
read `references/shikanime.md` when operating in a shikanime org.

## When to Use

- A task reaches for a `secrets/*.enc.*` or any `.enc.*` file in the org
  repo — most often the fleet-config repo (per-host
  `secrets/<host>.enc.yaml`) or the render repo (fleet `*.enc.env` /
  `*.enc.conf`). Concrete repos: `references/shikanime.md`.
- The diff is a secret-value change, a key add/remove, or a structural edit to
  an encrypted file.
- You must verify the file still decrypts and still carries the right recipient
  set after the edit.

Don't use for: editing the Nix module or kustomization that *references* a secret
path (`sopsFile = ...`, `secretGenerator` key) — that is ordinary Nix / YAML, no
sops toolchain involved. Use `sks-dev` for the surrounding PR/landing
lifecycle.

## What changes between repos

The sops toolchain is the same; the recipient set, file shape, and consuming
side differ. Concrete org repos and recipient key names live in
`references/shikanime.md`.

|  Repo class         | File shape              | Recipient model                          | Consumer           |
|  ------------------ | ----------------------- | ---------------------------------------- | ------------------ |
|  fleet-config       | `secrets/<host>.enc.yaml` | per-host age key; no repo `.sops.yaml` | `sops-nix` on that host |
|  render             | `*.enc.env`, `*.enc.conf` | multiple fleet age recipients; no repo `.sops.yaml` | Flux `sops` decrypt |

The generic edit flow below covers both. The fleet render layer — exact
recipient keys, the devenv `sops` wrapper trap, INI store rules, the
`formatForPath` binary-store trap, and the `;` corruption — lives in
`references/sops-manifests.md`; read it when the target is
the render repo or the file is `*.enc.env` / `*.enc.conf`.

## Prerequisites

- `sops` on `$PATH`. In the fleet-config repo `nix develop` already carries
  it; on Darwin `brew install sops` is the standalone path.
- An age (or PGP/KMS) key that is a recipient of the file you are editing. If
  `sops` cannot decrypt the file, stop and report
  `BLOCKED: sops cannot decrypt <path>` with the error — not a guessed key.
- For fleet render files: the fleet age recipients (exact keys in
  `references/shikanime.md`) and the unwrapped
  `/nix/store/*-sops-*/bin/sops` binary — the devenv `sops` alias is
  wrapped and forces a single recipient, breaking Flux. Full recipe in
  `references/sops-manifests.md`.

## The object

A sops-encrypted file is **not a plain YAML/env file that happens to look garbled**.
The encrypted bytes are wrapped inside the file, and two classes of edits exist:

- **Structure-visible edits** — adding/removing a top-level key, changing a
  non-secret value, reordering — where you read cleartext and the ciphertext
  parts stay intact.
- **Deep edits** — changing a value under an encrypted subtree — where you must
  re-encrypt that subtree so the consuming side still sees valid encrypted
  material at the expected path.

Treat the file as an opaque encrypted blob you open only through `sops`, never as
a plaintext file you edit in an ordinary editor. The two failure modes that burn
are (1) editing plaintext and committing it, and (2) rewriting the file in a way
that drops or relocates the `sops` metadata block so the decrypt side no longer
knows which key covers which subtree.

## Workflow

### 1. Inspect before you touch

```bash
sops --decrypt secrets/<host>.enc.yaml >/dev/null && echo "decrypts" || echo "BLOCKED"
sops secrets/<host>.enc.yaml | head -40          # metadata + cleartext head
```

- Confirm decrypt works first. A file that decrypts but whose metadata block is
  malformed is a different failure than a file you lack a key for — both are
  blockers, but the recovery differs.
- Read the sops metadata (`sops:` key lists: `sops_age`, `sops_pgp`, `sops_kms`)
  so you know which keys are listed as recipients before you change anything.

### 2. Edit through sops, not a plain editor

```bash
sops secrets/<host>.enc.yaml
```

`sops` opens the decrypted content in `$EDITOR`; on save it re-encrypts using the
file's existing recipient set unless you override it. This is the normal path for
structural or value edits.

For non-interactive edits where an editor is not appropriate:

```bash
sops -d secrets/<host>.enc.yaml | \
  yq e '.some.path = "new value"' - | \
  sops -e -i secrets/<host>.enc.yaml
```

- Decrypt → transform → re-encrypt in one pipeline. Never write the decrypted
  intermediate to disk.
- Machine-driven structural merges (adding a whole resource pulled from
  elsewhere, e.g. a live k8s object) cannot stay in one pipe. The validated
  shape: decrypt to a /tmp intermediate with `--output-type json`, merge with
  `jq`, encrypt with `--input-type json --output-type yaml`, then validate by
  decrypting the NEW file with explicit `--input-type yaml --output-type json`
  and `cmp` against the sorted JSON of the intended plaintext (sorted
  canonical form keeps key order from masking real diffs). Purge the
  intermediates immediately — see the purge pitfall below.
- `-i` writes back in place; omit it to preview encrypted output on stdout.

### 3. Re-encryption recipients

When you add a new secret that a host or operator needs to read, the file's
recipient list must include a key that host/operator holds.

- An `age` recipient is an `AGE-SECRET-KEY-…` public key derived from the
  holder's secret key. Machines per-host files carry `sops_age__*-*` entries for
  that host's key; shared secrets carry every consuming party's recipient.
- Adding a recipient without removing the old one is the safe direction. Removing
  a recipient from a file still in use by another host is an availability bug, not
  cleanup.
- When you rewrite an `.enc.*` from a decrypted stream, explicitly carry the
  recipient set forward. The safe default is *not* to override recipients and let
  `sops` re-encrypt against the file's existing metadata; override only when you
  have verified the new recipient set is a superset of the old one for every live
  consumer.

For fleet render files specifically: use the unwrapped sops binary and the
comma-joined fleet age recipients exactly as in
`references/sops-manifests.md` — the devenv wrapper and the
wrong-recipient path break Flux.

### 4. `.enc.env` and `.enc.conf` are not YAML

These carry flat env-var-style or INI-style secrets, not YAML structure.
Treating them like YAML leads to brittle rewrites.

- Decrypt to verify: `sops -d secrets/<name>.enc.env`.
- Edit with `sops -e -i` only after you have confirmed the cleartext line set and
  the recipient list.
- For INI files (`*.enc.conf`): pass `--input-type ini --output-type ini` on
  encrypt AND decrypt — the flags are symmetric; one-sided flags silently
  round-trip through the JSON store. Full detail in
  `references/sops-manifests.md`.
- Deleting a key from an `.enc.env` is not complete until you have checked every
  consumer that reads that variable — a consumer that still references the now-
  missing variable gets an empty string or a mount error, not a loud failure.

### 5. sops-nix plumbing (fleet-config repo)

In the fleet-config repo, hosts consume secrets through `sops-nix`:

- Each host's flake config points `sops.defaultSopsFile` at its own
  `secrets/<host>.enc.yaml`. There is no repo-owned single `.sops.yaml` governing
  all hosts — each host file carries its own sops metadata, and `sops` resolves
  recipients from that metadata at edit/decrypt time.
- Some hosts additionally use `sops.templates.*` to materialize decrypted config
  fragments into the store. When you add a new secret a template wants to
  reference, the template and the secret file must be added in the same unit
  of work — a secret with no template is dead storage, a template with no
  secret is a deploy-time failure.

### 6. Commit and verify

1. Verify the file still decrypts after the edit:

   ```bash
   sops --decrypt secrets/<host>.enc.yaml >/dev/null && echo ok
   ```

2. Confirm the recipient set you expect is present:

   ```bash
   sops secrets/<host>.enc.yaml | grep -A2 '^sops:'
   ```

3. Commit per `sks-commit` with the org co-author trailer (org value in
   `references/shikanime.md`). A secret edit
   often pairs with a module edit (`sopsFile` path, template, systemd unit that
   reads the decrypted path) — keep them in the same commit when they are one
   logical change, not a secret commit followed by a plumbing commit that lands
   later and leaves the host between states.
4. No `nix fmt` / treefmt on `.enc.*` files. The formatter doesn't know the file
   is sops-wrapped and can corrupt the wire encoding or the metadata block.
   Exclude `secrets/*.enc.*` from formatting. Never run a formatter across a
   checkout that has a dirty secret file.

## Pitfalls

- **`nix fmt` / treefmt on `.enc.*` corrupts the file.** They treat it as an
  arbitrary file and may reformat the encrypted material or the metadata block.
  Exclude `secrets/*.enc.*` from formatting. Never `nix fmt` a checkout with a
  dirty secret file.
- **Don't decrypt to a plaintext file and edit that.** The plaintext either gets
  committed by accident or left on disk. Always `sops -e -i` or edit through
  `sops` so the only on-disk artifact is the encrypted file.
- **Adding a recipient is safe; removing one is not, unless you verified no live
  consumer needs it.** A host whose key you removed from a shared secret can no
  longer decrypt it after the next rollout — and that host may be the one you are
  on, with no backup key.
- **A file that decrypts locally can still fail on the target.** Local `sops -d`
  can succeed with a key you hold while the target host, which holds a different
  key, fails — because the `sops` metadata block doesn't list the target's
  recipient. Check the recipient set, not just local decrypt.
- **`.enc.env` deletion is a consumer-side change, not just a file edit.** The
  secret file dropping a key does not remove the key from the units that reference
  it; those units must be updated in the same unit of work.
- **sops cannot always decrypt from stdin in every configuration.** When a
  consumer expects a path and you hand it a stream, the plumbing breaks. Prefer
  path-based edits and let `sops-nix` materialize the decrypted path; don't
  refactor a `sopsFile` consumer to read from stdin without testing the target.
- **Direnv flakes and sops creation rules don't mix trivially.** If the repo's
  `.envrc` or a flake-driven dev shell tries to set up sops creation rules, the
  encrypted file's own metadata governs re-encryption — not the dev-shell wiring.
  Don't assume a dev-shell setup step re-encrypts correctly; verify with
  `sops -d` after.
- **fleet render: the devenv `sops` wrapper forces a single recipient.**
  Always locate and use the unwrapped `/nix/store/*-sops-*/bin/sops`
  binary and pass the fleet age recipients exactly once. See
  `references/sops-manifests.md`.
- **Renamed/extension-less files defeat sops format sniffing.** Decrypting
  `file.enc.yaml.new` (any non-canonical extension) with format flags
  omitted yields EMPTY output with exit 0 — a validation that silently
  "passes" on garbage. Pass `--input-type`/`--output-type` explicitly on
  every decrypt/encrypt of a renamed intermediate, and never suppress
  stderr on a validation decrypt: a pipe's rc comes from its LAST command,
  so `sops -d f | jq` reports success even when sops emitted nothing.
- **Keep the plaintext purge a standalone command.** Batching
  copy+verify+`rm` of plaintext intermediates into one shell line gets
  approval-blocked as one unit — a denial then strands every artifact AND
  blocks the harmless copy. Copy and verify in their own call; issue the
  `rm` of the named /tmp files alone; on denial, halt and enumerate the
  stranded artifacts for the user instead of retrying.

## Verification

```bash
# decrypts cleanly
sops --decrypt secrets/<host>.enc.yaml >/dev/null && echo ok

# recipient coverage audit for a SHARED file: derive each consumer host's
# age recipient from its ssh host key and diff against the ciphertext's
# own recipient list (offline host: its known_hosts entry works too)
for h in <hosts>; do
  ssh-keyscan -t ed25519 "$h" 2>/dev/null | grep -v '^#' \
    | ssh-to-age
done | sort -u > /tmp/want
grep -o 'recipient: age1[0-9a-z]*' secrets/<shared>.enc.yaml \
  | awk '{print $2}' | sort -u > /tmp/got
diff /tmp/want /tmp/got   # empty = every consumer can decrypt

# recipient set matches expectation (age example)
sops secrets/<host>.enc.yaml | grep -E '^sops_age' | sort

# no plaintext secret file accidentally on disk
git status --porcelain secrets/ | grep -v '\.enc\.'

# staged diff is only the encrypted file(s) + their plumbing
jj diff --git | grep -E '^diff --git a/.*\.enc'
```

## See also

- `sks-commit` — commit style with the org co-author trailer (org
  value in `references/shikanime.md`).
- `sks-dev` — branch / push / landing discipline.
- `references/sops-manifests.md` — the fleet render layer: recipient
  keys, devenv wrapper trap, INI store rules, the `formatForPath`
  binary-store trap, and the `;` corruption.
- `sks-pr` — open the PR from the pushed bookmark.
- `sks-pr-review` — review a secret-swap PR before approving.
- `sks-delegate` — isolate this unit in a fresh jj workspace before editing.
