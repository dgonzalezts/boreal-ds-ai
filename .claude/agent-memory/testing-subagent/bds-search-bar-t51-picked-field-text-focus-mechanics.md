# bds-search-bar T51 — proving the synchronous picked-field application

Context: plan T51 (`EOA-19597`), fix in `bds-search-bar.tsx` — `handleSelectChange` calls
`applyPickedFieldText()` (write `fieldText` → `focus()` → `selectInputText()`) inside the pick handler,
guarded by `isApplyingPickedFocus`, which also short-circuits `selectCommittedText()`.

## A focus tracker that swallows the focus event can hide the guard it exists to prove

`installFocusTracker()` in `search-bar-items.test-utils.ts` replaced `HTMLElement.prototype.focus` with
a recorder that never dispatched a `focus` event. Good for "was focus moved, and in what order", but it
makes any guard that only matters *because of the focus event it causes* untestable: the component's own
`handleFocus` → `selectCommittedText()` never ran, so deleting `isApplyingPickedFocus` from
`selectCommittedText()` left "exactly one `setSelectionRange` call per pick" still green.

Fix: the helper now takes `installFocusTracker({ dispatchFocusEvent: true })`, which dispatches
`new Event('focus')` (bubbles: false) on the element from inside the patched `focus()`.

**Do not delegate to the original `focus()`.** mock-doc's `HTMLElement.focus()` dispatches a
`MockFocusEvent` with `bubbles: true, composed: true`, and mock-doc's `triggerEventListener` walks
ancestors — so `input.focus()` bubbles to `bds-text-field`'s Host `onFocus` handler, which calls
`input?.focus()` again. That recursion only stops via mock-doc's per-listener `try/catch`, so it emits
one `bdsFocus` per recursion level (the search bar's `handleFocus` runs many times) and logs a
`RangeError`. Dispatching a non-bubbling event on the input reproduces the browser's real `focus`
(non-bubbling; only `focusin` bubbles) and reaches the input's own `onFocus` → `bdsFocus` chain exactly
once.

## Which assertions actually fail without the fix

- Remove the `this.applyPickedFieldText();` call → the three positive tests fail (no focus recorded,
  `input.value` still `""` in slotted mode). The programmatic-`value` test and the `mode="search"` test
  still pass: they are negative-path guards, not proofs of the call.
- Remove only `this.isApplyingPickedFocus ||` from `selectCommittedText()` → "exactly once" fails with
  **2** calls (1 synchronous + 1 from the rAF the pick's own focus event scheduled). That is the only
  test that kills the guard mutant, which is why the tracker must dispatch.

## Mechanics worth reusing

- `setSelectionRange` is absent on mock-doc inputs (`selectInputText` feature-checks it), so install a
  per-input shim (`Object.defineProperty(input, 'setSelectionRange', { value: jest.fn() })`) and assert
  the arguments (`0`, label length). The resulting caret range is not modelled — do not claim it.
- Assert *before* the first `await`: "synchronously, inside the handler" is the whole contract, and any
  `await page.waitForChanges()` would let the deferred path hide a missing synchronous write.
- Still assert after `settleFrames()` for the call-count test, since the deferred rAF selection is the
  thing that must *not* happen.
- `input.value` is attribute-backed in mock-doc (`patchPropAttributes`), so the property and
  `getAttribute('value')` agree.
- The `mode !== "list"` guard is unreachable through the DOM there (no `bds-select` is rendered), so that
  test calls `applyPickedFieldText()` on `page.rootInstance` directly — the sanctioned internal-member
  pattern.
