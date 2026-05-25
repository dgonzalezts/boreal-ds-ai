# PR Title

feat(boreal-styleguidelines): EOA-13638 add depth token pipeline with shadow assembler

---

# PR Body

Adds a `depth` group to `primitives.json` and a shadow assembly layer to the token
generator, so composite `box-shadow` CSS shorthands are produced automatically from
Figma-native decomposed sub-tokens rather than being hardcoded in component SCSS.

The design system previously had no token-driven shadow values. Component SCSS files
hardcoded `rgba(19, 19, 22, 0.15)` and passed hex colors as arguments to SCSS functions
in `_interactions.scss`, meaning shadow colors were never theme-aware and could not be
updated centrally. This PR replaces that approach with 14 assembled `depth-box-shadow-*`
tokens emitted per theme, using each theme's `black` value (auto-derived as `black-rgb`)
to drive shadow color, and `white` and `focus` for the focus ring.

A key constraint discovered during implementation: depth composites reference
`--boreal-black-rgb`, `--boreal-white`, and `--boreal-focus`, which are theme-scoped
and only resolve inside `[data-theme]` blocks. Placing composites in `:root` caused
CSS custom property resolution failures in the browser. Composites are therefore emitted
per-theme only, never in the primitives pass. The `assembleShadowTokens` method accepts
a `mode` parameter (`"css"` | `"scss"`) so each output layer uses its own variable
syntax — CSS generators emit `rgba(var(--boreal-black-rgb), 0.15)` while SCSS generators
emit `rgba($boreal-black-rgb, 0.15)` for consistency with the surrounding token files.

The `_interactions.scss` migration also required `@use '@telesign/boreal-style-guidelines/dist/stencil/_index' as *`
at the top of the partial. Stencil's `injectGlobalPaths` compiles each injected file
standalone before prepending it to component SCSS, so `$boreal-*` variables are not in
scope from other injected files unless explicitly imported. This follows the pattern
established by `_selectable-button.scss` on the checkbox-button branch.

Also touches `packages/boreal-web-components` (11 component SCSS files + `_interactions.scss`).

Refs EOA-13638
