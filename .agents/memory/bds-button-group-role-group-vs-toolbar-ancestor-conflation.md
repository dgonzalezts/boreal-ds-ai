# `bds-button-group` conflated explicit `role="group"` with a toolbar-ancestor context

`bds-button-group`'s internal `_role` getter resolved to `'group'` in two genuinely different scenarios and treated them identically:

1. A consumer explicitly passes `role="group"` as an attribute (e.g. `bds-table`'s toolbar button group).
2. The button group is nested inside an ancestor element with `[role="toolbar"]`, where that ancestor is expected to own keyboard navigation itself.

`_setupKeyboard()` used `if (this._role === 'group') return;` to skip setting up roving-tabindex Arrow-key navigation — correct for scenario 2 (the toolbar ancestor already manages focus), but wrong for scenario 1, where there is no ancestor managing anything and the button group is the only thing that could. This silently broke Tab/Arrow-key navigation for `bds-table`'s Filter/Column-visibility toolbar buttons.

**Symptom was most visible in Safari**, whose Tab-order model is stricter about ARIA group semantics than Chrome/Firefox (which still let native `<button>` elements take Tab focus regardless of an ancestor's resolved ARIA role) — but the underlying bug was not Safari-specific; it was a pure logic conflation.

**Fix**: check for the actual `[role="toolbar"]` ancestor directly (`this.el.parentElement?.closest('[role="toolbar"]') != null`), not the resolved `_role` string, so the roving-tabindex setup only skips when a real toolbar ancestor exists to take over.

**General takeaway**: when a component's internal logic branches on a computed/resolved value derived from multiple possible sources (an explicit prop, an inherited attribute, an ancestor's context), verify each source independently rather than collapsing them into one shared code path — they often warrant different behavior.

**Source**: EOA-16000 `bds-table` v4 cross-browser QA session (Safari focus/keyboard investigation).
