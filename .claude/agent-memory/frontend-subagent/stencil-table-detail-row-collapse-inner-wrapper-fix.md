---
name: stencil-table-detail-row-collapse-inner-wrapper-fix
description: bds-table row-detail collapse animation padding-floor bug fix, plus the follow-up td-height residual fix
metadata:
  type: project
---

## Fix applied (EOA-16000, non-virtualized master-detail collapse)

`bds-table.tsx` `renderDetailRow()` previously put `ref={el => this.applyRowDetail(el, row)}` directly
on the `.bds-table__detail-content` div — the same element carrying the `bds-transition-collapse` mixin
(`grid-template-rows: 0fr` / `1fr`). The mixin's `> * { overflow: hidden }` selector therefore targeted the
consumer's own cloned `<template slot="row-detail">` root. If that root had its own padding (e.g.
`padding: 12px 20px`, exactly what `src/index.html`'s `expand-basic`/`expand-virtual` scenarios use), the
row could never collapse below the padding sum — padding is never compressible below its own total
regardless of `box-sizing`, since a grid item's automatic minimum size only zeroes out for *content*, not
its own declared padding.

Fix: inserted a new `.bds-table__detail-content-inner` div between `.bds-table__detail-content` (keeps the
mixin, unchanged) and the consumer's cloned template root. `applyRowDetail`'s `ref` now targets the new
inner wrapper instead. Because the inner wrapper is the direct child of `.bds-table__detail-content`, the
mixin's existing `> *` selector automatically applies `overflow: hidden` to it with zero new SCSS needed —
the wrapper's own automatic min-size correctly resolves to 0 per spec since it has no padding of its own.
`applyRowDetail`'s `CellContentCache` identity-guard logic (`detail:${rowId}` key, `el.firstChild !== cached`
check) needed no change — it only cares about whatever `el` is passed in.

Verified live via Playwright against the running dev server (`stencil build --dev --watch --serve`):
collapsed height of `.bds-table__detail-content` went from a stuck 24px (12px + 12px padding) before the fix
to exactly 0px after, with the expand animation's open height (178.5px) identical before/after. All 276
`bds-table` spec tests still pass (2 tests in `bds-table.expand.spec.ts` needed updating from
`.bds-table__detail-content` to `.bds-table__detail-content-inner` for `firstElementChild` cache-identity
assertions — `.bds-table__detail-content`'s direct child is now the wrapper, not the cloned content).

## Follow-up fix applied — residual td-height artifact (same session area, later task)

The previously-flagged residual bug is now fixed. `bds-table.scss`'s `&__tr-detail td` selector
(compiles to `.bds-table__tr-detail td`, specificity 0-1-1) already outranks the unscoped global
`td { height: var(--bds-table-cell-height, 55px); ... }` rule (specificity 0-0-1), so adding
`height: auto;` there wins regardless of stylesheet source order — no `!important` or extra
specificity hack needed. Selector is now:

```scss
&__tr-detail td {
  height: auto;
  padding: 0;
}
```

Verified live via Playwright against the running dev server on both `expand-basic` (non-virtual) and
`expand-virtual` scenarios in `src/index.html`: collapsed `tr.bds-table__tr-detail` height went from a
stuck 55px to ~1px (just the `border-bottom`), while expanded height still correctly grows to fit
content (111.5px / 67px measured, well above the old 55px cap) — confirming the outer `<td>` constraint
is gone without breaking the expand-to-fit-content behavior. All 276 `bds-table` spec tests still pass
unmodified (no test asserted on the old 55px collapsed height). Screenshot confirmed no visible blank
strip between rows after collapsing.

Note: project `CLAUDE.md`'s non-negotiable "no inline comments explaining what code does" rule overrides
this skill's own guidance (which allows a one-line SCSS comment for non-obvious specificity overrides) —
when the two conflict, `CLAUDE.md` wins per its explicit "these instructions OVERRIDE any default
behavior" clause. No comment was left on the `height: auto;` line as a result.
