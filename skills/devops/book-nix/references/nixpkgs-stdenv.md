# The Standard Environment (distilled from Nixpkgs Manual §chap-stdenv, §ssec-stdenv-dependencies)

## What stdenv gives you

- `stdenv` is the standard build environment. It automates the common
  `./configure; make; make install` flow — for such packages you write **no** build
  script at all.
- Use **`stdenv.mkDerivation`** (not the primitive `derivation`).

## Minimal derivation

```nix
stdenv.mkDerivation {
  name = "libfoo-1.2.3";
  src = fetchurl { url = "http://example.org/libfoo-1.2.3.tar.bz2"; hash = "sha256-…"; };
}
```

- Prefer **`pname` + `version`** (RFC 0035) so the version is reusable:

  ```nix
  stdenv.mkDerivation (finalAttrs: {
    pname = "libfoo"; version = "1.2.3";
    src = fetchurl { url = "http://example.org/libfoo-source-${finalAttrs.version}.tar.bz2"; hash = "sha256-…"; };
  })
  ```

  `mkDerivation` sets `name = "${pname}-${version}"` by default.

## Specifying dependencies (the critical distinction)

- `nativeBuildInputs` — executed **during the build**: tools on `$PATH` (cmake,
  pkg-config), setup hooks (makeWrapper), build-time interpreters.
- `buildInputs` — end up **copied/linked into the output** (runtime): libraries,
  runtime interpreters.
- The two criteria are **independent**. Example: Wayland needs `wayland` in
  `buildInputs` (runtime lib) *and* `nativeBuildInputs` (wayland-scanner runs at build).
- Test deps: `nativeCheckInputs` (test tools on `$PATH`, e.g. ctest, pytestCheckHook),
  `checkInputs` (libs linked into test executables). Only injected when
  `doCheck = true`.
- Propagated deps (`propagatedBuildInputs`): made available to all downstream
  consumers (used for Python). Use sparingly — obscures real inputs, can cause
  conflicts.

## Phases

- Build is split into overridable phases: unpack, patch, configure, build, install,
  fixup, … Override with `buildPhase = '' … '';` etc.
- Always wrap custom code with hooks:

  ```nix
  buildPhase = ''
    runHook preBuild
    gcc foo.c -o foo
    runHook postBuild
  '';
  ```

- Custom builder: `builder = ./builder.sh;` (stdenv sets up PATH from inputs), or
  define phase functions and call `genericBuild`.

## Tools provided by stdenv

GCC (C/C++), coreutils, findutils, diffutils, sed, grep, gawk, tar, gzip/bzip2/xz,
make, bash, patch. On **Linux**, also `patchelf`.

## Building inside nix-shell

```bash
cd "$(mktemp -d)"
nix-shell '<nixpkgs>' -A some_package
export out=$(pwd)/out
phases="unpackPhase patchPhase" genericBuild
phases="configurePhase buildPhase checkPhase" genericBuild
phases="installPhase fixupPhase installCheckPhase" genericBuild
```

- Note: shell env differs from sandbox (TMPDIR non-empty, outputs not writable);
  for faithful failures use `breakpointHook` + `nix-build --keep-failed`.
