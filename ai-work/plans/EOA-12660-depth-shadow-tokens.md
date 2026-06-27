---
ticket: EOA-12660
status: done
created: 2026-05-19
---

# Depth (Box-Shadow) Token Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Add a `depth` group to `primitives.json` with Figma-native decomposed shadow sub-tokens, then extend the token generator to assemble composite `box-shadow` CSS shorthand strings from those primitives — including auto-deriving `black-rgb` from each theme's existing `black` token.

**Architecture:** The Figma-exported decomposed structure (`y`, `blur`, `spread`, `opacity` per size/state) is stored faithfully in `primitives.json`. A new `assembleShadowTokens()` method in `TokenProcessor` reads the already-flattened atomic keys and emits composite `box-shadow` shorthand strings. Composites are emitted inside `[data-theme]` blocks (not `:root`) because they depend on theme-scoped variables (`black-rgb`, `white`, `focus`). `filterDepthAtomics()` suppresses all atomic `depth-*` keys from the primitives pass. The `black-rgb` token is auto-derived from the theme `black` hex value at processing time — no manual entries in theme files.

**Tech Stack:** TypeScript, JSON (W3C Design Tokens format), existing `TokenProcessor` / `CSSGenerator` / `SCSSGenerator` pipeline in `packages/boreal-styleguidelines`.

---

## Files created / modified

| File | Notes |
| ---- | ----- |
| `packages/boreal-styleguidelines/src/tokens/primitives/primitives.json` | Modified — added `depth` group at root level |
| `packages/boreal-styleguidelines/src/generators/token-processor.ts` | Modified — added `assembleShadowTokens(mode)` + `hexToRgbChannels()` + `filterDepthAtomics()` + `black-rgb` auto-derivation |
| `packages/boreal-styleguidelines/src/generators/css-generator.ts` | Modified — depth composites wired into theme pass only (not `:root`) |
| `packages/boreal-styleguidelines/src/generators/scss-generator.ts` | Modified — depth composites wired into theme pass with `"scss"` mode |
| `packages/boreal-styleguidelines/src/__tests__/token-processor.spec.ts` | Created — 33 unit tests across 5 describe blocks |
| `packages/boreal-web-components/src/styles/_interactions.scss` | Modified — replaced all functions with 3 no-argument mixins using `$boreal-*` variables |
| `packages/boreal-web-components/src/components/actions/bds-button/bds-button.scss` | Modified — updated call sites |
| `packages/boreal-web-components/src/components/actions/bds-button-group/bds-button-group.scss` | Modified — updated call sites |
| `packages/boreal-web-components/src/components/actions/bds-toggle/bds-toggle.scss` | Modified — updated call sites |
| `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.scss` | Modified — updated call sites |
| `packages/boreal-web-components/src/components/feedback/bds-tag/bds-tag.scss` | Modified — updated call sites |
| `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.scss` | Modified — updated call sites |
| `packages/boreal-web-components/src/components/forms/bds-checkbox-card/bds-checkbox-card.scss` | Modified — updated call sites |
| `packages/boreal-web-components/src/components/forms/bds-radio-card/bds-radio-card.scss` | Modified — updated call sites |
| `packages/boreal-web-components/src/components/forms/bds-radio-button/bds-radio-button.scss` | Modified — updated call sites |
| `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio.scss` | Modified — updated call sites |
| `packages/boreal-web-components/src/components/overlays/bds-dialog/bds-dialog.scss` | Modified — replaced hardcoded `rgba(...)` with `$boreal-depth-box-shadow-l` |

---

## Task 1: Add `depth` group to `primitives.json` ✅

**Files:**

- `packages/boreal-styleguidelines/src/tokens/primitives/primitives.json` (modified)

**What was built:**

Added a `depth` key at the root of `primitives.json` as a sibling of `spacing`, `radius`, `typography`, etc. Structure:

```
depth
├── y:     xs: 1, s: 2, m: 4, l: 8, xl: 12 | xs-inverse: -1, s-inverse: -2, m-inverse: -4, l-inverse: -8, xl-inverse: -12
├── blur:  xs: 2, s: 4, m: 8, l: 12, xl: 16
├── spread: default: 0
├── opacity: default: 0.15
└── state
    ├── active: y: 0, blur: 0, spread: 2, opacity: 0.15
    ├── focus:  y: 0, blur: 0, inner-spread: 1, outer-spread: 3
    ├── inset:  y: 1, blur: 2, spread: 0, opacity: 0.15
    └── plain:  y: 0, blur: 0, spread: 0, opacity: 0.15
```

No `color` sub-token — shadow color derived from theme `black`. No `$extensions` fields. `state.focus` uses `inner-spread` / `outer-spread` for the double-ring style.

**Commit:** `feat(tokens): add depth primitive tokens to primitives.json`

---

## Task 2: Add `hexToRgbChannels()` and `black-rgb` auto-derivation to `TokenProcessor` ✅

**Files:**

- `packages/boreal-styleguidelines/src/generators/token-processor.ts` (modified)

**What was built:**

- `hexToRgbChannels(hex: string): string` — private method, accepts with or without `#`, returns `"R, G, B"`
- `resolveHexFromReference(rawValue: string): string | undefined` — private method, resolves a `{dot.path}` reference against the `primitiveTokens` map to get the underlying hex
- `flattenThemeTokensForCSS()` and `flattenThemeTokensForSCSS()` — extended: when the key `"black"` with `$type: "color"` is encountered, resolve hex and inject `"black-rgb"` into the result map additively

**Unit tests (33 total):**

- 5 tests in `"TokenProcessor — black-rgb auto-derivation"` covering all 4 themes and the additive contract

**Commit:** `feat(tokens): auto-derive black-rgb from theme black token in TokenProcessor`

---

## Task 3: Add `assembleShadowTokens()` and `filterDepthAtomics()` to `TokenProcessor` ✅

**Files:**

- `packages/boreal-styleguidelines/src/generators/token-processor.ts` (modified)

**What was built:**

`assembleShadowTokens(flattenedPrimitives: FlattenedTokens, mode: "css" | "scss" = "css"): FlattenedTokens`

- Returns a new map with exactly 14 composite `box-shadow` entries
- Does not mutate the input
- `mode` controls variable reference syntax:
  - `"css"` (default): `rgba(var(--boreal-black-rgb), 0.15)` and `var(--boreal-white)`
  - `"scss"`: `rgba($boreal-black-rgb, 0.15)` and `$boreal-white`
- Blur key for inverses: strips `-inverse` suffix (e.g. `depth-y-xs-inverse` → blur uses `depth-blur-xs`)
- `active` = concatenation of assembled `focus` + `inset` strings
- `depth-box-shadow-focus` uses `ref("white")` and `ref("focus")` — no `rgba`, pure ring via `var()`/`$`

`filterDepthAtomics(flattened: FlattenedTokens): FlattenedTokens`

- Returns a new map excluding any key that starts with `depth-` AND is not `depth-box-shadow-*`
- Used on the primitives path to suppress atomic sub-tokens from the consumer-facing output
- Does not mutate the input

**Unit tests (33 total):**

- 10 tests in `"TokenProcessor — assembleShadowTokens"` (CSS mode, default)
- 6 tests in `"TokenProcessor — assembleShadowTokens mode parameter"` (CSS vs SCSS mode)
- 6 tests in `"TokenProcessor — filterDepthAtomics"`

**Commit:** `feat(tokens): add shadow assembler and filterDepthAtomics to TokenProcessor`

---

## Task 4: Wire assembler into `CSSGenerator` and `SCSSGenerator` ✅

**Files:**

- `packages/boreal-styleguidelines/src/generators/css-generator.ts` (modified)
- `packages/boreal-styleguidelines/src/generators/scss-generator.ts` (modified)

**Key architectural decision made during implementation:**

Depth composites reference `--boreal-black-rgb`, `--boreal-white`, and `--boreal-focus` — variables that only exist inside `[data-theme]` blocks, not in `:root`. Placing composites in `:root` caused CSS custom property resolution failures (values shown as `initial` in DevTools). The fix is to emit depth composites **inside the per-theme pass only**, never in the primitives pass.

**What was built:**

`CSSGenerator`:
- `generateGlobalCSS()` / `generateCSSBundle()` `:root` block: `filterDepthAtomics(flattenedPrimitives)` — no shadows assembled here
- `generateThemeCSS()` / `generateCSSBundle()` per-theme block: shadows assembled (`"css"` mode) and merged alongside `flattenedTheme` and `flattenedUsage`

`SCSSGenerator`:
- Primitive path (non-theme): `filterDepthAtomics(flattenPrimitiveTokens(...))` — no shadows assembled
- Theme path (variables, maps, stencil): `assembleShadowTokens(..., "scss")` — composites merged with `$boreal-*` variable references for SCSS consistency

**Output verification (after `pnpm generate`):**

- `dist/css/theme-proximus.css`: `--boreal-depth-box-shadow-xs: 0 1px 2px 0px rgba(var(--boreal-black-rgb), 0.15)` inside `[data-theme="proximus"]` ✓
- `dist/scss/variables/_theme-proximus.scss`: `$boreal-depth-box-shadow-xs: 0 1px 2px 0px rgba($boreal-black-rgb, 0.15)` ✓
- `dist/scss/variables/_theme-proximus.scss`: `$boreal-depth-box-shadow-focus: 0 0 0 1px $boreal-white, 0 0 0 3px $boreal-focus` ✓
- `dist/stencil/_theme.scss`: `$boreal-depth-box-shadow-xs: var(--boreal-depth-box-shadow-xs)` ✓ (bridge pattern)
- `:root` block: no `depth-box-shadow-*` keys ✓

**Unit tests (33 total):**

- 4 tests in `"Generator wiring contract — primitives path vs theme path"` encoding the architectural constraint

**Commit:** `feat(tokens): wire shadow assembler into CSS and SCSS generators`

---

## Task 5: Migrate `_interactions.scss` and all call sites to depth token variables ✅

**Files:**

- `packages/boreal-web-components/src/styles/_interactions.scss` (modified)
- 11 component SCSS files (modified — see file table above)

**Context:** `_interactions.scss` is in Stencil's `injectGlobalPaths` — it is processed standalone by Sass before being prepended to every component SCSS file. The `@use '@telesign/boreal-style-guidelines/dist/stencil/_index' as *` declaration at the top of the partial makes it self-contained so `$boreal-*` variables are in scope during standalone compilation. This follows the pattern established by `_selectable-button.scss` on `feature/EOA-12342_checkbox_button_DG`.

**What was built:**

`_interactions.scss`:
- Added `@use '@telesign/boreal-style-guidelines/dist/stencil/_index' as *` at top
- Removed all 9 old functions/mixins: `bds-focus-ring-value`, `bds-hover-shadow($color)`, `bds-active-shadow-inset`, `bds-shadow-inset`, and duplicates
- Defined 3 no-argument mixins:
  - `bds-focus-ring` → `box-shadow: $boreal-depth-box-shadow-focus`
  - `bds-focus-ring-active` → `box-shadow: $boreal-depth-box-shadow-active`
  - `bds-hover-shadow` → `box-shadow: $boreal-depth-box-shadow-xs`
- Kept unchanged: `bds-transition-visibility`, `bds-transition-surface`, `bds-transition-action`, `bds-icon`

All call sites:
- `@include bds-hover-shadow(...)` → `@include bds-hover-shadow`
- `@include bds-focus-ring(...)` / `box-shadow: bds-focus-ring-value(...)` → `@include bds-focus-ring`
- Active states (focus + inset combined) → `@include bds-focus-ring-active`
- `bds-dialog.scss` hardcoded `box-shadow: 0 8px 12px 0 rgba(19, 19, 22, 0.15)` → `box-shadow: $boreal-depth-box-shadow-l`

**Manual test:**

Run: `pnpm dev:components` and open in browser

- [ ] Hover state on `bds-button` shows `xs` shadow (subtle elevation)
- [ ] Focus state on `bds-button` shows double-ring: 1px white inner + 3px focus-color outer
- [ ] Active state on `bds-button` (variant with inset) shows focus ring + inset shadow combined
- [ ] Hover and focus on `bds-tag`, `bds-radio`, `bds-checkbox-card`, `bds-radio-card`, `bds-radio-button` all show consistent shadow
- [ ] Shadow colors adapt per theme (switch `data-theme` on `<body>`)
- [ ] No Sass compilation errors in build output

**Commit:**

```bash
git commit -m "refactor(styles): replace hardcoded shadow values with depth token variables"
```
