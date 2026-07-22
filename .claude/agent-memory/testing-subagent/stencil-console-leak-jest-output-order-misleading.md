---
name: stencil-console-leak-jest-output-order-misleading
description: When a console warning/info leaks during a multi-file scoped test run, Jest's parallel-worker output order does not reliably indicate which spec file emitted it — isolate the file to confirm before editing
metadata:
  type: project
---

When `pnpm --filter <pkg> run test -- <scoped-path>` runs multiple spec files in parallel (`--max-workers=8` by default via Stencil's Jest wrapper), a `● Console` block in the output appears adjacent to whichever file's `PASS` line the reporter happened to flush nearest in time — **not necessarily the file whose `PASS` line immediately precedes or follows it**. Do not assume adjacency means causation.

**Confirmed case:** `bds-button` scoped run showed a console block (2x `console.warn`, 4x `console.info` from `checkAccessibleName()`) printed directly after `bds-button-a11y.spec.ts`'s `PASS` line. That file already had matching `jest.spyOn(console, 'warn'/'info').mockImplementation()` scoped correctly per-test, so it looked like a real bug (spy not working). Running each spec file in isolation (bare positional path pointed at exactly one file, see [[stencil-test-invocation-vs-jest-direct]]) proved the leak actually came from `bds-button-slots.spec.ts`, which had no console suppression at all — its icon-only/badge-only fixtures incidentally triggered the component's real accessible-name diagnostics as a side effect of testing render/slot behavior, unrelated to what that file was asserting.

**How to apply:** before editing a spec file to fix a console leak, isolate the suspected file with the exact same scoped-invocation pattern (`pnpm --filter <pkg> run test -- <exact-file-path>`, no extra flags before the path — inserting flags like `--runInBand` before the positional path broke Stencil's scoping and silently ran the entire 200+ file suite instead of one file). Confirm the leak reproduces alone before attributing it.

Fix applied: added a `suppressConsoleInfo()` twin to the existing `suppressConsoleWarn()`/`suppressConsoleError()` helpers in `packages/boreal-web-components/src/utils/testing/mocks/console.ts` (same beforeEach/afterEach spy-with-mockImplementation shape), then called both `suppressConsoleWarn()` + `suppressConsoleInfo()` at module top level in `bds-button-slots.spec.ts` — matching the already-documented sibling convention [[stencil-suppress-console-warn-sibling-convention]] (`.agents/memory/`), extended here to cover `console.info` as well as `console.warn`.
