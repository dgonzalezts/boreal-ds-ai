---
title: "Grid System — bds-grid & bds-grid-item"
ticket: ".ai/tickets/grid-system-&-component.md"
figma: "https://www.figma.com/design/htCJc5chrgNRK337cyc14K/-BOR--DSG-COMPONENTS-%E2%86%92-GUIDELINES?node-id=7273-43888"
status: pending
date: 2026-04-15
---

## Context

The Boreal DS currently has no layout primitive. Proximus frontend teams rely on ad-hoc CSS Grid/Flex implementations to align UI elements, leading to inconsistency across products. This plan covers the implementation of `bds-grid` and `bds-grid-item` as a standardised, token-driven 12-column layout system.

The Figma node (`7273:43888`) is a **MDS Guidelines / Grid** document — authoritative for breakpoint values, column counts, gutter sizes, and outer margins. The ticket was cross-checked against it and against the Colibri reference implementation; discrepancies and decisions are captured in:

- [ADR-0010](../decisions/0010-grid-dimensional-model.md) — Gutter sizing and container width model
- [ADR-0011](../decisions/0011-grid-navigation-reserve.md) — Navigation reserve as CSS custom property
- [ADR-0012](../decisions/0012-grid-no-flexbox-fallback.md) — Browser support scope (no Flexbox fallback)

### Ticket misalignments resolved in this plan

| # | Ticket says | This plan supersedes with |
|---|---|---|
| 1 | 3 breakpoints (mobile / tablet / desktop) | 5 breakpoints from Figma, aligned to Colibri naming: `sm/md/lg/xl/2xl` |
| 2 | "Fixed gutters" | Responsive gutters, 16px at sm–lg, 24px at xl–2xl |
| 3 | max-width: 960px | 960px is the column area; container = 992px at `lg` (see ADR-0010) |
| 4 | Shadow DOM required | Light DOM — all Boreal DS components use light DOM; Shadow DOM AC removed |
| 5 | `sidebar-reserve` prop | `--bds-grid-nav-offset` CSS custom property (see ADR-0011) |
| 6 | Flexbox fallback | Dropped (see ADR-0012) |
| 7 | `cols-sm`, `cols-md`, `cols-lg` | Prop names use `col-span-sm/md/lg/xl/2xl`, aligned to Colibri and industry conventions |

---

## Breakpoints (source of truth: Figma, aligned to Colibri naming, amended by ADR-0010)

| Token | Min-width | Columns | Relleno (each side) | Outer margin |
|---|---|---|---|---|
| `sm` | 320px | 4 | 16px *(ADR-0010)* | 0 |
| `md` | 769px | 8 | 16px *(ADR-0010)* | 0 |
| `lg` | 960px | 12 | 16px | 16px |
| `xl` | 1152px | 12 | 24px | 24px |
| `2xl` | 1344px | 12 | 24px | 32px |

---

## Component API

### `<bds-grid>`

| Prop | Type | Default | Description |
|---|---|---|---|
| `layout` | `'fixed' \| 'fluid'` | `'fluid'` | Fixed caps the column area at 960px; fluid fills full width |
| `row-gap` | token key or px value | — | Independent row gap override; defaults to the breakpoint gutter when unset |

CSS custom properties exposed on host:
- `--bds-grid-nav-offset: 0px` — horizontal offset for navigation reserve (see ADR-0011)

### `<bds-grid-item>`

> **Naming note**: `col-span` is used (not `cols`) to distinguish item spanning from the container's column count, and to mirror the Colibri reference convention.

| Prop | Type | Default | Description |
|---|---|---|---|
| `col-span` | `1–12 \| 'full'` | `12` | Column span at all breakpoints (fallback). `'full'` maps to `grid-column: 1 / -1` |
| `col-span-sm` | `1–4 \| 'full'` | — | Override at `sm` (320px) |
| `col-span-md` | `1–8 \| 'full'` | — | Override at `md` (769px) |
| `col-span-lg` | `1–12 \| 'full'` | — | Override at `lg` (960px) |
| `col-span-xl` | `1–12 \| 'full'` | — | Override at `xl` (1152px) |
| `col-span-2xl` | `1–12 \| 'full'` | — | Override at `2xl` (1344px) |
| `row-span` | `1–N \| 'full'` | — | Row span (`grid-row: span N`). `'full'` maps to `grid-row: 1 / -1` |
| `offset` | `0–11` | `0` | Column offset (shifts item right by N columns) |

---

## Architecture notes

- **Light DOM** — consistent with all other Boreal DS components; `shadow: false` (Stencil default). `:host` compiles to the tag-name selector and is injected into `<head>`. No shadow boundary, no `::part()`.
- **Host as grid container** — `bds-grid`'s `:host` has `display: grid`. Direct `bds-grid-item` children are natural CSS Grid items; no `display: contents` wrapper needed.
- **CSS custom properties for responsive tokens** — `--bds-grid-columns`, `--bds-grid-gutter`, `--bds-grid-margin` are redefined per breakpoint inside `@media` blocks in the component SCSS. Props on `bds-grid-item` inject a `--_bds-col-span` internal variable used by `grid-column: span var(--_bds-col-span)`.
- **No ARIA grid roles** — `role="grid"` / `role="gridcell"` are ARIA data-grid roles (for spreadsheet-like widgets). A CSS layout grid carries no ARIA role; semantics belong to the content inside the items.

---

## Implementation Steps

### Step 1 — Design tokens

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

### Step 2 — `bds-grid` component
- **Location**: `packages/boreal-web-components/src/components/layout/bds-grid/`
- Light DOM (no `shadow` key in `@Component`)
- `display: grid` and `grid-template-columns: repeat(var(--bds-grid-columns), 1fr)` on `:host`
- `gap: var(--bds-grid-gutter)` on `:host`; `row-gap` prop overrides the row axis when set
- `padding-inline: var(--bds-grid-margin)` on `:host` for outer margins
- `@media` blocks redefine the three CSS tokens at each breakpoint
- `layout="fixed"` adds `max-width: calc(960px + 2 * var(--bds-grid-margin))` and `margin-inline: auto`

### Step 3 — `bds-grid-item` component
- **Location**: `packages/boreal-web-components/src/components/layout/bds-grid/`
- Light DOM; host element is the grid item (no wrapper div needed)
- `col-span` prop (and per-breakpoint overrides) writes `--_bds-col-span` via `@Watch`; `grid-column` reads it
- `col-span="full"` maps to `grid-column: 1 / -1` (bypasses the variable)
- `row-span` follows the same pattern on the row axis
- Zero internal padding — grid manages position only

### Step 4 — Unit tests
- **Location**: `packages/boreal-web-components/src/components/layout/bds-grid/__tests__/bds-grid.spec.tsx`
- Column span math per breakpoint
- `col-span="full"` renders `grid-column: 1 / -1`
- `row-span` renders correctly
- Offset rendering
- Fixed vs fluid container width

### Step 5 — Manual testing
- **File**: `packages/boreal-web-components/src/index.html` — add `<bds-grid>` + `<bds-grid-item>` examples to the `<body>`
- **Command**: `pnpm dev:components` from monorepo root → opens dev server at localhost
- **Checklist**:
  - 12-column layout renders at desktop width
  - Resize through all 5 breakpoints — columns and gutters reflow
  - `layout="fixed"` caps container at ~992px and centres it
  - `--bds-grid-nav-offset: 64px` shifts grid right without breaking alignment
  - `col-span="full"` spans all columns at all breakpoints
  - No console errors; no style leakage to surrounding page

### Step 6 — Storybook
- **Location**: `apps/boreal-docs/src/stories/layout/bds-grid.stories.ts` + `.mdx`
- Default story: 12-column desktop layout
- Responsive story: items spanning all 5 breakpoints
- Grid overlay toggle (CSS `background-image` column visualiser, toggled via story arg)
- Navigation reserve story: `--bds-grid-nav-offset` at 64px and 294px
- MDX: document `col-span="full"`, minimum browser requirements (Chrome/Firefox/Safari last 2 major)

---

## Files to create / modify

| File | Action |
|---|---|
| `packages/boreal-styleguidelines/src/tokens/primitives/primitives.json` | Add grid tokens |
| `packages/boreal-styleguidelines/src/generators/token-processor.ts` | Add 4 `grid-*` path checks to `addUnitIfNeeded()` |
| `packages/boreal-web-components/src/index.html` | Add manual test markup (Step 5) |
| `packages/boreal-web-components/src/components/layout/bds-grid/bds-grid.tsx` | New |
| `packages/boreal-web-components/src/components/layout/bds-grid/bds-grid.scss` | New |
| `packages/boreal-web-components/src/components/layout/bds-grid/types/IGrid.ts` | New |
| `packages/boreal-web-components/src/components/layout/bds-grid/bds-grid-item.tsx` | New |
| `packages/boreal-web-components/src/components/layout/bds-grid/bds-grid-item.scss` | New |
| `packages/boreal-web-components/src/components/layout/bds-grid/types/IGridItem.ts` | New |
| `packages/boreal-web-components/src/components/layout/bds-grid/__tests__/bds-grid.spec.tsx` | New |
| `apps/boreal-docs/src/stories/layout/bds-grid.stories.ts` | New |
| `apps/boreal-docs/src/stories/layout/bds-grid.mdx` | New |

---

## Out of scope (future follow-up)

- `auto-fit` mode (`grid-template-columns: repeat(auto-fit, minmax(...))`) — useful for card grids, not required by ticket
- Named grid areas (`areas` / `area` props) — complex layout patterns, separate ticket
- **CSS utility class approach** — class-based alternative à la Colibri (`bds-grid-cols-4`, `bds-col-span-6`, responsive variants). Implemented in `boreal-styleguidelines` as a generated SCSS utility file, separate from the Stencil components. To be planned and implemented after Steps 1–6 are complete and verified.

---

## Verification

1. `pnpm --filter boreal-styleguidelines build` — generated `_primitives.scss` contains `--boreal-grid-gutter-sm: 16px` (with px) and `--boreal-grid-columns-sm: 4` (no px)
2. `pnpm --filter boreal-web-components build` — zero TypeScript errors
3. `pnpm --filter boreal-web-components test` — all column math and span tests pass
4. Manual test via `src/index.html` passes all checklist items (Step 5)
5. Open Storybook → grid overlay visible and correct at all 5 breakpoints
6. Set `layout="fixed"` — container caps at ~992px (960 + 2×16 at `lg`)
7. Set `--bds-grid-nav-offset: 64px` — grid shifts right without breaking alignment
8. `col-span="full"` — item spans all columns regardless of breakpoint
