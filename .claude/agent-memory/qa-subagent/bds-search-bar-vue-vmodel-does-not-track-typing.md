---
name: bds-search-bar-vue-vmodel-does-not-track-typing
description: Vue v-model on bds-search-bar never follows typed text or the blur/Tab commit — the Vue wrapper reads target.value (the committed prop) while the component emits typed text only in event.detail, and the blur commit emits no valueChange at all
metadata:
  type: project
---

Confirmed during EOA-19597 Task 18 (wrapper parity, Chrome, 2026-10-26) on the 1,000-item `items` bar in
`examples/vue-testapp`:

- Typing `zzz`: three `valueChange` events fire from `BDS-SEARCH-BAR` with `detail` `z`, `zz`, `zzz`,
  while the `v-model` ref stays `(empty)`. The component's `value` property is still the *committed*
  value during typing (`handleFieldInput` sets `typedText`, not `value`).
- Pressing Tab (blur commit): **no** `valueChange` at all. Field keeps `zzz`, host `value` becomes
  `zzz`, the `v-model` ref stays `(empty)` — it never converges, 900 ms and 60 s later.
- Mouse pick and X-clear DO round-trip the ref correctly.
- Net effect: the ref is permanently one commit behind (after commit 1 the ref holds the pre-1 value,
  after commit 2 it holds commit 1's value) — it only ever receives whatever `value` was at emit time.

Mechanism (both read from source, no speculation):

1. `@stencil/vue-output-target`'s `defineContainer` v-model directive emits `update:modelValue` with
   `resolvePath(e, 'target.value')` — by default the element **property**, not `e.detail` (the
   `bds-search-bar` entry sets no `eventAttr`).
   (`packages/boreal-vue/lib/components.ts` line ~825 passes `'value', 'valueChange'`.)
2. `bds-search-bar.handleFieldInput` emits `valueChange.emit(newValue)` (typed text) but leaves
   `this.value` at the committed value, so the wrapper hands Vue the stale committed value per keystroke.
3. `handleBlur` → `commitTypedQuery()` → `applyQuery()` sets the value with **no** `valueChange` emission
   (unchanged in that respect from the pre-EOA-19597 code), so there is no event to correct the ref.

React is unaffected in practice: its `onValueChange` handler receives `event.detail`, so per-keystroke
events leave the controlled state equal to the last typed text, which matches what blur commits.

**How to apply:** never verify a wrapper `v-model` round-trip for this component with a mouse pick only —
that path passes. Always type free text, then Tab, and read the bound value. Report per-framework; do not
infer Vue from React.
