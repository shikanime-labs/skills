# Supply Chain and Release Hunting

Use when the target resolves dependencies, builds from untrusted
contributions, runs CI, creates release artifacts, signs or promotes
builds, loads plugins, or updates deployed software — every trust handoff
from source and dependency to the artifact a user runs.

## Core Discipline

- A mutable or known-vulnerable dependency is not a finding by itself.
  Show who can influence resolution, which build consumes it, and what
  execution or release boundary follows.
- Follow integrity across every handoff: source identity, resolved
  inputs, build worker, artifact identity, test result, signature and
  attestation, promotion, update consumer.
- CI configuration is authorization code. Establish which event triggered
  a workflow, whose code runs, which secrets and tokens exist, and what
  it may publish or mutate.
- A checksum fetched from the same untrusted location as the artifact
  establishes no independent integrity. Identify the trusted root and
  the failure behavior.
- `confirmed` for in-repo control-flow failures with bounded local
  validation. Branch protection, hosted-runner, registry, signing-service,
  or production promotion facts that are not observable are
  `needs_validation`.

## Dependency and Build-Input Classes

- **Namespace and source confusion**: resolver configuration selecting an
  unintended public or private namespace, fallback registry, mirror, or
  source URL. Review package names, source priority, lockfile and
  checksum use, alternate build files, platform-specific resolution,
  first-install versus update behavior.
- **Mutable and unbound inputs**: builds consuming branches, tags,
  unverified submodules, downloaded tools, generated assets, remote
  includes, floating CI actions, or container tags whose content changes
  without source review. Require a lower-trust writer and a path into
  trusted build output; reproducibility alone does not prove
  authenticity.
- **Generated-source provenance gaps**: schemas, vendored archives,
  generated clients, localization, or binary blobs producing executable
  content without the review and integrity gate source gets. Compare
  local regeneration with committed output; verify who controls input
  and generator.
- **Build-context inclusion**: secrets, local configuration, repository
  metadata, test fixtures, or developer artifacts entering a package or
  image because the build context exceeds intended release inputs.
  Confirm the artifact exposes a real credential, private data, or
  privileged configuration.

## CI and Automation Classes

- **Untrusted code in a privileged workflow**: a pull request, issue
  comment, fork, dependency update, or external event running
  contributor-controlled code with protected secrets, write tokens,
  deployment authority, or a trusted runner. Compare trigger type,
  checkout ref, approval gate, environment protection, permission
  narrowing. Do not assume repository-host defaults absent from source.
- **Workflow command and expression confusion**: attacker-controlled
  branch names, commit messages, issue fields, artifact names, or matrix
  values entering shell commands, template expressions, paths, or
  privileged workflow inputs without canonical validation.
- **Cache and artifact trust mixing**: a lower-trust job populating a
  cache, artifact, workspace, or output that a higher-trust job later
  restores and executes or releases. Review cache keys and namespaces,
  producer identity, digest binding, retention, and whether promotion
  re-resolves by mutable name.
- **Automation identity overreach**: CI jobs holding permissions beyond
  the operation, repository, environment, or duration needed, with
  untrusted inputs selecting the affected resource. Missing least
  privilege alone is hardening; require a reachable privileged action.

## Release and Update Classes

- **Build-to-promotion substitution**: tests, review, signature, and
  publication referring to mutable tags, filenames, channels, or IDs
  rather than the same immutable digest. Check every copy, repack,
  architecture merge, and provenance step between build and release.
- **Authorization and signing-policy gaps**: a release or signature
  accepted from the wrong workflow, repository, branch, environment, key
  role, or threshold; identity claims inside attestations the consumer
  never validates. Rotation, expiry, and revocation must fail closed
  where policy requires.
- **Update metadata and rollback confusion**: an updater authenticating
  payload bytes but not version, product, platform, channel, target path,
  expiry, or rollback state; metadata and payload from different
  transactions; non-atomic installation and recovery. A signature API
  call without policy binding is incomplete.
- **Plugin trust expansion**: an extension package gaining host authority
  beyond its declared scope; a lower-trust publisher replacing another
  publisher's identity; install and update hooks running before
  authenticity and capability checks. Intended installation of
  same-user plugins is not a privilege boundary.

## Moves and Validation

Walk backward from a released digest or installed update to every source,
generated input, credential, worker, cache, test result, and
authorization decision. Compare untrusted and protected workflow events
side by side, marking each persisted channel crossing and requiring
immutable identity plus producer trust. Review revoked key, failed
download, missing attestation, partial platform release, rollback, and
registry outage paths — the failure policy is part of release integrity.

Before reporting: name the lower-trust actor, the controllable source,
cache, artifact, or metadata, the consuming trusted job or updater, and
the resulting unauthorized publication, code inclusion, secret
disclosure, or privileged execution. Prove artifact identity across the
broken handoff — a different mutable name or unbound digest must reach a
real consumer. Verify package-manager, repository-host, registry, and
signing defaults for the pinned version; unknown hosted controls are
`needs_validation`. Keep local validation bounded: harmless fixture
repositories, dummy credential markers, local registries, non-production
namespaces; never publish or alter a real release.
