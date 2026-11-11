---
name: bds-search-bar-t22-t47-regression-mechanics
description: How to pin the ten bds-search-bar behaviour fixes (T22/T24/T29/T32/T34/T35/T40/T45/T46/T47) in newSpecPage — which assertions discriminate, which only lock an invariant, and the mock-doc gaps involved
metadata:
  type: project
---

Regression specs for the ten `bds-search-bar` fixes landed 2026-10-26 (EOA-19597/19598). Authored in
`bds-search-bar.events.spec.ts` (T22/T24/T29/T46/T47), `…items.spec.ts` (T32/T34/T35),
`…variants.spec.ts` (T45) and `…a11y.spec.ts` (T40). Read with
[[bds-search-bar-items-mode-test-harness]] and [[bds-search-bar-t30-t31-regression-mechanics]].

**Which assertions actually discriminate the fix (verified by per-fix source reverts).**

| Fix | Fails without the fix | Passes either way (invariant lock) |
| --- | --- | --- |
| T22 child-event boundary | 1 `bdsClear` on X-clear; 1 `bdsSearch` + 1 `valueChange` on pick (2 modes each) | 3 `bdsInput` + 4 `valueChange` on typing; Escape's single `bdsClear` |
| T24 slotted labels | picked label, programmatic label, mounted-over-captured, captured-after-unmount | free text, `mode="search"` raw value |
| T29 trigger reopen | reopen (items + slotted), no-reopen with no list, no-reopen disabled | `mode="search"` (no popover exists) |
| T32 duplicates | warn-once, no-second-warning | keeps both entries, no warning in `mode="search"` |
| T34 items → undefined | close with no slotted list | stays open with slotted list, `[]` empty state |
| T35 retry budget | removing the `mountRetryFrames` cap guard makes the retries run past the budget | — |
| T40 `aria-controls` | all three resolution tests | extended list-less test (`''`) |
| T45 clear after pick | pick, programmatic value, hide-after-clear | `variant="static"` rules |
| T46 select-on-focus | pointer pick, keyboard pick | free text not selected |
| T47 always-emit | none — no source change; locks the documented contract | both |

**Typing after `root.value = …` needs `page.waitForChanges()`.** A `flushMicrotasks()` alone leaves
the field input's `value` attribute at `''`; the slotted/programmatic label tests read
`input.getAttribute('value')` and must `await flushMicrotasks(); await page.waitForChanges();`.

**mock-doc has no `setSelectionRange`.** `selectInputText()` feature-checks `typeof
input.setSelectionRange === 'function'`, so T46 must install a per-input shim
(`Object.defineProperty(input, 'setSelectionRange', { configurable: true, value: jest.fn() })`) and
then settle ~3 frames — `selectCommittedText()` defers to `requestAnimationFrame`. Clear the shim
(`mockClear()`) after the pick: the popover-close path also selects, and the test is about the focus
path.

**`field.clearable` cannot prove T45 in list mode — two writers.** `bds-select.loadDefaultProps()`
writes `clearable = !this.static` straight onto the shared field, and the search bar only patches the
same prop when *its* `canShowClear` value changes, so a stale `true` can survive. Assert
`canShowClear` on `page.rootInstance` (the value the render passes down) plus `field.clearable`
after a transition that does flip it (post-clear). `mode="search"` has no select, so
`field.clearable` is the honest observable there. `hasValue` is internal — leave it out of the
expectations or the `variant="static"` "unchanged" test fails for the wrong reason.

**T35 retry budget: `jest.spyOn(global, 'requestAnimationFrame')`, don't fake timers.**
`setupAnimationFrameMocks()` defines rAF as `setTimeout(cb, 0)` (writable + configurable, so the spy
works and still calls through). Mount with no `items`, assign them, then remove
`.bds-search-bar__list .bds-list-menu__content` **before every frame tick** and `await new
Promise(r => setTimeout(r, 0)); await flushMicrotasks();`. Loop while
`instance.mountRetryFrames < ITEMS_MODE_MOUNT_MAX_FRAMES` (bounded by `2×` for safety), record
`requestAnimationFrame.mock.calls.length`, run 5 more ticks, then assert: `mountRetryFrames` is
`ITEMS_MODE_MOUNT_MAX_FRAMES`, `mountRetryFrame` is `null`, the schedule-spy call count is unchanged,
and `VirtualWindow.prototype.mount` was never called. Removing the content once is not enough — the
list menu re-creates it on a re-render, hence the remove-per-tick. Removing the `mountRetryFrames`
guard makes the retries run past the budget (observed 125+) and the test fails.

**`aria-controls` details.** In a list-less `mode="list"` fixture the attribute stays *present but
empty* (the fix only removes it in `mode="search"`), and `page.doc.getElementById('')` returns the
**document**, not `null` — never assert null there. In items mode the id comes from `bds-select`
(`.bds-search-bar__list`), in slotted mode from the consumer list. `items` **plus** a slotted list
resolves to the hidden slotted list (`role="menu"`) — a real gap, catalogued as PD-06 rather than
tested.

**An X-clear emits more than one event.** `bds-select.listenClearInput → setValue('') → bdsChange →
handleSelectChange` adds a second `valueChange` **and** a `bdsSearch {value: ''}` to the clear. That
is host-targeted from the search bar itself, so `event.target` assertions cannot separate it from the
"leaked child event" class; T22 asserts only the `bdsClear` count. Open as PD-05.

**Copying a sibling spec's `components` array by hand is a trap.** `bds-list-menu-item` is imported as
`BdsListMenuItem` throughout this folder; an invented variant of that identifier compiles fine,
becomes an unregistered tag in `newSpecPage`, and the child simply never renders (the failure surfaces
much later as "the pick emitted nothing"). Copy the array verbatim or use `SEARCH_BAR_COMPONENTS`.
