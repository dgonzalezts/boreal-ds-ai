---
name: bds-table-rows-mode-testing
description: Patterns and gotchas for testing bds-table's rows prop (internal pagination + cross-page selection)
metadata:
  type: project
---

`bds-table`'s `rows` mode (internal pagination, cross-page selection) is covered by
`packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.rows.spec.ts`.
Fixture: 25 rows (`id`/`name`), slotted `<bds-pagination items-per-page="10">` gives 3 pages
(10/10/5). Mount via `page.doc.createElement` + manual property assignment (rows is an array
prop, can't be set via HTML attribute string), matching the existing `selectedRows` seeding
pattern already used in `bds-table.selection.spec.ts`.

## Re-emitted event double-counting

`bds-table` listens directly on the slotted `paginationEl` (`paginationEl.addEventListener('bdsPageChange', ...)`,
not JSX-delegated) and then re-emits its own `bdsPageChange` of the **same name** from the host.
If a test dispatches a synthetic `bdsPageChange` on `paginationEl` with `bubbles: true` and also
listens for `bdsPageChange` on the host (`root.addEventListener(...)`), the listener fires
**twice**: once from the original event bubbling up through the light DOM, once from the host's
own re-emission (which reaches its own listener regardless of bubbling, since target === root).
Fix: dispatch the synthetic event with `bubbles: false` — the direct (non-delegated) listener on
`paginationEl` still fires (dispatch always invokes listeners on the target itself), and the
host's re-emission is what reaches `root`'s listener, giving a clean single count. General
lesson: whenever a component re-emits an event under the *same name* it also listens for on a
child, don't bubble a synthetic test dispatch if you're asserting call counts at the parent.

## Stencil dev-mode noise on state writes during componentDidLoad

`bds-table.tsx`'s `componentDidLoad()` calls `setupRowsPagination()` → `sliceVisibleRows()`,
which sets `@State() visibleRows` synchronously during `componentDidLoad`. Stencil's testing
build logs its own framework-level `console.warn` for this ("The state/prop \"visibleRows\"
changed during \"componentDidLoad()\", this triggers extra re-renders...") — separate from the
app's `Logger.warn` (`console.warn('[bds-table]: ...')`). This fires on **every** rows-mode
mount, so a test asserting "no warning logged" must scope the assertion to the specific message
substring (e.g. `expect(warnSpy).not.toHaveBeenCalledWith(expect.stringContaining('data\` and
\`rows\` are set'))`), not `expect(warnSpy).not.toHaveBeenCalled()`. This is implementation
behavior, not a test bug — do not "fix" it by suppressing warnings broadly; scope the assertion
instead. Flagging this pattern is possibly worth promoting to team memory if it recurs on other
components with similar componentDidLoad state writes.

## Empty-state row count

`bds-table` always renders exactly one `<tr>` in `tbody` for the empty state (a single `<td
colspan>` with the empty message), even with zero rows. Don't assert `tbody tr` count `=== 0` for
an empty check — assert on `tbody td.bds-table__empty-state` presence instead.

## BdsPagination readonly prop is writable at runtime

`bds-pagination`'s `@Prop() readonly currentPage` is TS-readonly only; `bds-table.tsx` sets
`this.paginationEl.currentPage = 1` directly on the real registered child instance in
`onRowsChange`, and it works at runtime (Stencil's `readonly` in the `@Prop()` decorator is not
enforced by the runtime setter). Tests can assert `paginationEl.currentPage` after a `rows`
prop change to confirm the reset-to-page-1 behavior.
