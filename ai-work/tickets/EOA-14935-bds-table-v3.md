# EOA-14935 — bds-table v3 dataset mode, footer, server-side/loading, virtualization, guardrail

**Ticket:** EOA-14935
**Status:** Pending
**Goal:** Carry forward the `bds-table` v2 scope that did not land in [`ai-work/tickets/EOA-14935-bds-table-v2.md`](./EOA-14935-bds-table-v2.md) (status: `done`) — full-dataset internal pagination with cross-page selection, a slot-based column footer, server-side mode with an inline skeleton loading visual, opt-in row virtualization, and a large-dataset guardrail warning.

**Plan:** [`ai-work/plans/EOA-14935-bds-table-v3.md`](../plans/EOA-14935-bds-table-v3.md)

## Scope

**In:**

- Full dataset prop (`dataset`) + internal pagination + cross-page selection (requires the `bds-pagination` `totalItems` watcher fix, already shipped in v2)
- Column footer row — **slot-based**, not a computed callback: consumers slot static markup per column (`<span slot="footer">`), `bds-table` projects it into `<tfoot>`, matching the existing `slot="empty-state"`/`slot="row-actions"` pattern. Requires a design sign-off gate before implementation (already resolved in principle during v2 planning — slot-based, not a prop — but the sign-off itself is still a gate in the v3 plan's task sequence).
- Server-side sort/pagination/filter mode, including finishing the existing `loading` prop stub with an inline skeleton-row visual (implemented as a private, table-scoped render helper — see "Deferred: `bds-skeleton` primitive" below, not a new component)
- Row virtualization for large datasets, reusing the already-present `@tanstack/virtual-core` dependency directly (not the existing `VirtualScrollController` utility — see Open Questions)
- `maxClientRows` guardrail — warns (non-blocking) when a client-side dataset exceeds a safe row count without `serverSide`/`virtual` enabled
- A single consolidated mutation-testing pass (Stryker) across every component touched by this ticket's tasks, run once at the end rather than per-task — this also covers any remaining mutation-testing debt from the v2 ticket's own touched files, which was deferred there for the same reason

**Also newly in scope (2026-07-09 — promoted from the v2 ticket's "Out" list; these had no plan-file tasks yet as of this writing and need their own design/planning pass before execution):**

- Column grouping, drag/drop reorder ("Button Reorder"), column resizing, row expand/collapse (previously Medium/Low priority items deferred as "separate future work")
- Multiple header type variants, per-column skeleton dropdown config, explicit scrollbar visibility toggles, and per-cell state variants (previously flagged for "a future design pass, not scoped")
- Custom cell content via declarative `<template>` slots for body cells (formatter callback remains available as an alternative mechanism; this adds a second, declarative option — distinct from, and additive to, the footer slot already in scope above)
- Responsive toolbar behavior below 744px (previously blocked on UX/UI sign-off per the original spike — sign-off still required before implementation, same as the footer's own gate)

**Deferred further still (not in this ticket either):**

- New reusable `bds-skeleton` primitive (rect/text/circle variants, shimmer via `var(--boreal-*)` tokens) — the loading visual needed here is implemented as a private, table-scoped render helper inside `bds-table` itself, built to the future primitive's exact shape (class names, custom-property names, helper signature) so extraction later is close to mechanical. Actually extracting it into a standalone component is gated on a second real consumer appearing (e.g. `bds-list`, `bds-card`), not scheduled here.
- A shared virtualization utility between `bds-table` and `bds-search-bar` — researched and found technically possible only via a larger rearchitecture of `bds-search-bar`'s own list rendering, gated on an accessibility redesign with no scheduled owner. See `ai-work/research/2026-07-06-shared-virtualization-utility.md`.

**Out (still not in scope):**

- Any change to `bds-search-bar`'s own large-list performance behavior beyond the deferred shared-utility research above (a related but separate concern — its `VirtualScrollController` keeps all DOM nodes mounted rather than reducing DOM count, which is why it isn't reused for `bds-table`'s virtualization)

## Acceptance Criteria

- [ ] `bds-table` supports a `dataset` prop with internal pagination and cross-page selection, mutually exclusive with `data` (warns via `Logger` if both are set)
- [ ] `bds-table` supports a `footer` render path per column, signed off before implementation
- [ ] `bds-table` supports `serverSide` mode and a working `loading` skeleton-row visual (respecting `prefers-reduced-motion`)
- [ ] `bds-table` supports `virtual` opt-in row virtualization backed by `@tanstack/virtual-core`, with correct row-identity preservation (`key={rowId}`) across sort/filter, and the sticky `<thead>` explicitly disabled while `virtual=true` (documented limitation — see the plan's Task 7 for the underlying TanStack Virtual bug this avoids)
- [ ] Pin-offset recomputation is throttled during virtualized scroll (does not re-run on every scroll-driven re-render)
- [ ] `bds-table` warns (non-blocking) via `Logger` when a client-side dataset exceeds `maxClientRows` without `serverSide`/`virtual` enabled
- [ ] `bds-table.mdx`'s "Current limitations" table has all five shipped-in-this-ticket rows removed
- [ ] `bds-table-column` supports column grouping and drag/drop reorder ("Button Reorder"), and `bds-table` supports column resizing and row expand/collapse — each needs its own design/planning pass before implementation (no plan-file tasks exist yet for these; see Open Questions)
- [ ] `bds-table-column` design gap closed for multiple header type variants, per-column skeleton dropdown config, explicit scrollbar visibility toggles, and per-cell state variants — pending a design pass to define the actual API surface (currently only visible in a design playground, with no equivalent in the implementation)
- [ ] `bds-table-column` supports declarative `<template>`-based custom cell content as an additive alternative to the existing formatter callback
- [ ] `bds-table`'s toolbar adapts responsively below 744px, signed off by UX/UI before implementation (same gating pattern as the footer's own sign-off)
- [ ] Every new/changed behavior has passing unit tests (coverage phase) added per task
- [ ] A single mutation-testing pass (Stryker, ≥90% per component, documented survivors for anything below 100%) run once across every component this ticket touches, as the final task

## Dependencies

- `EOA-14935-bds-table-v2.md` (shipped, `status: done`) — this ticket continues its deferred scope; specifically depends on the `bds-pagination` `totalItems` watcher fix and `loading` prop already shipped there
- `2026-06-16-bds-table-column-api-spike.md` — primary research source
- `@tanstack/virtual-core` (already a direct dependency, `^3.17.1`, used today by `VirtualScrollController`) — unblocks the `virtual` item without adding a new dependency

## Open Questions

- `data` vs `dataset` mutual exclusivity enforcement mechanism — resolved: `Logger.warn`, non-blocking.
- Footer design — resolved: slot-based (`slot="footer"`), not a computed callback prop. A sign-off gate remains in the plan (Task 2) to confirm before implementation actually starts.
- `maxClientRows` default value — proposed `1000`, still needs team confirmation.
- Whether `VirtualScrollController` should eventually be generalized to support true DOM-count virtualization (not just positional) — resolved: yes, technically possible via a windowed-creation model, not by generalizing `VirtualScrollController`'s current positional/`MutationObserver` design (no working precedent found, sits in a real upstream bug class — `TanStack/virtual#1133`, `#1147`, `#823`). Decision: deferred to a separate future spike, out of scope for this ticket. `bds-table` builds its own integration against `@tanstack/virtual-core` directly, fully decoupled from this question. Full research: `ai-work/research/2026-07-06-shared-virtualization-utility.md`; related bug: `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md`.
- Mutation-testing cadence — resolved: one batched pass at the end (plan Task 12), not per-task — this was also how the v2 ticket's own gate was actually run in practice.
- **Not yet resolved:** the four items promoted from the v2 ticket's "Out" list (column grouping/drag-drop-reorder/resizing/row-expand-collapse, header type variants/skeleton-dropdown-config/scrollbar-toggles/cell-state-variants, declarative `<template>` cell content, responsive toolbar below 744px) are now in this ticket's scope but have no corresponding tasks in `ai-work/plans/EOA-14935-bds-table-v3.md` yet — each needs its own design/scoping pass (similar to how the footer needed its own sign-off gate) before tasks can be written and executed. Do not start implementation on any of these until that planning pass happens.
