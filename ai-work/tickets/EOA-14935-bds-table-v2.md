# EOA-14935 — bds-table v2 high-priority limitations

**Ticket:** EOA-14935
**Status:** Done (2026-07-09)
**Goal:** Close four of the six "Priority: High" limitations documented in `bds-table.mdx` that were tractable without deeper architectural prerequisites, plus a `bds-pagination` bug-fix pass and a new `bds-tooltip` manual/imperative-control API, moving `bds-table` a step toward the v2 capabilities scoped in the `EOA-10576` column-API spike.

**Remaining scope:** the rest of the originally-scoped v2 work (full `dataset` prop + internal pagination + cross-page selection, column footer, server-side mode + skeleton loading, row virtualization, `maxClientRows` guardrail) did not land in this pass — see [`ai-work/tickets/EOA-15507-bds-table-v3.md`](./EOA-15507-bds-table-v3.md), which carries it forward as its own ticket.

## Scope

**In (shipped):**

- Three `bds-pagination` bug fixes: `totalItems` watcher snap-back, a stray literal `"1"` in the empty state, and a new `loading` prop that disables navigation.
- `bds-tooltip` gains a `manual` mode plus `show()`/`hide()`/`anchorTo()` methods — not just three methods bolted on, but a way to bypass `anchoredMixin`'s automatic trigger-discovery-on-mount entirely, since a singleton tooltip reused across hundreds of table cells cannot go through that path repeatedly without leaking listeners.
- Externally controlled row selection on `bds-table`: `selectedRows` prop plus a dedicated `selectedRowsChange` event and `v-model:selectedRows` wiring in `vue-output-target.ts` (the existing `bdsSelect` event's richer payload can't drive Vue's `componentModels` directly).
- Built-in `searchable` prop on `bds-table` using `bds-search-bar`. This surfaced two real gaps in `bds-search-bar` itself (not originally scoped, discovered during manual testing and fixed as part of this same ticket): `mode="search"` never actually collapsed visually, and had no clear button. Also surfaced and fixed a keyboard-accessibility bug (`Shift+Tab` trapped focus in a loop when exiting an open search bar) and a bug where the clear button/blur-while-typing behavior silently never worked in `mode="search"`.
- Hover state fix for `pinnable`-only (non-sortable) columns — sortable columns already got a hover-darken treatment on their header icon that pinnable-only columns didn't.
- Overflow tooltip on truncated header/cell text, via the new `bds-tooltip` manual-mode singleton.

**Deferred to v3 (not shipped in this ticket):**

- Full dataset prop + internal pagination + cross-page selection.
- Column footer row (slot-based).
- Server-side sort/pagination/filter mode + skeleton loading visual.
- Row virtualization for large datasets (`@tanstack/virtual-core`).
- `maxClientRows` guardrail.
- The standalone reusable `bds-skeleton` primitive — deferred further still, pending a second real consumer (see the v3 ticket/plan for the trigger condition).

**Out (surfaced during a design playground review, not added to scope in this ticket):**

- Column grouping, drag/drop reorder ("Button Reorder" in the reviewed playground), column resizing, row expand/collapse (Medium/Low priority items, previously "separate future work" — **update (2026-07-09): promoted into v3's scope**, see the v3 ticket)
- Multiple header type variants, per-column skeleton dropdown config, explicit scrollbar visibility toggles, and per-cell state variants (all visible in the reviewed column-config playground but with no equivalent in the current `bds-table-column` implementation) — previously "flagged for a future design pass, not scoped here" — **update (2026-07-09): promoted into v3's scope**, see the v3 ticket
- Custom cell content via declarative `<template>` slots for body cells (formatter callback remains available as an alternative mechanism, distinct from the footer slot) — **update (2026-07-09): promoted into v3's scope**, see the v3 ticket
- Responsive toolbar behavior below 744px (blocked on UX/UI sign-off per the original spike) — **update (2026-07-09): promoted into v3's scope** (sign-off gate still required), see the v3 ticket
- Any change to `bds-search-bar`'s own large-list performance behavior (a related but separate concern — its `VirtualScrollController` keeps all DOM nodes mounted rather than reducing DOM count, which is why it isn't reused for `bds-table`'s virtualization) — still out of scope, not carried into v3 either

## Acceptance Criteria

- [x] `bds-pagination`'s `totalItems` watcher no longer snaps back to a stale `currentPage` prop value
- [x] `bds-pagination`'s empty state no longer renders a stray literal `"1"`
- [x] `bds-pagination` exposes a `loading` prop that disables navigation
- [x] `bds-tooltip` exposes `show()`, `hide()`, `anchorTo(element)` methods usable by a singleton consumer
- [x] `bds-table` supports `selectedRows` for external/controlled selection
- [x] `bds-table` supports `searchable` rendering a built-in `bds-search-bar`
- [x] `bds-table` shows a real overflow tooltip on truncated header/cell text, independent of the existing per-column `info` tooltip
- [x] `bds-table` supports a hover-darken state for `pinnable`-only (non-sortable) columns
- [x] `bds-table.mdx`'s "Current limitations" table has all four shipped-in-this-ticket rows removed (renumbered)
- [x] Unit tests added for every change in this ticket, coverage ≥90% statements per component
- [ ] Mutation-score gate (Stryker) — intentionally deferred to a single batched pass across all touched components rather than per-feature; not yet run against final source at ticket close. Tracked as the first task of follow-on work (see the v3 plan's Task 12, which also covers this ticket's own touched files).

Moved to the v3 ticket (not acceptance criteria here anymore):

- `dataset` prop with internal pagination and cross-page selection
- `serverSide` mode and `loading` skeleton-row visual
- `footer` render path per column
- `virtual` opt-in row virtualization
- `maxClientRows` guardrail

## Dependencies

- `EOA-10576-bds-table-v1.md` (shipped, `status: done`) — this ticket continues its deferred v2 backlog
- `2026-06-16-bds-table-column-api-spike.md` — primary research source
- `bds-search-bar` component (already shipped) — unblocked the `searchable` item; several latent bugs in it were fixed as part of this ticket (see Scope above)

## Open Questions (resolved during this ticket)

- `anchorTo()` on `bds-tooltip` — resolved: a new `manual` prop skips `anchoredMixin`'s automatic trigger discovery entirely, so `anchorTo()` can cheaply reassign `triggerSlot` without ever calling the listener-attaching `subscribe()` path.
- Whether to keep `slot="search-bar"` as a fallback alongside `searchable` — resolved: no. Per an explicit UX/UI decision, `slot="search-bar"` was removed entirely rather than kept as an escape hatch, enforcing `bds-search-bar` as the only supported search mechanism.
- Mutation-testing cadence — resolved (2026-07-09): run once, batched across all touched components, rather than after every individual task/feature. Carried forward as the stated testing policy for the v3 plan too.

Remaining open questions (dataset mutual exclusivity, footer sign-off gate, `maxClientRows` default, `VirtualScrollController` generalization) moved to [`ai-work/tickets/EOA-15507-bds-table-v3.md`](./EOA-15507-bds-table-v3.md) along with their scope.
