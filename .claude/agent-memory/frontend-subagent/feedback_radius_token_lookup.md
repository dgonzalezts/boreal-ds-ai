---
name: feedback-radius-token-lookup
description: Where to find resolved pixel values for $boreal-radius-* (and other primitive) SCSS tokens when a Figma spec quotes a different-looking radius value
metadata:
  type: project
---

`packages/boreal-styleguidelines/src/tokens/primitives/primitives.json` is the token *source* but its JSON shape isn't a quick grep target. The fast, reliable way to check a primitive token's actual resolved value is the generated
`packages/boreal-styleguidelines/dist/scss/variables/_primitives.scss` (plain `$name: <px-value>;` pairs — trivial to grep). The parallel `dist/stencil/_primitives.scss` instead maps each `$name` to `var(--boreal-name)` (the runtime custom-property form actually consumed by component SCSS via `@use`).

Confirmed values relevant to skeleton/placeholder work: `$boreal-radius-xs2: 2px`, `$boreal-radius-xs: 4px`, `$boreal-radius-m: 12px`.

**Why this matters:** a Figma design-context pull for a node can report a *different* radius than what the codebase's existing shared class actually uses (e.g. `_paginator-skeleton`'s square buttons show `--radius/xs` (4px) in the Figma dev-mode CSS, but this codebase's established `.bds-skeleton--rect` class already uses `$boreal-radius-xs2` (2px) for every square skeleton placeholder site-wide). Precedent (matching the already-shipped [[feedback_skeleton_render_helper]]-style skeleton work in `bds-table`) wins over a literal per-node Figma re-read — don't introduce a second radius for visual "family" consistency across a component's skeleton state.

**How to apply:** when a plan/task references specific Figma radius/color values for a skeleton or placeholder element, check whether the codebase already has an established shared skeleton class first (e.g. `.bds-skeleton`, `.bds-skeleton--rect`, `.bds-skeleton--text`) and reuse it as-is rather than hand-matching the Figma node's own reported token.
