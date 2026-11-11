# bds-select `valueString` / `managed` text ownership — spec mechanics

Context: EOA-19597 Task 12 (2026-10-23) added two tests-relevant behaviours to `bds-select`:
`loadValue()` clears `valueString` when `value` resolves to no mounted option, and
`@Watch('valueString')` early-returns on `''` while `value` is committed (`hasValue`).

## Where the tests live

`src/components/forms/bds-select/__test__/bds-select.basics.spec.ts` already owns both the
`valueString` watch block and a `loadValue (single select)` block added by this task. That file
calls `suppressConsoleWarn()` + `setupPopoverMocks()` but **not** `suppressConsoleError()` —
extend it rather than adding a seventh spec file, and don't add a suppress hook it doesn't have.

## Proving a "field was not written" assertion is not vacuous

`updateElementAttr(this.bdsField, 'value', x)` calls `setAttribute` on the same element node
`root.querySelector('bds-text-field')` returns, so `jest.spyOn(textField, 'setAttribute')`
intercepts it. A negative assertion (`not.toHaveBeenCalledWith('value', expect.any(String))`)
on its own could pass because the spy never sees anything — pair it with a **positive** assertion
on the same spy in the sibling test that exercises the write path (the "no value committed still
clears the field" case) so the mechanism is self-verified inside the file.

## Values that matter

- `bds-text-field`'s `value` prop is `@Prop({ mutable: true, reflect: true })` with default `''`,
  so a freshly mounted field already carries `value=""` — managed-mode assertions are
  `getAttribute('value') === ''`, not `null`.
- `bds-list-menu-item.selected` is `@Prop({ reflect: true })`, so "option selected" is an
  attribute assertion after `await page.waitForChanges()`.
- mock-doc **does** implement `HTMLElement.scrollIntoView()` (`@stencil/core/mock-doc`), so
  `jest.spyOn(option, 'scrollIntoView')` works and is the cleanest proof that the `.then()` body
  after the `if (!this.managed)` guard still executed (`toHaveBeenCalledWith({ block: 'nearest' })`).
  Install the spy *before* driving the second `value` change — the initial `loadValue()` in
  `componentDidLoad` has already run by the time `newSpecPage()` resolves.
- `value` accepts `string | string[]` even in single-select (`loadValue` uses `value[0]`); set
  `root.value = ['2']` to reach the array branch of the `hasValue` guard.

## Scoped coverage numbers for this folder (do not treat as a regression)

`test:coverage` scoped to `src/components/forms/bds-select` exits 1 on the repo's configured
global **branch** threshold (80%) regardless of these tests: 71.92% branches / 88.57% statements
without the Task-12 tests, 73.64% / 89.34% with them. Statements clear the 80% Phase-1 gate;
branch does not and never did. Measure a baseline without editing files by excluding the new
tests with a negative lookahead:
`--testNamePattern="^(?!.*(phrase one|phrase two)).*$"` — Stencil's CLI forwards
`--testNamePattern` verbatim (unlike `--testPathPattern`, which it mangles).
