# Nix Language (distilled from nix.dev/manual/nix/2.28/language)

## Properties (mental model)

- **Domain-specific**: built-ins integrate with the Nix store / derivations.
- **Declarative**: no sequential steps; dependencies established only through data.
- **Pure**: values don't change during computation; same input → same output.
- **Functional**: functions are values (passed, returned, assigned).
- **Lazy**: values computed only when needed.
- **Dynamically typed**: type errors surface at evaluation.

## Basic values

- String: `"hello world"`
- Multiline: `''  multi  line  string  ''` — strips common leading indentation;
  `"` and `\` are NOT special (good for shell code). Evaluates to `"multi\n line\n string"`.
- Comment: `# Explanation`
- String interpolation: `"hello ${ {a="world";}.a }"` → `"hello world"`;
  `"${pkgs.bash}/bin/sh"` → store path.
- Booleans: `true`, `false`. Null: `null`.
- Int `123`, float `3.141`.
- Path: `/etc`, `./foo.png` (relative to the file), `~/.config`.
- Lookup path: `<nixpkgs>` — resolved via `$NIX_PATH`.

## Compound values

- Attrset: `{ x = 1; y = 2; }`
- Nested set shorthand: `{ foo.bar = 1; }` ≡ `{ foo = { bar = 1; }; }`
- Recursive set: `rec { x = "foo"; y = x + "bar"; }` (attrs visible within).
- Lists: `[ "foo" "bar" ]`, `[ 1 2 3 ]`, `[ (f 1) {a=1;} [ "c" ] ]`.

## Operators

- `"foo" + "bar"` string concat; `1 + 2` int add.
- `"foo" == "f" + "oo"` (true); `"foo" != "bar"` (true).
- `!true` negation.
- `{ x = 1; }.x` attribute selection (→ `1`).
- `{ x = 1; }.z or 3` selection with default (→ `3`).
- `{ x = 1; } // { z = 3; }` merge (right wins).

## Control structures

- `if 1+1==2 then "yes!" else "no!"`
- `assert 1+1==2; "yes!"`
- `let x = "foo"; y = "bar"; in x + y`
- `with builtins; head [1 2 3]` — brings attrs of a set into scope (careful with
  shadowing).
- `inherit pkgs src;` → `pkgs = pkgs; src = src;`
- `inherit (pkgs) lib stdenv;` → `lib = pkgs.lib; stdenv = pkgs.stdenv;`

## Functions (lambdas)

- `x: x + 1`
- Curried: `x: y: x + y` ≡ `x: (y: x + y)`.
- Call: `(x: x + 1) 100` → `101`.
- Set pattern: `{ x, y }: x + y`; optional `{ x, y ? "bar" }`; ignore rest `{ x, y, ... }`.
- Bind whole set: `{ x, y } @ args:` or `args @ { x, y }:`.

## Builtins (selected)

- `import ./foo.nix` — load & return a Nix expression.
- `map (x: x + x) [1 2 3]` → `[2 4 6]`.

## Pitfalls

- Function application binds *looser* than list construction: wrap overrides in
  parens, e.g. `environment.systemPackages = [ (pkgs.emacs.override {…}) ];`.
- `rec` and `with` can cause surprising shadowing; prefer explicit.
