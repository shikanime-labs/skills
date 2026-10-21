# Anti-Slop Audit

Run this before polishing. Fix composition first, then color and type, then
decoration. A tell is a finding; a repaired tell is not.

## The Ten Tells

| Tell | Why it reads cheap | Repair |
| --- | --- | --- |
| Default indigo accent | Looks like an unstyled component library | Pick an accent from the direction |
| Purple-blue hero gradient | The default AI landing-page skin | Flat canvas or one brand gradient |
| Emoji as UI icons | Platform-dependent and visually noisy | Use the icon set or SVG |
| Left-border accent cards | A dashboard cliché that adds no hierarchy | Use spacing and type weight |
| Invented metrics | Destroys trust and means nothing | Use real evidence or omit |
| Filler copy | "Feature one, feature two" signals no product | Write the actual value |
| Cookie-cutter hero plus three cards | Wrong archetype for most surfaces | Change the composition |
| Uniform card soup | Every item has the same weight | Rank, group, or vary density |
| Decorative blobs and glows | Hides weak hierarchy | Remove or make structural |
| Rainbow of semantic colors | No single meaning per color | One accent plus semantic tokens |

## Composition Checks

- The surface archetype is named and the layout matches it.
- One primary action is obvious at first glance.
- The reading path is F-pattern, Z-pattern, or a deliberate scan column.
- The visual anchor is the product, a real artifact, or the primary action.
- Density matches the user's frequency: monitor surfaces are dense, decide
  surfaces are calm.
- The layout reads in grayscale before color is added.

## Color And Type Checks

- One accent color carries the primary action; semantic colors are separate.
- Body text meets WCAG AA contrast; muted text still passes on canvas.
- The type scale has at least three distinct levels; weights do the work.
- Display type is not a default system stack unless the direction says so.
- Radii, borders, and shadows are consistent across controls and cards.
- Dark mode is a token swap, not a second design.

## Content Checks

- Every number is real, sourced, or labeled as a placeholder.
- Every feature names a user outcome, not a capability.
- No "lorem ipsum", no "feature one", no "trusted by thousands" without proof.
- CTA labels are verbs: "Start a commission", not "Submit".
- Empty states explain the next action, not the absence of data.

## Motion And State Checks

- Hover, focus, active, disabled, loading, empty, and error states exist.
- Focus rings are visible and not removed for aesthetics.
- Motion is short, purposeful, and respects `prefers-reduced-motion`.
- No layout shift on load; reserve space for images and data.
- No horizontal scroll at 390px.
