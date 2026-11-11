---
name: bds-search-bar-task43-vue-vmodel-commit-fix-verified
description: Task 43's applyQuery commit emission is confirmed live — Vue v-model now converges after free-text + Tab/blur, emits exactly one commit valueChange, and React gains nothing new; also records the asymmetry (Vue 4 events vs React 3 for the same typing) and why
metadata:
  type: project
---

Re-verified EOA-19597/98 Task 43 (Chrome, pack pipeline, React + Vue testapps, 2026-10-26). Fix under test:
`bds-search-bar.applyQuery` commits `this.value` and emits `valueChange` behind an equality guard
(`if (this.value !== value) { this.value = value; this.valueChange.emit(value); }`).

Verdict: **fix works, no regression on React.** Evidence (all read from live DOM, not inferred):

- Vue, free text `zzz` + Tab → `v-model` ref `zzz`, host `value` `zzz`, field `zzz`. Previously the ref
  stayed `(empty)` forever ([[bds-search-bar-vue-vmodel-does-not-track-typing]]).
- Vue, `item-7` + Tab → ref `item-7`, field `Item 7` (label). Pick `Item 199` → then select-all + type
  `zzz` + Tab → ref `zzz`, **not** `item-199`; the "one commit behind" symptom is gone.
- Event counts for typing 3 chars: **Vue 4** (`z`, `zz`, `zzz`, `zzz`), **React 3**. Not a divergence bug:
  Vue's `v-model` reads `event.target.value`, which is still the *committed* value during typing, so the
  commit is a genuine `value` change from the component's point of view and the guard lets it through;
  React's controlled handler writes `event.detail` back on every keystroke, so by commit time `value`
  already equals the typed text and the guard suppresses a 4th event. Both are correct.
- The commit event fires exactly **once** per commit even when both dismissal paths run: typing then
  clicking the page gutter (popover-close → `commitTypedQuery` *and* blur → `commitTypedQuery`) yields
  3 + 1 events, never 3 + 2.
- Blur **after** the debounce already committed adds 0 events and 0 React renders; a second Tab, a
  focus+blur with no typing, and a second focus+blur likewise add 0 events / 0 renders
  (React render counter flat at 116 across all three repeats).
- Uncontrolled bar (no `value` binding) proves the emission actually exists: typing `abc` + waiting yields
  3 keystroke events **+ 1 commit event with detail `abc`**, and the host `value` becomes `abc`. Without
  the fix this stage produces 3 events and sets `value` silently — so an uncontrolled bar, not a v-model
  bar, is what distinguishes "the fix works" from "the guard suppresses everything".
- Pre-existing, untouched by this fix (already logged as plan Task 22): a clear emits `valueChange ""`
  twice (bar + bubbled child) plus a `bdsSearch {value:""}`; a pick emits its own `valueChange` plus one
  bubbled from the inner `bds-select` (filter by `event.target === host` when counting).

**How to apply:** when verifying a commit-emission fix, always run the *uncontrolled* variant too — a
v-model harness can mask the emission behind the equality guard and look identical to a broken fix.
