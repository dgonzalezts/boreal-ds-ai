# PR Title

feat(web-components): EOA-14935 add bds-table controlled selection, built-in search, pinnable hover state, and overflow tooltip

---

# PR Body

## Description

Closes out Tasks 1–15 of the `bds-table` v2 plan (`ai-work/plans/EOA-14935-bds-table-v2.md`): three `bds-pagination` bug fixes, a new `manual` mode + imperative API on `bds-tooltip`, and four `bds-table` capabilities that were previously listed as "Current limitations" in its docs — externally controlled row selection, a built-in search input, a hover state for pinnable-only columns, and an overflow tooltip on truncated header/cell text. Remaining v2 scope (dataset/internal pagination, column footer, server-side/skeleton loading, virtualization, large-dataset guardrail) is tracked separately — see Additional Remarks.

## Implementation Details

**`bds-pagination`**
- Fixed the `totalItems` watcher re-clamping against the stale `currentPage` prop instead of `internalCurrentPage`, which caused a snap-back to page 1 in some sequences.
- Removed a stray literal `"1"` rendered in the empty state.
- Added a `loading` prop that disables all navigation controls and the items-per-page select independent of `totalPages`.

**`bds-tooltip`**
- Added a `manual` prop that skips `anchoredMixin`'s automatic trigger discovery/subscription entirely, plus `show()`/`hide()`/`anchorTo(element)` methods — needed so a single tooltip instance can be reused as a singleton across many trigger elements (see the overflow-tooltip use below) without leaking listeners on every anchor change.
- Fixed an unrelated `arrowX`/listener-cleanup falsy-value bug in `bds-popover` (shares `anchoredMixin`) discovered while working on the tooltip's anchoring path — `arrowData.x ? 20 : undefined` treated a real `0` offset as absent; same fix applied to a listener-removal null-check.

**`bds-table` — controlled selection**
- Added `selectedRows` (external/controlled prop) and `selectedRowsChange` (plain `string[]` event), alongside the existing richer `bdsSelect` event, and wired `v-model:selectedRows` into the Vue output target's `componentModels`.

**`bds-table` — built-in search (`searchable`)**
- `searchable` renders a `<bds-search-bar mode="search" async minimized clearable>` in the toolbar; `bds-table` does not filter internally, consumers listen to `bdsSearch`/`bdsInputDebounced`.
- Per an explicit UX/UI decision, the previous `slot="search-bar"` escape hatch was removed entirely rather than kept alongside — `bds-search-bar` is now the only supported search mechanism.
- `mode="search"` had never actually collapsed visually (the collapse/expand width CSS was scoped only to `mode="list"`'s `<bds-select>` wrapper) and had no clear button (`mode="list"` only had one via `bds-select`'s internal override). Both are now fixed, and in the process:
  - Consolidated the collapse/expand width transition onto the Host element as the single owner, instead of splitting it across the Host and an inner wrapper with mismatched timing (was producing a visible flicker).
  - Fixed a real keyboard-accessibility bug: the trigger's focus listener was bound to `bds-button`'s outer wrapper, which never receives real focus (`bds-button` never forwards `tabIndex` to its inner native `<button>`) — this silently broke `Shift+Tab` navigation out of an open search bar, trapping focus in a loop. Retargeted the listener (and the imperative `tabindex` sync) to the actual inner button.
  - Fixed `handleFieldClear`/`handleBlur` guards that keyed off `this.value === ''`, which is always true in `mode="search"` since that mode never writes typed input back into `value` — this silently broke both the clear button (never actually restored the consumer's data) and the "stay open while a value is typed" blur behavior.
  - `bds-table`'s own toolbar layout needed a small fix too: the search bar's growth was pushing the Filter/Column-visibility buttons sideways since they shared normal document flow; the search bar is now given a fixed-footprint placeholder and absolutely positioned within it so its expansion never affects sibling layout. Its expanded width is exposed via `--bds-table-search-width` (falls back to a `clamp()`-based default) so consumers aren't stuck with one fixed number.

**`bds-table` — pinnable column hover state**
- `renderTh` now stamps `data-pinnable` (parallel to the existing `data-sortable`) so a pinnable-only column's pin icon gets the same hover-darken treatment a sortable column's sort icon already had. Deliberately does **not** add a pointer cursor to the whole header — unlike sortable headers, clicking anywhere in a pinnable-only header doesn't do anything; only the icon itself is interactive.

**`bds-table` — overflow tooltip**
- A single `<bds-tooltip manual>` singleton, delegated `mouseenter`/`mouseleave` (capture phase) on the table wrapper. Anchors tightly to a dedicated inner text-wrapping element (`.bds-table__td-text` for cells, the existing `.bds-table__th-label-text` for headers) rather than the padded cell/header itself, which was initially anchoring to the wrong element and rendering visibly offset from the text. Verified independent of the existing per-column `info` tooltip — both can be present on the same column without either affecting the other.

## Impact Analysis

- All new behavior is opt-in via new props (`selectedRows`, `searchable`, `loading`, `manual`) — no default/v1 behavior changes.
- `slot="search-bar"` is a breaking removal for any consumer that had adopted it ahead of this release — per an explicit UX/UI decision to enforce `bds-search-bar` as the only search mechanism. No known external consumers yet.
- The `bds-search-bar` keyboard-focus and clear-button fixes affect all existing consumers of that component (both `mode="list"` and `mode="search"`), not just the new `bds-table` integration — these were latent bugs, not new API.

## Testing Conducted

**Automated:**
- [x] Unit tests added/updated for every change in this PR (`bds-pagination`, `bds-tooltip`, `bds-search-bar`, `bds-table`) — coverage comfortably clears the ≥90% statement bar per component (e.g. `bds-search-bar.tsx` 98.64%, `bds-table.tsx` 98.33%).
- [ ] Mutation-testing gate (Stryker, per `.agents/memory/mutation-testing-workflow-decisions.md`) — intentionally deferred to a follow-up pass across all touched components at once rather than per-task; not yet run against the final source. See Additional Remarks.

**Manual (via Playwright MCP against `pnpm dev:components`/`pnpm dev:docs`):**
- [x] `bds-pagination`: `totalItems` snap-back, empty-state literal, `loading` disables all controls.
- [x] `bds-tooltip`: `manual` mode with `anchorTo()`/`show()`/`hide()`, no listener leakage across repeated re-anchoring.
- [x] `bds-table` selection: `selectedRows` reflects into checkboxes; every internal change emits both `bdsSelect` and `selectedRowsChange`.
- [x] `bds-table` search: collapsed-by-default, expands without overlapping the Filter/Column-visibility icons (button-group position confirmed unchanged via bounding-box measurement through the full open/type/clear cycle), Enter and debounced-as-you-type filtering both verified, clear restores the full dataset, Shift+Tab now correctly exits the component instead of looping.
- [x] `bds-table` pinnable hover: pin icon darkens to the same color as a sortable column's sort icon; no pointer cursor on pinnable-only headers.
- [x] `bds-table` overflow tooltip: shows full text tightly anchored to the truncated text (not offset from the padded cell); independent of the per-column `info` tooltip in the same header (verified both directions — hovering label vs. hovering the info icon only ever shows one tooltip at a time).

## Related Changes

- **boreal-docs**: `bds-table.mdx`/`bds-table.stories.ts` — removed the four now-shipped limitation rows (renumbered the rest), added `selectedRows`/`selectedRowsChange`/`searchable` to the props table, rewrote the `WithSearch` story (it still referenced the removed `slot="search-bar"` pattern and would not have filtered anything), added `WithControlledSelection`, updated `WithPinnedColumn`/`WithLongHeaderLabel`/`WithLongCellContent` doc comments to describe the now-real hover/tooltip behavior instead of "(To be implemented in v2)". `bds-tooltip.mdx` documents the new manual-mode/programmatic-control API.
- **boreal-vue**: `vue-output-target.ts` gained the `v-model:selectedRows` `componentModels` entry (regenerates the Vue proxy on next build).
- **No changes to**: `boreal-react`, `boreal-styleguidelines`.

## Additional Remarks

- **Mutation testing intentionally not yet run for this PR.** Per plan, it's being run once across all touched components together as a final gate rather than per-task — will follow in a subsequent update to this PR (or a fast-follow commit) before merge.
- **Remaining v2 scope is tracked as a new v3 plan/ticket**, not in this PR: `dataset` prop + internal pagination + cross-page selection, slot-based column footer (pending a design sign-off gate), `serverSide` mode + inline skeleton loading rows, opt-in row virtualization (`@tanstack/virtual-core`), and the `maxClientRows` large-dataset guardrail. See `ai-work/plans/EOA-14935-bds-table-v3.md` and its companion ticket.
- The `--bds-table-search-width` CSS custom property (search bar's expanded width) is intentionally **not** documented in `bds-table.mdx` — that doc doesn't document any CSS custom properties currently (not even the pre-existing `--bds-table-header-height` etc.), so adding one now would be inconsistent with its established scope.
- `packages/boreal-web-components/src/index.html` (the dev playground) is included in this PR with manual-test scenarios for every task in this ticket — flagging in case reviewers prefer playground scratch content stay out of the diff; can be dropped before merge if so.

## References

Refs EOA-14935

## Checklist

### General

- [x] Follows conventional commit format: `feat(scope): TICKET-ID description`
- [x] Ticket reference included (`Refs EOA-14935`)
- [x] Code adheres to TypeScript strict mode — no `any` or implicit types
- [x] Self-reviewed code for quality, readability, and correctness
- [x] All tests pass locally (`.agents/scripts/with-node.sh pnpm test`)

### Boreal DS — Component Standards

- [x] Design tokens used exclusively — no hard-coded colors, spacing, or radii
- [x] Component tag uses `bds-` prefix
- [x] All props have explicit TypeScript types
- [x] Events use bare `@Event()` (no `bubbles`/`composed` unless required)
- [x] SCSS follows `@use` pattern (no `@import`)
- [ ] Light DOM patterns documented if used — N/A, no new light-DOM slot patterns introduced (one was removed: `slot="search-bar"`)

### Testing

- [x] Unit test coverage ≥ 90% statements on every touched component
- [x] Tests cover happy path, error cases, and edge cases (including the info/overflow-tooltip independence and keyboard-trap regression cases)
- [x] Accessibility verified (keyboard navigation fix for the search bar's Shift+Tab trap; existing ARIA behavior unchanged elsewhere)
- [x] Manual testing completed via Playwright MCP against the local dev server
- [ ] Mutation-score gate — deferred, see Additional Remarks

### Documentation

- [x] JSDoc added to all public APIs (props, events, methods)
- [x] Storybook story created/updated with usage examples
- [x] Storybook MDX documentation added/updated (usage, API, examples)
- [ ] README updated if component API changed — N/A, no top-level README changes needed

### Performance & Compatibility

- [x] No new console warnings or errors (also fixed 40 pre-existing `jest.useFakeTimers()` warnings in `bds-search-bar`'s test suite, unrelated to this feature but discovered while testing it)
- [ ] Bundle size impact assessed — not measured this pass
- [ ] Compatible across supported browsers — verified in Chromium via Playwright only; Firefox/Safari not separately checked
- [x] No regression in existing functionality (`mode="list"` search-bar behavior, existing table sort/selection/pin behavior all re-verified)
</content>
