---
ticket: EOA-12029
component: bds-grid
status: done
created: 2026-04-15
---

## Context

The Boreal DS currently has no layout primitive. Proximus frontend teams rely on ad-hoc CSS Grid/Flex implementations to align UI elements, leading to inconsistency across products. This plan covers the implementation of `bds-grid` and `bds-grid-item` as a standardised, token-driven 12-column layout system.

The Figma node (`7273:43888`) is a **MDS Guidelines / Grid** document — authoritative for breakpoint values, column counts, gutter sizes, and outer margins. The ticket was cross-checked against it and against the Colibri reference implementation; discrepancies and decisions are captured in:

- [ADR-0010](../decisions/0010-grid-dimensional-model.md) — Gutter sizing and container width model
- [ADR-0011](../decisions/0011-grid-navigation-reserve.md) — Navigation reserve as CSS custom property
- [ADR-0012](../decisions/0012-grid-no-flexbox-fallback.md) — Browser support scope (no Flexbox fallback)

### Ticket misalignments resolved in this plan

| #   | Ticket says                               | This plan supersedes with                                                              |
| --- | ----------------------------------------- | -------------------------------------------------------------------------------------- |
| 1   | 3 breakpoints (mobile / tablet / desktop) | 5 breakpoints from Figma, aligned to Colibri naming: `sm/md/lg/xl/2xl`                 |
| 2   | "Fixed gutters"                           | Responsive gutters, 16px at sm–lg, 24px at xl–2xl                                      |
| 3   | max-width: 960px                          | 960px is the column area; container = 992px at `lg` (see ADR-0010)                     |
| 4   | Shadow DOM required                       | Light DOM — all Boreal DS components use light DOM; Shadow DOM AC removed              |
| 5   | `sidebar-reserve` prop                    | `--bds-grid-nav-offset` CSS custom property (see ADR-0011)                             |
| 6   | Flexbox fallback                          | Dropped (see ADR-0012)                                                                 |
| 7   | `cols-sm`, `cols-md`, `cols-lg`           | Prop names use `col-span-sm/md/lg/xl/2xl`, aligned to Colibri and industry conventions |

---

## Breakpoints (source of truth: Figma, aligned to Colibri naming, amended by ADR-0010)

| Token | Min-width | Columns | Relleno (each side) | Outer margin |
| ----- | --------- | ------- | ------------------- | ------------ |
| `sm`  | 320px     | 4       | 16px _(ADR-0010)_   | 0            |
| `md`  | 769px     | 8       | 16px _(ADR-0010)_   | 0            |
| `lg`  | 960px     | 12      | 16px                | 16px         |
| `xl`  | 1152px    | 12      | 24px                | 24px         |
| `2xl` | 1344px    | 12      | 24px                | 32px         |

---

## Component API

### `<bds-grid>`

| Prop      | Type                  | Default   | Description                                                                |
| --------- | --------------------- | --------- | -------------------------------------------------------------------------- |
| `layout`  | `'fixed' \| 'fluid'`  | `'fluid'` | Fixed caps the column area at 960px; fluid fills full width                |
| `row-gap` | token key or px value | —         | Independent row gap override; defaults to the breakpoint gutter when unset |

CSS custom properties exposed on host:

- `--bds-grid-nav-offset: 0px` — horizontal offset for navigation reserve (see ADR-0011)

### `<bds-grid-item>`

> **Naming note**: `col-span` is used (not `cols`) to distinguish item spanning from the container's column count, and to mirror the Colibri reference convention.

| Prop           | Type             | Default | Description                                                                       |
| -------------- | ---------------- | ------- | --------------------------------------------------------------------------------- |
| `col-span`     | `1–12 \| 'full'` | `12`    | Column span at all breakpoints (fallback). `'full'` maps to `grid-column: 1 / -1` |
| `col-span-sm`  | `1–4 \| 'full'`  | —       | Override at `sm` (320px)                                                          |
| `col-span-md`  | `1–8 \| 'full'`  | —       | Override at `md` (769px)                                                          |
| `col-span-lg`  | `1–12 \| 'full'` | —       | Override at `lg` (960px)                                                          |
| `col-span-xl`  | `1–12 \| 'full'` | —       | Override at `xl` (1152px)                                                         |
| `col-span-2xl` | `1–12 \| 'full'` | —       | Override at `2xl` (1344px)                                                        |
| `row-span`     | `1–N \| 'full'`  | —       | Row span (`grid-row: span N`). `'full'` maps to `grid-row: 1 / -1`                |
| `offset`       | `0–11`           | `0`     | Column offset (shifts item right by N columns)                                    |

---

## Architecture notes

- **Light DOM** — consistent with all other Boreal DS components; `shadow: false` (Stencil default). Stencil injects component styles as a plain `<style>` tag into `<head>` — `:host` is a Shadow DOM pseudo-class and is **not** transformed to the tag name in light DOM mode. Component SCSS must use `bds-grid{}` / `bds-grid-item[]` tag-name selectors directly (confirmed by comparing compiled output of `bds-button.entry.js` vs `bds-grid.entry.js`).
- **Host as grid container** — `bds-grid` has `display: grid`. Direct `bds-grid-item` children are natural CSS Grid items; no `display: contents` wrapper needed.
- **CSS custom properties for responsive tokens** — `--bds-grid-columns`, `--bds-grid-gutter`, `--bds-grid-margin` are redefined per breakpoint inside `@media` blocks in the component SCSS. Props on `bds-grid-item` inject a `--_bds-col-span` internal variable used by `grid-column: span var(--_bds-col-span)`.
- **No ARIA grid roles** — `role="grid"` / `role="gridcell"` are ARIA data-grid roles (for spreadsheet-like widgets). A CSS layout grid carries no ARIA role; semantics belong to the content inside the items.

---

## Implementation Progress

| Step                               | Status  | Notes                                                                             |
| ---------------------------------- | ------- | --------------------------------------------------------------------------------- |
| Step 1 — Design tokens             | ✅ Done | `primitives.json` updated; `token-processor.ts` updated; Option C generator added |
| Step 2 — `bds-grid` component      | ✅ Done | Compound sub-folder structure; `$boreal-breakpoint-*` vars from generated file    |
| Step 3 — `bds-grid-item` component | ✅ Done | Component-specific `types/` folders; CSS custom property cascade pattern          |
| Step 4 — Manual testing            | ✅ Done | All 8 cases verified                                                              |
| Step 5 — Unit tests                | ✅ Done | 3 spec files; 100% mutation score (90 mutants killed)                             |
| Step 6 — Storybook                 | ✅ Done | 7 stories + full MDX page; grid overlay; nav-offset slider                        |

### Implementation decisions

- **Compound component structure**: First compound component in the codebase. Each registerable element lives in its own sub-folder (`grid/`, `grid-item/`) inside `bds-grid/`. Types separated into component-specific `types/` folders (no shared types folder).
- **Breakpoint SCSS variables (Option C)**: Instead of a manual `_breakpoints.scss`, a new `generateStencilBreakpoints()` in `scss-generator.ts` generates `dist/stencil/_breakpoints.scss` from `primitives.json`. Variables use `$boreal-breakpoint-*` naming (`$boreal-breakpoint-sm: 320px` etc.). The `_index.scss` forwards this file. The manual `src/styles/_breakpoints.scss` was deleted and the `injectGlobalPaths` entry removed from `stencil.config.ts`.
- **`addUnitIfNeeded()` additions still needed**: These serve the CSS custom property pipeline (`boreal.css`, `_primitives.scss`) independently of the SCSS breakpoints file.

---

## Implementation Steps

### Step 1 — Design tokens ✅

**`packages/boreal-styleguidelines/src/tokens/primitives/primitives.json`** — add a new top-level `"grid"` section after the existing `"layout"` section:

```json
"grid": {
  "breakpoints": {
    "sm":  { "$type": "number", "$value": 320 },
    "md":  { "$type": "number", "$value": 769 },
    "lg":  { "$type": "number", "$value": 960 },
    "xl":  { "$type": "number", "$value": 1152 },
    "2xl": { "$type": "number", "$value": 1344 }
  },
  "columns": {
    "sm":  { "$type": "number", "$value": 4 },
    "md":  { "$type": "number", "$value": 8 },
    "lg":  { "$type": "number", "$value": 12 },
    "xl":  { "$type": "number", "$value": 12 },
    "2xl": { "$type": "number", "$value": 12 }
  },
  "gutter": {
    "sm":  { "$type": "number", "$value": 16 },
    "md":  { "$type": "number", "$value": 16 },
    "lg":  { "$type": "number", "$value": 16 },
    "xl":  { "$type": "number", "$value": 24 },
    "2xl": { "$type": "number", "$value": 24 }
  },
  "margin": {
    "sm":  { "$type": "number", "$value": 0 },
    "md":  { "$type": "number", "$value": 0 },
    "lg":  { "$type": "number", "$value": 16 },
    "xl":  { "$type": "number", "$value": 24 },
    "2xl": { "$type": "number", "$value": 32 }
  },
  "fixed": {
    "max-columns-width": { "$type": "number", "$value": 960 }
  }
}
```

**`packages/boreal-styleguidelines/src/generators/token-processor.ts`** — `addUnitIfNeeded()` (lines 240–246): `generate.ts` and `scss-generator.ts` need no changes (they process all top-level sections generically). Add four sub-path checks so dimensional grid values receive `px` units. `grid-columns` is intentionally excluded — the values 4, 8, 12 must remain unitless for use in `repeat(N, 1fr)`:

```typescript
key.includes("grid-breakpoints") ||
key.includes("grid-gutter") ||
key.includes("grid-margin") ||
key.includes("grid-fixed") ||
```

**Design team notification** (parallel, non-blocking): once the CSS variable names are settled, share them with design so Figma variables can be aligned to match. All token values were sourced directly from the Figma spec — no design input is needed to proceed with implementation.

**`packages/boreal-styleguidelines/src/generators/scss-generator.ts`** — add `generateStencilBreakpoints()` method (implemented) and update `generateStencilIndex()` to `@forward 'breakpoints'`.

**`packages/boreal-styleguidelines/src/generators/generate.ts`** — add `generateStencilBreakpoints(primitives)` call after `generateStencilPrimitives`.

### Step 2 — `bds-grid` component ✅

- **Location**: `packages/boreal-web-components/src/components/layout/bds-grid/grid/`
- Light DOM (no `shadow` key in `@Component`)
- `:host` → `display: grid`, `grid-template-columns: repeat(var(--bds-grid-columns), 1fr)`, `gap: var(--bds-grid-gutter)`, `padding-inline: var(--bds-grid-margin)`, `margin-inline-start: var(--bds-grid-nav-offset, 0px)`
- `@media` blocks use `$boreal-breakpoint-*` SCSS vars from the generated `dist/stencil/_breakpoints.scss` (injected via `_index.scss` forwarding). CSS custom properties `var()` are invalid in `@media` conditions (W3C spec — cascade runs after `@media` evaluation).
- `layout="fixed"` adds `max-width: calc(var(--boreal-grid-fixed-max-columns-width) + 2 * var(--bds-grid-margin))` and `margin-inline: auto`
- `row-gap` prop overrides the row axis via inline style when set
- Types in `grid/types/` (`enum.ts`, `IGrid.ts`, `types.ts`, `index.ts`)

### Step 3 — `bds-grid-item` component ✅

- **Location**: `packages/boreal-web-components/src/components/layout/bds-grid/grid-item/`
- Light DOM; host element is the grid item (no wrapper div needed)
- All `col-span-*` props use `reflect: true`; CSS attribute selectors handle `="full"` cases → `grid-column: 1 / -1`
- Numeric col-span values set `--_col-base`, `--_col-sm` … `--_col-2xl` as inline styles; SCSS `@media` blocks cascade `var()` fallbacks per breakpoint
- `offset > 0` sets `grid-column-start` directly as inline style; `offset=0` leaves auto-placement intact
- `row-span` follows the same attribute-selector + CSS custom property pattern on the row axis
- Zero internal padding — grid manages position only
- Types in `grid-item/types/` (`IGridItem.ts`, `types.ts`, `index.ts`)

### Step 4 — Manual testing ✅

- **File**: `packages/boreal-web-components/src/index.html` — add `<bds-grid>` + `<bds-grid-item>` examples to the `<body>`
- **Command**: `pnpm dev:components` from monorepo root → opens dev server at localhost
- **Checklist**:
  - 12-column fluid grid renders at desktop width
  - Resize through all 5 breakpoints — columns and gutters reflow correctly
  - Responsive col-span overrides (`col-span-sm`, `col-span-md`, `col-span-lg`) switch at the correct widths
  - `col-span="full"` spans all columns at every breakpoint
  - `row-span` stretches item across multiple rows
  - `offset` shifts item right by the correct number of columns
  - `layout="fixed"` caps container at ~992px and centres it
  - `--bds-grid-nav-offset: 64px` shifts the grid right without breaking alignment
  - Invalid prop (e.g. `col-span="15"`) logs a `[BorealDS]` warning in the console
  - No console errors; no style leakage to surrounding page

### Step 5 — Unit tests ✅

- **Location**: `packages/boreal-web-components/src/components/layout/bds-grid/__tests__/bds-grid.spec.tsx`
- Column span math per breakpoint
- `col-span="full"` renders `grid-column: 1 / -1`
- `row-span` renders correctly
- Offset rendering
- Fixed vs fluid container width

### Step 6 — Storybook ✅

- **Location**: `apps/boreal-docs/src/stories/layouts/bds-grid/bds-grid.stories.ts` + `bds-grid.mdx`
- `Default` — fluid grid across three rows; controls for `layout`, `row-gap`, and column overlay toggle
- `FixedLayout` — column area capped at 960 px with a dashed ruler
- `ResponsiveBreakpoints` — items changing col-span at `sm`, `md`, `lg`
- `FullSpan` — `col-span="full"` stretching across all columns
- `RowSpan` — item spanning two rows with column overlay
- `Offset` — three items at offset 0, 4, and 8
- `NavigationReserve` — `--bds-grid-nav-offset` slider (0–294 px) with nav area visualisation
- MDX: How to use, When to use, Accessibility, and per-component ArgTypes tables

---

## Files to create / modify

| File                                                                                                       | Status     | Notes                                                                  |
| ---------------------------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------- |
| `packages/boreal-styleguidelines/src/tokens/primitives/primitives.json`                                    | ✅ Done    | `"grid"` section added                                                 |
| `packages/boreal-styleguidelines/src/generators/token-processor.ts`                                        | ✅ Done    | 4 `grid-*` path checks added to `addUnitIfNeeded()`                    |
| `packages/boreal-styleguidelines/src/generators/scss-generator.ts`                                         | ✅ Done    | `generateStencilBreakpoints()` added; `generateStencilIndex()` updated |
| `packages/boreal-styleguidelines/src/generators/generate.ts`                                               | ✅ Done    | `generateStencilBreakpoints` call added                                |
| `packages/boreal-web-components/stencil.config.ts`                                                          | ✅ Done | Removed manual `_breakpoints.scss` entry from `injectGlobalPaths`      |
| `packages/boreal-web-components/src/components/layouts/bds-grid/grid/bds-grid.tsx`                          | ✅ Done |                                                                        |
| `packages/boreal-web-components/src/components/layouts/bds-grid/grid/bds-grid.scss`                         | ✅ Done | Uses `$boreal-breakpoint-*` vars                                       |
| `packages/boreal-web-components/src/components/layouts/bds-grid/grid/types/IGrid.ts`                        | ✅ Done | Component-specific types folder                                        |
| `packages/boreal-web-components/src/components/layouts/bds-grid/grid/types/enum.ts`                         | ✅ Done |                                                                        |
| `packages/boreal-web-components/src/components/layouts/bds-grid/grid/types/types.ts`                        | ✅ Done |                                                                        |
| `packages/boreal-web-components/src/components/layouts/bds-grid/grid/types/index.ts`                        | ✅ Done |                                                                        |
| `packages/boreal-web-components/src/components/layouts/bds-grid/grid-item/bds-grid-item.tsx`                | ✅ Done |                                                                        |
| `packages/boreal-web-components/src/components/layouts/bds-grid/grid-item/bds-grid-item.scss`               | ✅ Done | Uses `$boreal-breakpoint-*` vars                                       |
| `packages/boreal-web-components/src/components/layouts/bds-grid/grid-item/types/IGridItem.ts`               | ✅ Done | Component-specific types folder                                        |
| `packages/boreal-web-components/src/components/layouts/bds-grid/grid-item/types/types.ts`                   | ✅ Done |                                                                        |
| `packages/boreal-web-components/src/components/layouts/bds-grid/grid-item/types/index.ts`                   | ✅ Done |                                                                        |
| `packages/boreal-web-components/src/index.html`                                                             | ✅ Done | All 8 test cases active                                                |
| `packages/boreal-web-components/src/components/layouts/bds-grid/__test__/bds-grid.basics.spec.tsx`          | ✅ Done | Step 5                                                                 |
| `packages/boreal-web-components/src/components/layouts/bds-grid/__test__/bds-grid-item.basics.spec.tsx`     | ✅ Done | Step 5                                                                 |
| `packages/boreal-web-components/src/components/layouts/bds-grid/__test__/bds-grid-item.validation.spec.tsx` | ✅ Done | Step 5                                                                 |
| `apps/boreal-docs/src/stories/layouts/bds-grid/bds-grid.stories.ts`                                         | ✅ Done | Step 6 — 7 stories                                                     |
| `apps/boreal-docs/src/stories/layouts/bds-grid/bds-grid.mdx`                                                | ✅ Done | Step 6 — full MDX page                                                 |

---

## Out of scope (future follow-up)

- `auto-fit` mode (`grid-template-columns: repeat(auto-fit, minmax(...))`) — useful for card grids, not required by ticket
- Named grid areas (`areas` / `area` props) — complex layout patterns, separate ticket
- **CSS utility classes** — explicitly excluded. A parallel utility class API (`.bds-grid-cols-4`, `.bds-col-span-sm-6`) would create a "two ways to do the same thing" problem that increases decision fatigue for consuming teams. `<bds-grid>` already works in vanilla HTML as a web component. If a concrete team surfaces a use case the component cannot meet, revisit then with evidence. The only reasonable exposure is documenting the three internal CSS custom properties (`--bds-grid-columns`, `--bds-grid-gutter`, `--bds-grid-margin`) for advanced overrides.

---

## Verification

1. ✅ `pnpm --filter boreal-styleguidelines build` — generated `_primitives.scss` contains `--boreal-grid-gutter-sm: 16px` (with px) and `--boreal-grid-columns-sm: 4` (no px)
2. ✅ `pnpm --filter boreal-web-components build` — zero TypeScript errors
3. ✅ `pnpm --filter boreal-web-components test` — 3 spec files; 100% mutation score (90 mutants killed)
4. ✅ Manual test via `src/index.html` — all 8 checklist items verified (Step 4)
5. ✅ Open Storybook → 7 stories render; grid overlay toggles correctly; nav-offset slider works
6. ✅ `layout="fixed"` — container caps at ~992px (960 + 2×16 at `lg`)
7. ✅ `--bds-grid-nav-offset: 64px` — grid shifts right without breaking alignment
8. ✅ `col-span="full"` — item spans all columns regardless of breakpoint
