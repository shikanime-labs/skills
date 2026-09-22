# SOPS on the manifests repo: recipients, INI store, Flux traps

Scoped to `shikanime-labs/manifests` secrets (`*.enc.env`, `*.enc.yaml`,
`*.enc.conf`). The generic sops edit recipe lives in the
`sops-encrypted-yaml-edit` skill; this file is the manifests-fleet layer.

## Recipient discipline

Secrets are encrypted to the THREE fleet age recipients (telsha / nixtar /
nishir). Flux decrypts fine with this set. The devenv `sops` wrapper /
`devlib:sops:updatekeys` re-encrypt to the WRONG recipients and BREAK Flux —
use the unwrapped binary and the exact list below.

```bash
SOPS_AGE_KEY="$HOME/.config/sops/age/keys.txt" sops decrypt <file> > /tmp/plain.env
unset SOPS_AGE_KEY SOPS_AGE_KEY_FILE          # wrapper must not re-add wrong recipients
# three fleet age recipients, comma-joined; pass EXACTLY ONCE
R1='age17q5ljstyzkvqtejwfnyf5jvqduars2yauw7vtgu5fcf54tm2jf0sspvt3c'
R2='age1x9v4ps90txy9mk4392uya93tyzx40te4dvns4chg5s6q8mfy03ns74jpay'
R3='age1f4yuh4j3gqafjduusfpxz3na9xtwth9s6gznq043mfex0zglp5jqkkdm64'
/nix/store/*-sops-*/bin/sops encrypt --age "$R1,$R2,$R3" \
  /tmp/plain.env > /tmp/plain.env.new
# roundtrip-validate BEFORE replacing; live ciphertext survives any failure
SOPS_AGE_KEY="$HOME/.config/sops/age/keys.txt" sops decrypt /tmp/plain.env.new \
  | cmp -s - /tmp/plain.env && mv /tmp/plain.env.new <file>
rm -f /tmp/plain.env
```

- Locate the unwrapped binary via `/nix/store/*-sops-*/bin/sops` — the
  devenv `sops` alias is wrapped and forces a single recipient, ignoring
  `--age`.
- `--age` repeated collapses to the LAST value in this sops build — pass
  EXACTLY ONE `--age` (the comma-joined three).
- No repo `.sops.yaml` (user directive) — recipients live only in ciphertext
  metadata. sops auto-grows the file: an all-plaintext `--age` encrypt
  without a matching creation rule encrypts EVERY key and adds its own mac.
  To apply repo rules without devenv, copy the exact rule from `flake.nix`
  into a scratch `.sops.yaml` and encrypt in place at a matching path.
- Rules match the INPUT path — encrypt in-repo, never copy plaintext from
  /tmp to a non-matching path (skill: `sops-encrypted-yaml-edit`).
- Validate before pushing: local `sops decrypt` succeeds AND
  `kustomize build <overlay>` exits 0 (rendered Secret name matches the
  HelmRelease / BSP `valuesFrom.name` via the overlay `namereference`
  rewrite).

## Flux emit-format trap (extension-driven, verified PR #2157)

Flux decrypts a Secret field when the data contains a format marker
(`[sops]` for INI), but picks the OUTPUT format from the SECRET DATA KEY
EXTENSION via `formatForPath` (kustomize-controller internal/decryptor):
`.ini` → ini; unrecognized extensions (`.conf`, `.txt`, bare names) →
BINARY store → decrypt fails with `error emitting binary store: no binary
data found in tree` REGARDLESS of file content.

Fix: rename the kustomization `secretGenerator` key to a `.ini` suffix
(`qBittorrent.ini=qbittorrent/qBittorrent.enc.conf`) and project the runtime
filename back via Secret volume `items:` (`key: qBittorrent.ini`, `path:
qBittorrent.conf`) — the app keeps its real config filename.

Diagnose live:
`kubectl get kustomization <k> -o jsonpath='{.status.conditions}'` —
decryption failures show Ready=False + `BuildFailed` events, and
`lastAppliedRevision` lagging `lastAttemptedRevision` means the app has NOT
reconciled since the breakage (stale live config).

## INI store rules (symmetric, extension-driven)

- INI files (qBittorrent `config.enc.conf`, PR 2133): pass
  `--input-type ini --output-type ini` on encrypt AND on decrypt — the
  flags are SYMMETRIC. One-sided flags silently round-trip through the JSON
  store and emit `"DEFAULT": {}` JSON a QSettings app cannot parse.
- Decrypt ini OUTPUT still needs `--output-type ini`; the JSON default
  errors "error emitting binary store".
- Verify round-trips with `decrypt --output-type json` (true store view),
  never by eyeballing ini output.
- Keys containing a literal backslash (qBittorrent `WebUI\Password_PBKDF2`)
  need the regex `\\` in `encrypted_regex` — FOUR backslashes in a Nix
  double-quoted string. Compute escape counts, never eyeball.

## PARMENIDES RULE — the sops INI store corrupts `;`

Its parser treats a `;` as a line continuation: any plaintext value
containing one gets split at the `;` and the store rejoins the halves with a
NEWLINE (verified empirically: `"a;b"` stores as `"a\nb"`; Qt quotes and
backslash-escapes do NOT survive). If a live config key carries `;`
(qBittorrent `WebUI\ServerDomains`), TWO lossless forms exist — re-verified
2026-09-04, sops 3.13.3, PR #2155:

1. Ciphertext: add the key to `encrypted_regex` (base64 has no `;`).
2. BACKTICK-quote the value in the plaintext (`key = \`"a; b"\``):
   go-ini treats backtick-quoted values as RAW — the `;` survives encrypt
   AND decrypt intact, store stays INI. Double quotes and `\;` split;
   backticks are the only inline quoting that holds.

## Pull-the-live-config pattern (2026-09-03 user directive)

Seed from the live pod and keep live values in the seed — the seed IS the
GitOps source; restart converges the PVC to Git, so rotations land via the
repo, never via the WebUI. Verify the pull byte-for-byte after Qt-quote
normalization (strip surrounding `"`): a diff of quoted vs unquoted strings
is normal; a length mismatch minus the quotes is real drift.
