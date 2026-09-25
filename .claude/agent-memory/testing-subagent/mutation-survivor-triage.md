# Mutation-survivor triage without re-running Stryker

Verified 2026-09-25 (EOA-17662 Tasks 53/53a, `bds-date-picker` consolidated pass). Full detail
promoted to `.agents/memory/mutation-testing-stryker-setup.md`; this is the per-scope digest.

## Read the incremental JSON, not the clear-text log, for the exact mutant

`packages/boreal-web-components/reports/stryker-incremental.<config>.json` (in the mutation
worktree) has, per mutant: `id`, `mutatorName`, `replacement`, `status`, `killedBy`, `coveredBy`,
and `location.start/end` (line + **columns**). The clear-text console diff is lossy: for chained
`A && B && C`, a `LogicalOperator` survivor prints `A || B && C` with **no parentheses**, which
reads as `A || (B && C)`, but the real AST mutant is `(A || B) && C`. Reproduce both forms before
declaring equivalence — they behave differently. `testFiles[].tests[]` maps test IDs to names,
and counting JSON `status` values reproduces the console summary table exactly.

## kill `disconnectedCallback` detach mutants by spying, not dispatching

mock-doc ignores `AbortSignal` abort, so `KeyboardController.detach()` doesn't actually remove
listeners under `newSpecPage`; dispatching keys after `element.remove()` emits for the original
too. `element.remove()` *does* run `disconnectedCallback`, so spy the controller's method:
`jest.spyOn((page.rootInstance as unknown as { _keyboard: { detach: () => void } })._keyboard, 'detach')`.

## `date-fns` undefined coercion → `x !== undefined &&` guards are equivalent

`compareAsc(valid, undefined)` returns `NaN`; the project's `compareDates` narrows `NaN` to `0`.
`isSameDay(valid, undefined)` returns `false`. So `grid.ts` mutants replacing any
`x !== undefined` guard (weekStartsOn/min/max/rangeStart/rangeEnd/previewEnd) with `true` are
equivalents, not gaps — do not invent a test for them.

## Fast harness for proving a test kills a mutant (when Stryker can't be run)

Copy the source file into the owning `__test__/` dir, rewrite relative imports/styleUrl for the
new depth, rename the class+tag, apply one mutation, and run a throwaway spec replicating the
new test's assertions against the copy — the assertion must **fail** on the mutant and pass on the
real module. Delete the copies afterwards. A full copy of `bds-calendar-grid.tsx` compiles fine
under `newSpecPage` this way.
