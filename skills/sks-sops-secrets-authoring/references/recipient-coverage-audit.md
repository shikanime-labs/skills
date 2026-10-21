# Recipient coverage audit for a shared secret file

Loaded by `sks-sops-secrets-authoring` when verifying a SHARED `.enc.*`
file lists every consumer host's recipient. The per-file checks (decrypts,
recipient set present) live in the main flow.

Derive each consumer host's age recipient from its ssh host key and diff
against the ciphertext's own recipient list:

```bash
for h in <hosts>; do
  ssh-keyscan -t ed25519 "$h" 2>/dev/null | grep -v '^#' \
    | ssh-to-age
done | sort -u > /tmp/want
grep -o 'recipient: age1[0-9a-z]*' secrets/<shared>.enc.yaml \
  | awk '{print $2}' | sort -u > /tmp/got
diff /tmp/want /tmp/got   # empty = every consumer can decrypt
```

An offline host's known_hosts entry works as the ssh host key source too.
A non-empty diff names the host whose recipient is missing from the file.
