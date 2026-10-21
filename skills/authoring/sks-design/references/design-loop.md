# Design Loop

Read this when the harness lacks `claude-design`, `popular-web-designs`, or
`design-md`, or when the surface archetype or direction is unclear.

## Surface Archetypes

Name the archetype before any visual token. The job decides the layout.

| Archetype | User job | Composition rule |
| --- | --- | --- |
| Monitor | Watch state change | Dense rows, sparklines, status pills, no hero |
| Operate | Act on a queue | List plus detail, bulk actions, keyboard paths |
| Compare | Choose between options | Matrix, sticky headers, one differentiator per row |
| Configure | Set up a system | Progressive disclosure, one section per step |
| Decide/Learn | Evaluate a claim | Narrative plus proof, hero allowed, one CTA |
| Explore | Browse a space | Search, filters, card grid, generous imagery |
| Command/Inspect | Drive a tool | Monospace, keyboard-first, output density |

If a proposed layout is a hero plus three cards on a Monitor, Operate, or
Compare surface, the archetype is wrong or the layout is.

## Taste Directions

Use one direction. Do not blend three.

| Direction | DNA | Fits |
| --- | --- | --- |
| Build | 70%+ whitespace, 200-600 weight shifts, one accent | Product, developer, premium utility |
| Editorial | Serif display, asymmetric grid, rules | Writing, research, culture |
| Technical | Dense grid, mono labels, visible structure | Dashboards, tooling, infrastructure |
| Friendly | Rounded shapes, candy palette, sticker energy | Community, creators, consumer |
| Luxury | Muted palette, large imagery, wide tracking | Commerce, hospitality, portfolio |
| Brutalist | Raw borders, high contrast, no radius | Culture, events, statement pages |

## Token Extraction

When the user gives a reference, extract these before writing CSS:

- Palette: canvas, surface, ink, muted, accent, success, warning, danger.
- Type: display family, body family, scale ratio, weights, tracking.
- Spacing: base unit, section rhythm, density.
- Radii: control, card, pill.
- Elevation: border, shadow, blur.
- Motion: duration, easing, reduced-motion fallback.
- Density: rows per viewport or cards per row.

Write the tokens as a table in `DESIGN.md`; the implementation imports them.

## Redesign Protocol

1. **Preservation boundary.** Name the identity elements that must survive:
   logo, wordmark, signature color, mascot, copy voice, navigation model.
2. **Transformation mode.** Choose one:
   - `Refinement`: same layout, better tokens and spacing.
   - `Layout Restructure`: new composition, same content and identity.
   - `Full Redesign`: new composition and visual language.
3. **Biggest source of mediocrity.** Name one: weak hierarchy, generic
   palette, card soup, no product evidence, unclear CTA, or noisy density.
4. **Before/after.** Keep one before screenshot and one after screenshot at
   the same viewport; compare them in the final report.

Do not recolor a layout that fails its archetype. Do not rebuild a layout
that only needs token discipline.

## Screenshot Checklist

Capture at least:

- 1440 desktop and 390 mobile.
- Light and dark, or the product's supported themes.
- Loading, empty, error, and happy path for data surfaces.
- The primary interaction after hover, focus, and active.
- The locales the product ships, when copy length can break layout.

Inspect for overlap, clipping, horizontal scroll, contrast, focus rings,
truncation, and inconsistent radii. Read the images; a DOM snapshot is not a
visual check.

## DESIGN.md Template

```markdown
# Design

## Direction

One paragraph: surface archetype, named direction, and the user job.

## Tokens

| Token | Value | Use |
| --- | --- | --- |
| `--canvas` |  | Page background |
| `--surface` |  | Cards and panels |
| `--ink` |  | Primary text |
| `--muted` |  | Secondary text |
| `--accent` |  | Primary action |
| `--radius` |  | Controls and cards |

## Type

Display, body, scale, weights, and tracking.

## Components

The real component layer and the theme entry point.

## Rules

What must not change, and the one distinctive choice this design owns.
```
