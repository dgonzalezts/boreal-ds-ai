# EOA-14935 — bds-table v2 high-priority limitations

**Ticket:** EOA-14935
**Goal:** Close out the six "Priority: High" limitations documented in `bds-table.mdx`, plus two team-requested follow-ups (built-in search bar, skeleton loading) and a large-dataset guardrail raised in a feedback meeting, bringing `bds-table` from its v1 client-side-only scope toward the v2 capabilities scoped in the `EOA-10576` column-API spike.

## Scope

**In:**

- Overflow tooltip on truncated header/cell text — requires a new `manual` mode plus `show()`/`hide()`/`anchorTo()` methods on `bds-tooltip` (not just three methods — the existing auto-discovery-on-mount behavior in `anchoredMixin` must be bypassable, otherwise a singleton tooltip reused across hundreds of cells leaks listeners)
- Full dataset prop + internal pagination + cross-page selection (requires a `bds-pagination` bug fix)
- Externally controlled row selection (`selectedRows` prop) plus a dedicated `selectedRowsChange` event and `v-model:selectedRows` wiring in `vue-output-target.ts` (the existing `bdsSelect` event's richer payload can't drive Vue's `componentModels` directly)
- Server-side sort/pagination/filter mode, including finishing the existing `loading` prop stub using the new `bds-skeleton` primitive
- Row virtualization for large datasets, reusing the already-present `@tanstack/virtual-core` dependency directly (not the existing `VirtualScrollController` utility — see Open Questions)
- Column footer row — **slot-based**, not a computed callback: consumers slot static markup per column (`<span slot="footer">`), `bds-table` projects it into `<tfoot>`, matching the existing `slot="empty-state"`/`slot="row-actions"` pattern
- Built-in `searchable` prop using the now-available `bds-search-bar` component
- New reusable `bds-skeleton` primitive (rect/text/circle variants, shimmer via `var(--boreal-*)` tokens) — justified by the loading mockup showing skeleton needed in at least four places within `bds-table` alone (toolbar, header, cells, pagination row)
- Hover state fix for `pinnable`-only (non-sortable) columns — confirmed missing in current SCSS, sortable columns get a hover-darken treatment on their header icon that pinnable-only columns don't
- `maxClientRows` guardrail — warns (non-blocking) when a client-side dataset exceeds a safe row count without `server-side`/`virtual` enabled

**Out (surfaced during a design playground review, not added to scope):**

- Column grouping, drag/drop reorder ("Button Reorder" in the reviewed playground), column resizing, row expand/collapse (Medium/Low priority items, separate future work)
- Multiple header type variants, per-column skeleton dropdown config, explicit scrollbar visibility toggles, and per-cell state variants (all visible in the reviewed column-config playground but with no equivalent in the current `bds-table-column` implementation) — flagged for a future design pass, not scoped here
- Custom cell content via declarative `<template>` slots for body cells (Medium priority, formatter callback remains the only mechanism — note this is distinct from the footer slot, which is now in scope)
- Responsive toolbar behavior below 744px (blocked on UX/UI sign-off per the original spike)
- Any change to `bds-search-bar`'s own large-list performance behavior (a related but separate concern — its `VirtualScrollController` keeps all DOM nodes mounted rather than reducing DOM count, which is why it isn't reused for `bds-table`)

## Acceptance Criteria

- [ ] `bds-pagination`'s `totalItems` watcher no longer snaps back to a stale `currentPage` prop value
- [ ] `bds-pagination`'s empty state no longer renders a stray literal `"1"`
- [ ] `bds-pagination` exposes a `loading` prop that disables navigation
- [ ] `bds-tooltip` exposes `show()`, `hide()`, `anchorTo(element)` methods usable by a singleton consumer
- [ ] `bds-table` supports `selectedRows` for external/controlled selection
- [ ] `bds-table` supports `searchable` rendering a built-in `bds-search-bar`
- [ ] `bds-table` shows a real overflow tooltip on truncated header/cell text
- [ ] `bds-table` supports a `dataset` prop with internal pagination and cross-page selection, mutually exclusive with `data`
- [ ] `bds-table` supports `serverSide` mode and a working `loading` skeleton-row visual
- [ ] `bds-table` supports a `footer` render path per column, signed off before implementation
- [ ] `bds-table` supports `virtual` opt-in row virtualization backed by the already-present `@tanstack/virtual-core` dependency, with correct row-identity preservation (`key={rowId}`) across sort/filter, and the sticky `<thead>` explicitly disabled while `virtual=true` (documented v1 limitation — see Task 22/22b in the plan for the underlying TanStack Virtual bug this avoids)
- [ ] `bds-table` warns (non-blocking) via `Logger` when a client-side dataset exceeds `maxClientRows` without `serverSide`/`virtual` enabled
- [ ] `bds-table.mdx`'s "Current limitations" table has all shipped rows removed
- [ ] Every new/changed behavior has passing unit tests meeting the two-phase coverage + mutation-score gate

## Dependencies

- `EOA-10576-bds-table-v1.md` (shipped, `status: done`) — this ticket continues its deferred v2 backlog
- `2026-06-16-bds-table-column-api-spike.md` — primary research source for items 1–6
- `bds-search-bar` component (already shipped) — unblocks the `searchable` item
- `@tanstack/virtual-core` (already a direct dependency, `^3.17.1`, used today by `VirtualScrollController`) — unblocks the `virtual` item without adding a new dependency

## Open Questions

- Plan file identity: continue `EOA-10576-bds-table-v1.md` numbering or start fresh under this ticket? → resolved: new file under this ticket.
- `data` vs `dataset` mutual exclusivity enforcement mechanism — resolved: `Logger.warn`, non-blocking.
- Footer design — resolved: slot-based (`slot="footer"`), not a computed callback prop. Sign-off gate remains (Task 17 of the plan) to confirm before implementation.
- `anchorTo()` on `bds-tooltip` — resolved: a new `manual` prop skips `anchoredMixin`'s automatic trigger discovery entirely, so `anchorTo()` can cheaply reassign `triggerSlot` without ever calling the listener-attaching `subscribe()` path.
- `maxClientRows` default value — proposed `1000`, needs team confirmation.
- Whether `VirtualScrollController` should eventually be generalized to support true DOM-count virtualization (not just positional) — **resolved (2026-07-06):** yes, technically possible, via a windowed-creation model, not by generalizing `VirtualScrollController`'s current positional/`MutationObserver` design (no working precedent found anywhere, sits in a real upstream bug class — `TanStack/virtual#1133`, `#1147`, `#823`). **Refined (2026-07-06, follow-up review):** the mechanism doesn't have to be Vaadin's imperative `createElements`/`updateElement` pool — if `bds-search-bar` renders its own `<bds-list-menu-item>` children via its own Stencil JSX (from a data-array prop) instead of relying on consumer-slotted markup, it can use the identical "`.map()` over `getVirtualItems()`" pattern `bds-table` already plans, sharing the same factory rather than needing a separate imperative adapter. Vaadin's `createElements`/`updateElement` is cited only as proof that one shared class *can* serve a list and a grid — not as the recommended mechanism for this codebase. **Decision: deferred to a separate future spike, out of scope for this ticket.** `bds-table` builds its own integration against `@tanstack/virtual-core` directly, fully decoupled from this question. Full research and citations: `/Users/dgonzalez/.claude/plans/let-s-continue-improving-the-calm-balloon.md`; bug tracked at `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md`. Follow-up spike (API design + migration strategy, including the JSX-rendering refinement): `ai-work/research/2026-07-06-shared-virtualization-utility.md` — neither the shared factory nor `bds-search-bar`'s migration is scheduled.
