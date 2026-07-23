---
name: stencil-virtual-table-needs-maxheight-to-bound-dom
description: bds-table virtualization only bounds rendered <tr> count when maxHeight gives the wrapper a bounded scroll container; without it the virtualizer's "visible window" equals full content height and renders (almost) everything anyway.
metadata:
  type: project
---

When manually verifying `bds-table` virtualization (opt-in `virtual` or the `maxClientRows`
auto-enable guardrail, EOA-15507 Task 10), a playground/test table with `virtual`/`effectiveVirtual`
true but **no `maxHeight` set** will NOT show a bounded `<tr>` count — TanStack Virtual computes its
visible window from the scroll container's own height, and an unbounded `.bds-table__wrapper` (no
`max-height`) just grows to fit all content, so the "visible" window covers nearly the entire
dataset.

This is exactly why `checkVirtualMaxHeight()` already exists and warns `'`virtual` is enabled without
`maxHeight` set...'` — that warning is the signal, not just a nice-to-have. Any manual verification
of a virtualized `bds-table` scenario (Playwright DOM-count checks included) must set
`max-height="<value>px"` on the table, or the DOM-count assertion will silently pass/fail for the
wrong reason (looks like "virtualization isn't bounding rows" when actually it's "no bounded
container to window against").

See [[stencil-dev-server-hashed-chunk-stale-cache]] for a related dev-server verification gotcha
found in the same virtualization work (EOA-15507 Task 7/8/10).
