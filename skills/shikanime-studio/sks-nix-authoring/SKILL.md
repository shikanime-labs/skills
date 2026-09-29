---
name: sks-nix-authoring
description:
  "Use when authoring or editing Nix in a shikanime repo: nixfmt-sorted style,
  single-use let bindings, no explanatory comments, YAGNI on new options."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - nix
      - nixos
      - nix-darwin
      - style
      - sorting
      - shikanime-labs
    related_skills:
      - sks-delegate
      - sks-commit
      - sks-dev-workflow
      - sks-pr-review
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Nix Authoring

Write Nix in a shikanime repo (`machines`, `manifests`, and any other
flake-parts / nixpkgs consumer) the way the fleet already reads it: sorted,
minimal, no prose in the source, no option surface that only covers a case the
defaults already handle.

## When to Use

- Writing or changing `.nix` in a shikanime repo — profile modules, flake
  outputs, package wraps, kustomization renders, any Nix surface.
- Deciding whether a new option, wrapper, or helper is worth adding.
- Applying `nix fmt` and verifying the result did not corrupt a non-Nix file.

Don't use for: editing the YAML/Kubernetes side of a manifests app — that is
`sks-manifest-authoring`. Don't use for sops-encrypted secret files — that is
`sops-authoring` (and `nix fmt` must not touch `.enc.*`).

## The defaults that already cover most things

The repo norm is boring on purpose: the tooling enforces the mechanical pieces
and the reviewer enforces the YAGNI piece. Before you add anything, check that
the default stack does not already cover it:

- **Formatting** — `nix fmt` (treefmt) owns formatting. Do not hand-align, do not
  hand-sort keys, do not invent a custom style on top of it. If a file you touch
  is Nix, `nix fmt` it. If a file is not Nix, do not run `nix fmt` across it —
  see the gotcha about `.enc.*` and the broader `nix fmt` whole-tree cave in
  `sks-dev-workflow`.
- **Sorting** — sorted keys are the house style, enforced by `nix fmt`/treefmt
  where configured and by reviewer otherwise. Write sorted; do not write
  unsorted and promise to "sort later".
- **Comments** — explanatory comments inside `.nix` are out of fashion in these
  repos. The convention from machines is "no explanatory comments in `.nix`
  files". A comment that restates what the line does is noise; a comment that
  records WHY a non-obvious choice was made can earn its place, but prefer
  naming and structure over prose first. If the code is clear, the comment goes.
- **New options / new attrs** — add only when a real consumer needs a distinct
  knob. A option that duplicates a default, wraps another option with no added
  behavior, or exists "in case we need it" is tech debt, not insurance.

The rule of thumb: if the default already does it, do not add a layer.

## Style checklist (what the reviewer actually checks)

1. **Run `nix fmt` on the files you touched.** One scope at a time for nix
   repos that carry non-Nix files — a whole-tree `nix fmt` rewrites unrelated
   files and can corrupt `.enc.*` in manifests. Scope it:

   ```bash
   nix fmt apps/<app>          # nix files only in that tree
   ```

   For a single-file edit in a repo that is all-Nix (e.g. a profile module),
   `nix fmt <file>` is fine.
2. **Keys sorted in any record you write or extend.** If two or more keys share
   a parent, use a record literal with keys sorted; a single leaf under a shared
   parent uses dotted assignment. Pattern from machines:

   ```nix
   # single leaf under parent `foo`
   foo.bar = v;

   # two or more keys under `foo` → record literal, keys sorted
   foo = {
     bar = v1;
     baz = v2;
   };
   ```

   Do not mix the two styles inside the same parent haphazardly — pick the style
   that matches how many keys actually live under that parent.
3. **Inline single-use let bindings.** If a `let` binds exactly one use, inline
   it unless naming it makes the expression genuinely clearer. A binding that
   exists only to avoid repeating a long expression once is sometimes worth it;
   a binding that exists "to be tidy" for a single use is YAGNI.
4. **No explanatory comments. Name the intermediate instead.** A comment that
   exists only to label a chunk of a list or expression is a symptom that the
   chunk should be named. Prefer:

   ```nix
   let
     svcAccountResources = [ sa.yaml rbac.yaml ];
     probeResources = [ liveness.yaml readyness.yaml ];
   in  svcAccountResources ++ probeResources
   ```

   over a commented concatenation:

   ```nix
   # few stuffs related sa a b c
   [ sa.yaml rbac.yaml ]
   # other stuffs related probes y i
   ++ [ liveness.yaml readyness.yaml ]
   ```

   The name `svcAccountResources` carries what the comment would have said,
   and a reader does not have to match a comment to the lines beneath it.
   Comments that survive this refactoring — a name cannot capture a
   non-obvious WHY — are the rare justified ones; the rest are deleted.
5. **Single-responsibility functions and values.** When a derivation, function,
   or let-binding does two things that could be described with two names, split
   it. A value named for what it *is* (e.g. `baseImage`, `extraArgs`,
   `monitoringResources`) is cheaper to review than a value named for how it is
   *used* (e.g. `finalImage` with a body that also adds args). Split until each
   name answers "what is this?" in one breath; if the answer reads "this is X and
   also Y", it is two values.
6. **One logical change per commit.** A Nix refactor that also renames ten attrs
   and adds a new option and retires an old one is four changes. Split so the
   diff reads as one decision each.
7. **New option = real consumer.** Before adding an option, argument, or config
   knob, ask: is there a consumer that will use a non-default value here? If the
   answer is "maybe later", the option is premature. Default it, do not expose
   it.

## What not to add (YAGNI catalog)

These are the recurring over-additions this skill is here to cut. If you catch
yourself doing one, stop and ask whether the default already covers it.

- **A wrapper module that re-exposes another module's option with the same
  default.** That is one line that adds surface and zero behavior. Remove it.
- **A package wrap that only sets the default flags the upstream wrapper already
  sets.** If the upstream already builds what you want, use it directly.
- **A `let` that binds a value used once and exists only to shorten a line.**
  Inline it unless the name carries meaning the expression lacks.
- **A comment that restates the code.** Delete it.
- **A `with` import used to shave a few keystrokes across a wide scope.** Explicit
  is better than implicit here; `with` obscures where names come from. Prefer
  explicit references unless the scope is genuinely small and obvious.
- **A default that mirrors upstream default.** If the Nixpkgs default is already
  what you want, do not restate it as a local default — that is a future drift
  source.

## Repo shape differences (machines vs manifests Nix)

The style is the same; the surface differs.

- **machines-class flakes** (NixOS / nix-darwin / Home Manager, flake-parts +
  devlib): the flake carries sops-nix, the per-host `secrets/<host>.enc.yaml`,
  and the shared modules under `modules/`. When you touch sops-nix wiring, the
  sops side (recipients, templates, `sopsFile`) is a secret edit — involve
  `sops-authoring` for the `.enc.*` part. The Nix part is this skill.
- **manifests-class flakes** (kustomize / Flux render, kustomization YAML as Nix
  output): the Nix here generates YAML. Sorting and formatting still apply to the
  Nix; the generated YAML sorting and structure are the manifests skill's
  territory. Do not hand-edit the generated YAML to "fix" sorting — fix the Nix
  that produces it, then re-render.

## Verification

```bash
# Nix files you touched are fmt-clean
nix fmt -- --check   # or scoped: nix fmt <path>

# no explanatory comments left on the lines you added
grep -nE '^\s*# ' <file>.nix      # review the survivors; delete the obvious ones

# new option has a real consumer
grep -rn "<new-option>" .     # at least one non-default consumer, or drop it

# staged diff is only the Nix you intended
jj diff --git | grep -E '^diff --git a/.*\.nix'
```

## Pitfalls

- **`nix fmt` is whole-tree by default in these flakes.** A bare `nix fmt` in a
  repo that also carries non-Nix files rewrites everything treefmt owns and can
  corrupt `.enc.*`. Scope it to the Nix trees you touched. See
  `sks-dev-workflow` "Formatting: nix fmt + markdown".
- **`nix fmt` does not sort the way a human would sort a mixed record.** If
  treefmt's nix formatter is configured, it owns sorting; do not hand-sort around
  it. If it is not configured for a given repo, sorting is a reviewer check, and
  the written file should already be sorted.
- **A comment that survives `nix fmt` is not automatically a justified comment.**
  The formatter keeps it; the reviewer still asks why it exists. If the answer is
  "it explains the line", delete it.
- **Adding an option is cheap now and expensive later.** Every option is a
  contract: someone must document it, someone must test it, and someone must
  retire it if it becomes wrong. Only add it when a non-default value is actually
  in flight.

## See also

- `sks-delegate` — isolate this unit in a fresh jj workspace before editing.
- `sks-commit` — commit shape with the Automata co-author trailer.
- `sks-dev-workflow` — branch / push / landing; carries the
  `nix fmt` whole-tree caveat.
- `sks-manifest-authoring` — the YAML/kube side when the Nix generates manifests.
- `sks-pr-review` — the reviewer lens that enforces YAGNI on the PR.
