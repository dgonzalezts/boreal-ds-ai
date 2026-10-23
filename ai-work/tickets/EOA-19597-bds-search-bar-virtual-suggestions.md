# EOA-19597 — bds-search-bar-virtual-suggestions

**Ticket:** EOA-19597
**Goal:** Mount only the visible window of `bds-search-bar` suggestions by extracting `bds-table`'s TanStack wiring into a shared `VirtualWindow` utility, so large suggestion lists no longer pay the cost of mounting every item.

## Scope

**In:**
- New `VirtualWindow` utility; `bds-table` moved onto it with no behaviour change
- Data-driven `items` prop on `bds-search-bar` with windowed rendering, data-side filtering, window-aware keyboard navigation, label resolution, and a11y (`aria-setsize`/`aria-posinset`, result-count live region)
- Removal of `VirtualScrollController`
- Story, MDX, bug-report corrections, manual QA, React/Vue parity

**Out:**
- Any change to `bds-select`, `bds-list-menu`, `bds-list-menu-item`, `bds-pagination`, `bds-date-picker`
- Multiselect, group headers, dynamic row heights in `items` mode
- `aria-activedescendant` migration
- Windowing for `bds-select` itself

## Acceptance Criteria

- [ ] With 1,000 `items`, at most ~20 `bds-list-menu-item` elements are mounted at any time
- [ ] Filtering, clearing, empty state, selection, and keyboard navigation (including wrap and window edges) work across the full list
- [ ] `bds-table` virtualization behaves identically; its spec suite passes (virtual spec retargeted only)
- [ ] Slotted `list` mode still works for small lists
- [ ] `VirtualScrollController` is deleted with no remaining references
- [ ] `bds-select`, `bds-list-menu`, `bds-list-menu-item` sources are unmodified; pagination and date-picker selects show no regression
- [ ] Coverage ≥80% and mutation score at the project bar for `VirtualWindow` and `bds-search-bar`
- [ ] React and Vue wrappers match raw component behaviour
- [ ] Bug report corrected and before/after instance count and timing recorded

## Dependencies

- `@tanstack/virtual-core` (already installed)
- Research: `ai-work/research/2026-10-21-virtual-list-approach-*.md`
- Source bug: `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md`

## Open Questions

- Actual Storybook/Chromatic timeout cause (log not yet captured)
- Typical and maximum suggestion list size of real consumers (none today)
- Whether the capture-phase keyboard interception cleanly pre-empts `bds-list-menu`'s navigation (spike at start of T11)
