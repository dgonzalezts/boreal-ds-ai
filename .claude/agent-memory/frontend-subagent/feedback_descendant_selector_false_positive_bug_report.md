---
name: feedback_descendant_selector_false_positive_bug_report
description: A reported "extra/duplicate/phantom row" in bds-table row-detail turned out to be a test-query artifact, not a component bug — verification technique to rule this out fast
metadata:
  type: feedback
---

A user-visible bug report of an "extra empty row" appearing when toggling `bds-table` row-detail expand/collapse was **not reproducible as an actual DOM defect**. The real cause: the diagnostic/reproduction query used a broad CSS descendant selector (`tbody tr`), which matches a `<tr>` at *any* depth under *any* ancestor `<tbody>` — including a `<tr>` that lives inside the **consumer-authored** `<template slot="row-detail">` content itself (e.g. a demo detail panel containing its own nested `<table><thead><tr>...`), which sits inside the outer table's real detail `<tr>`/`<td>`. That inner header `<tr>` has the outer `<tbody>` as a legitimate (if distant) ancestor, so `tbody tr` double-counts it as if it were a sibling top-level row.

**Verification technique that resolved it in under 5 minutes:** compare `outerTbody.children.length` (direct children only) against `t.querySelectorAll('tbody tr').length` (any-depth descendants). If the direct-child count matches the expected `rows + expanded-detail-rows` total exactly, and the extra entries in the broader query all have `.closest('.bds-table__detail-content') !== null`, the "duplicate" is nested consumer content, not a component defect — no code change needed.

**Why to apply this early:** before touching `renderRow`/`renderDetailRow`/`visibleFlatRows` on a "duplicate row" report, always distinguish `:scope > tr` / `.children` (direct) from a bare descendant selector — see also [[stencil-mockdoc-no-scope-selector]] for the related `newSpecPage` constraint (mock-doc has no `:scope`, but a live browser does, and `Array.from(el.children)` works in both).
