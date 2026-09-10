# CLI: cmctl & Controller Flags

## cmctl

Standalone binary (moved to `github.com/cert-manager/cmctl`; cert-manager 1.14
was last release with the bundled `cert-manager-ctl`). Install:
`brew install cmctl`, download from releases, or `go install
github.com/cert-manager/cmctl/v2@latest`.

### Commands

- `cmctl status certificate <name> -n <ns>` — full status dump (Certificate,
  CR, Secret, Issuer, ACME Order/Challenge). Primary troubleshooting command.
- `cmctl renew <name>` — force renewal. Flags: `--all`, `-A/--all-namespaces`,
  `-l/--selector`.
- `cmctl approve|deny <cr> -n <ns> --reason --message` — approve/deny a
  CertificateRequest (internal approver auto-approves unless disabled via
  `--controllers=*,-certificaterequests-approver`).
- `cmctl create certificaterequest <name> --from-certificate-file cert.yaml
  --fetch-certificate --timeout 20m` — create a CR from a Certificate manifest;
  writes key/cert to local files (not into Kubernetes).
- `cmctl convert -f cert.yaml` — convert manifest between API versions
  (`--output-version`, `-o`).
- `cmctl check` — check cert-manager components.
- `cmctl inspect` — details on cert-related resources.
- `cmctl version` — CLI + deployed cert-manager version.
- `cmctl upgrade migrate-api-version --qps 5 --burst 10` — migrate pre-v1 CRs.

### Experimental (`cmctl x`)

- `cmctl x install [--set ...] [--dry-run > out.yaml]` — install cert-manager
  (same Helm params); `--dry-run` templated manifest to stdout.
- `cmctl x uninstall [--namespace] [--dry-run]` — safe uninstall, keeps CRDs
  (cmctl v2).
- `cmctl x create csr -f cert.yaml <name> [-w]` — create a
  CertificateSigningRequest; `kubectl certificate approve <name>` needed unless
  a custom approver runs.

## Controller flags (subset, most-used)

Set via Helm values or the controller args. Full set:
`cert-manager.io/docs/cli/controller/`.

- `--cluster-resource-namespace` (default `cert-manager` in Helm; `kube-system`
  in raw flag docs — verify). Where ClusterIssuer secrets live.
- `--max-concurrent-challenges` (default 60).
- `--dns01-check-retry-period` (default 10s) — applies to HTTP01 too.
- `--dns01-recursive-nameservers` / `--dns01-recursive-nameservers-only` — for
  DNS-constrained envs.
- `--certificate-request-minimum-backoff-duration` (1h) /
  `--certificate-request-maximum-backoff-duration` (32h) — exponential backoff
  on failed CRs.
- `--enable-certificate-owner-ref` — delete Secret when Certificate is deleted.
- `--acme-http01-solver-*` — image, resource limits, non-root, runtime class.
- `--namespace` — limit cert-manager to one namespace (disables ClusterIssuers).
- `--controllers=*` enable all; `*,-foo` disable `foo`.
- `--config` — path to a `ControllerConfiguration` object (e.g. set
  `maxConcurrentChallenges` via config file).

## Feature gates (`--feature-gates`)

Notable: `ExperimentalGatewayAPISupport` (BETA, default true as of 1.15),
`ListenerSets` (ALPHA), `LiteralCertificateSubject` (BETA, default true),
`NameConstraints` (BETA, default true), `OtherNames` (BETA, default true),
`StableCertificateRequestName` (BETA, default true), `ACMEUseARI` (ALPHA),
`ValidateCAA` (ALPHA), `ServerSideApply` (ALPHA).
