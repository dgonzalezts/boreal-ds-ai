# PR Title

feat(web-components): EOA-15507 add bds-table v3 — dataset mode, column footer, server-side mode, virtualization, guardrail

---

# PR Body

## Description

Closes out the remaining `bds-table` v2 scope that did not land in `EOA-14935` (v2, shipped): full-dataset internal pagination with cross-page selection, a slot-based column footer, server-side mode with an inline skeleton loading visual, opt-in row virtualization, and a large-dataset auto-virtualization guardrail. Continues the `bds-table` roadmap from `ai-work/research/2026-06-16-bds-table-column-api-spike.md`.

---

## Implementation Details

- **`rows` prop + internal pagination + cross-page selection** — full unfragmented dataset owned by the table; wires the slotted `bds-pagination`, slices `visibleRows` internally, and preserves selection across page navigation. Required a `bds-pagination` fix: `itemsPerPage`/`currentPage` changed from `readonly` to `mutable` with write-back, since the props were going stale after internal navigation.
- **Column footer row** — slot-based (`slot="footer"`), not a computed callback, matching the existing `slot="empty-state"`/`slot="row-actions"` pattern. Pinned-column offset tracking extended to footer cells so they stay aligned with header/body cells.
- **Server-side mode + skeleton loading** — `serverSide` prop disables local sort reordering; `loading` prop renders a private, table-scoped skeleton (toolbar, header, checkbox column, body rows, footer, paginator), respecting `prefers-reduced-motion`. Skeleton row count is remainder-aware (a partial last page renders only its actual row count, not a full page's worth).
- **Row virtualization (`virtual` prop)** — `@tanstack/virtual-core` integration, windowed rendering via spacer rows bracketing the visible range. Sticky `<thead>` works normally with `virtual={true}` (validated via two Playwright spikes against this component's actual CSS — an earlier assumption that the combination was broken was reversed before implementation). Variable-height rows supported via `measureElement`. Fixed a critical crash bug found via manual testing: the very first render (before the `Virtualizer` instance exists) previously fell through to rendering the full unbounded dataset; now renders one bounded spacer row instead.
- **Pin-offset throttling during virtualized scroll** — a `ResizeObserver`-driven, two-phase guard (cached expensive read + unconditional cheap write) so pinned-column offsets recompute correctly on both container resize and virtualized scroll's dynamically-swapped row elements, without recomputing on every scroll-driven re-render.
- **`maxClientRows` guardrail** — auto-enables `virtual` internally once the active row count exceeds a threshold (default 1000, module constant), even if the consumer never set `virtual`. Only applies when `serverSide` is `false`; sticky (doesn't turn back off if the dataset shrinks); overrides an explicit `virtual={false}` (deliberate — no escape hatch, since this is a safety guardrail against a real precedent of users adding excessive rows to a table in another internal component library). Non-blocking console warnings cover both the auto-enable event and the remaining sort/selection/memory cost that virtualization alone doesn't address.
- **Component housekeeping** — reordered `bds-table.tsx`'s class members to match the 15-section standard in `ai-docs/guidelines/stencil-best-practices.md` (pure reorder, verified via sorted-line diff with zero content drift), and removed internal (non-public-API) JSDoc per `.claude/CLAUDE.md`'s inline-comment policy — `@Prop()`/`@Event()`/`@Method()`/class-level `@slot` JSDoc is untouched.

---

## Impact Analysis

- No breaking changes to existing `data`/`selectable`/`searchable`/`serverSide` usage.
- `maxClientRows` (default 1000) changes rendering behavior for any existing consumer whose row count already exceeds the threshold — such tables will now auto-virtualize where they previously rendered every row. This is a deliberate, non-optional safety change; two console warnings surface it.
- New direct dependency surface: none — `@tanstack/virtual-core` was already present in the workspace.
- `bds-pagination`'s `itemsPerPage`/`currentPage` props changed from `readonly` to `mutable` — additive, not breaking (external writes still work; the props just also update from internal navigation now).

---

## Testing Conducted

**Automated:**

- [x] Unit tests added per feature area — `bds-table.rows.spec.ts`, `bds-table.footer.spec.ts`, `bds-table.skeleton.spec.ts`, `bds-table.virtual.spec.ts`, `bds-table.pin-offsets.spec.ts`, `bds-table.max-client-rows.spec.ts` (new), plus updates to existing `bds-pagination` specs
- [x] Full `bds-table` suite: 233/233 passing, coverage 98.1% statements / 90.69% branches / 100% functions / 99.47% lines
- [x] `tsc --noEmit` and `eslint` clean on all touched files
- [x] Independently re-verified (not just trusted subagent self-reports) — diffs reviewed, tests re-run, coverage numbers reproduced

**Manual (via Playwright against the real dev server):**

- [x] Sticky-header + virtualized-scroll combination validated with two prototype spikes before implementation
- [x] Crash-bug fix verified against a real 5,000-row dataset (bounded `<tr>` count on first paint, no crash)
- [x] `maxClientRows` auto-enable, override-of-explicit-`false`, and `serverSide` exemption all verified with real DOM node counts and console output
- [x] Pin-offset correctness verified through scroll and through a simulated container resize
- [x] Server-side skeleton loading verified across page navigation, sort-disable behavior, and remainder-aware row counts on partial last pages

---

## Related Changes

- **`bds-pagination`**: `itemsPerPage`/`currentPage` mutability fix (prerequisite for cross-page navigation state to stay in sync)
- **`bds-search-bar`**: minor layout fix for slot placement within `bds-table`'s toolbar-actions integration
- **`boreal-docs`**: `bds-table.mdx` and `bds-table.stories.ts` updated with new sections for dataset mode, column footer, server-side mode, loading state, row virtualization (including a dedicated `WithVirtualization` story), and the `maxClientRows` guardrail; "Current limitations" table cleaned up to remove every row this PR closes, including one stale entry (`rows` prop/cross-page selection) left over from an earlier doc pass
- **`packages/boreal-web-components/src/index.html`**: dev-only playground scenarios for manual verification (per project convention, not intended to be reviewed as production code)

---

## Additional Remarks

- **Deferred to `EOA-16000` (v4)**: column grouping, drag/drop column reorder, column resizing, row expand/collapse, declarative `<template>` cell content, five row-selection refinements (`checkboxSelectionVisibleOnly`, `isRowSelectable`, shift+range selection, `keepNonExistentRowsSelected`, `disableRowSelectionOnClick`), opt-in filter/column-visibility toolbar buttons, and the responsive toolbar (blocked on a UX/UI review with no scheduled owner). See `ai-work/tickets/EOA-16000-bds-table-v4.md`.
- **Mutation testing (Task 12 of the v3 plan) deferred to `EOA-16000`** as well — moved so it runs once against the full combined v2+v3+v4 surface area instead of running now and again after v4 ships.
- `estimateSize` (fixed at 48px, self-correcting via `measureElement`) and `overscan` (fixed at 10) are intentionally not exposed as configurable props — documented as a deliberate scope decision, not an oversight.
- Full task-by-task history and design rationale: `ai-work/plans/EOA-15507-bds-table-v3.md` (status: done) and `ai-work/research/2026-06-16-bds-table-column-api-spike.md`.

---

## References

Closes EOA-15507

---

## Checklist

### General

- [x] Follows conventional commit format: `feat(web-components): EOA-15507 description`
- [x] Ticket reference included (`Closes EOA-15507`)
- [x] Code adheres to TypeScript strict mode — no `any` or implicit types
- [x] Self-reviewed code for quality, readability, and correctness
- [x] All tests pass locally

### Boreal DS — Component Standards

- [x] Design tokens used exclusively — no hard-coded colors, spacing, or radii
- [x] Component tag uses `bds-` prefix
- [x] All props have explicit TypeScript types
- [x] Events use bare `@Event()` (no `bubbles`/`composed` unless required)
- [x] SCSS follows project conventions (no `@use` of the token package in component files)
- [x] Light DOM patterns documented where used (virtualization spacer rows, pin-offset `ResizeObserver`)

### Testing

- [x] Unit test coverage ≥ 90% statements (98.1%)
- [x] Tests cover happy path, error/warning cases, and edge cases (partial-page skeletons, sticky auto-enable, explicit-`false` override)
- [x] Manual testing completed via Playwright against the real running dev server for all rendering/DOM-affecting changes

### Documentation

- [x] JSDoc present on all public APIs (props, events, methods) — internal/private-method JSDoc intentionally removed per `.claude/CLAUDE.md`
- [x] Storybook story added for row virtualization (`WithVirtualization`)
- [x] Storybook MDX documentation updated (dataset mode, column footer, server-side mode, loading state, virtualization, guardrail)
- [x] "Current limitations" table in `bds-table.mdx` updated to remove every closed item

### Performance & Compatibility

- [x] No new console warnings or errors outside the deliberate `maxClientRows`/`virtual` guardrail warnings
- [x] No new dependency added (`@tanstack/virtual-core` already present)
- [x] No regression in existing functionality (verified via full suite + manual Playwright pass)
</content>
