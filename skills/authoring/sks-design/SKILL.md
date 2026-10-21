---
name: sks-design
description:
  "Use when designing or redesigning an interface — landing page, app screen,
  dashboard, deck, or report — with a taste anchor, a real component system,
  and screenshot verification."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - design
      - ui
      - ux
      - frontend
      - visual
      - redesign
    related_skills:
      - sks-summary
      - sks-adversarial
      - sks-skill-authoring
      - sks-curate
      - sks-dev
platforms:
  - linux
  - macos
  - windows
---

# Interface Design

Design is a routed process, not a one-shot generation. This skill fixes the
surface and the taste before it touches color, composes inside the project's
real component system, runs an anti-slop audit, and closes only after
screenshots prove the result.

The heavy design libraries are optional accelerants. When the harness has
`claude-design`, `popular-web-designs`, or `design-md`, load them by name:
`claude-design` for process and critique, `popular-web-designs` for a
matching system, and `design-md` for the token spec. When they are absent,
use `references/design-loop.md` and `references/anti-slop.md` as the
fallback.

## When to Use

- A new landing page, app screen, dashboard, deck, or report.
- A redesign or restyle: "less corporate", "more playful", "like Ko-fi".
- A design review where the output must be checked against a named direction.
- Not for backend work, pure refactors, or copy-only edits. Route code work
  to `sks-dev`; route prose to `sks-text-authoring`.

## Procedure

1. **Name the surface archetype.** Choose one: Monitor, Operate, Compare,
   Configure, Decide/Learn, Explore, or Command/Inspect. Write one sentence:
   "This is a [archetype] surface because [user job]."
   Monitor surfaces use dense rows, sparklines, and status pills.
   Decide/Learn surfaces can use a hero. Check: the archetype is named
   before any color or type token.

2. **Anchor taste.** If the user gave a reference, extract 6-10 tokens:
   palette, type pair, spacing scale, radii, elevation, motion, and density.
   If not, offer three named directions from `references/design-loop.md` and
   pick one. Load `claude-design`, `popular-web-designs`, and `design-md`
   when installed. Check: a one-paragraph direction plus a token table
   exists.

3. **Choose the project system.** Use the real component library and theme
   tokens. Theme Astryx, shadcn, Chakra, or the repo's system; do not build a
   parallel CSS system for primitives. Check: the component imports and theme
   file are named, and no new global CSS re-implements a primitive.

4. **Compose before decorating.** Lay out one primary action, one reading
   path, and one visual anchor. For a redesign, state what must be preserved,
   choose `Refinement`, `Layout Restructure`, or `Full Redesign`, and name
   the single biggest source of mediocrity. Check: the layout reads in
   grayscale, before color.

5. **Run the anti-slop audit.** Apply `references/anti-slop.md`: no default
   indigo, no purple-blue hero gradient, no emoji icons, no left-border
   cards, no invented metrics, no filler copy, and no hero plus three cards
   on a non-Decide surface. Fix composition first, then
   color and type, then decoration. Check: zero tells remain in the audit
   table.

6. **Verify visually.** Run the app and capture 1440 desktop and 390 mobile,
   light and dark. Read the screenshots as images, compare with the brief,
   fix, and recapture. If the model cannot see images, say so and request a
   screenshot review instead of claiming visual verification. Check: loading,
   empty, error, and happy-path states exist for data surfaces; the final
   pass has no overlap, clipping, or contrast failure.

7. **Close the loop.** Run build, lint, and test. Write `DESIGN.md` with the
   tokens, type, component layer, and rules. Report with `sks-summary`,
   naming the evidence and any unverified item. Check: the build is green,
   `DESIGN.md` exists, and the summary names the screenshots and commands.

## Pitfalls

- **Color before surface.** A palette applied to the wrong composition still
  reads wrong; the archetype decides the layout first.
- **Mood-board references.** "Like Stripe" is not a direction. Extract
  tokens, not adjectives.
- **Parallel CSS systems.** A new `hk-*` class layer next to Astryx doubles
  the maintenance and breaks dark mode; theme the real system.
- **Hero plus three cards everywhere.** That pattern is for Decide/Learn
  surfaces only; Monitor, Operate, and Compare surfaces need density.
- **Blind visual claims.** A DOM diff is not a screenshot; do not say
  "verified" without reading the render.
- **Decoration before composition.** Polishing shadows while the reading path
  is broken wastes the pass.
- **Unnecessary direction questions.** If the user gave a reference, extract
  it; ask only when the direction is genuinely open.

## Verification

```bash
nix develop -c nix fmt
uvx rumdl check skills/authoring/sks-design/
python3 -c "import json; json.load(open('skills.json')); \
json.load(open('package.json')); print('manifests ok')"
grep -c '"sks-design"' skills.json package.json
```

Done when: frontmatter matches the anatomy, evals pass, the skill appears in
README, skills.json, and package.json, and fmt/rumdl are clean.

## See also

- `sks-summary` — the fixed report block for the closing evidence.
- `sks-adversarial` — sandbox for a design comparison or a risky restyle.
- `sks-skill-authoring` — the authoring anatomy this skill follows.
- `sks-curate` — rework pass for an existing skill.
- `sks-dev` — the shipping loop.
