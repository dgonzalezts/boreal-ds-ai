---
name: no-strictnullchecks-non-null-assertion-autofixed-away
description: boreal-web-components tsconfig has no strictNullChecks, so a justified `x!` non-null assertion is a compiler no-op and gets auto-removed by `pnpm lint:fix` via @typescript-eslint/no-unnecessary-type-assertion
metadata:
  type: project
---

`packages/boreal-web-components/tsconfig.json` sets no `"strict"` and no `"strictNullChecks"` — meaning `T | undefined` is assignable to `T` everywhere, without a non-null assertion. Type safety around null/undefined in this package is enforced almost entirely by the `stencil/strict-boolean-conditions` ESLint rule instead of by tsc itself.

**Consequence:** writing `const x: T = a ?? b!;` where `b: T | undefined` — even when the `!` is genuinely justified by a proven invariant (e.g. an earlier early-return already guarantees `b` isn't undefined at that point) — compiles fine with or without the `!`. `pnpm --filter @telesign/boreal-web-components run lint:fix` will silently strip the `!` via `@typescript-eslint/no-unnecessary-type-assertion`, because from tsc's point of view (no strictNullChecks) the assertion changes nothing.

**Why:** discovered implementing EOA-17662 Task 32a (`resolveFallbackDisplayMonth` in `bds-date-picker/utils/value-mapping.ts`) — the plan's own acceptance criteria specified `const anchor: Date = validMax ?? validMin!;` with the `!` framed as "formalizing an already-proven invariant." lint:fix removed it anyway; `tsc --noEmit` was clean both before and after removal, confirming the assertion was never load-bearing for the compiler in this package.

**How to apply:** don't fight lint:fix on this — the assertion-free form is the correct, canonical style for this codebase. When a plan or task spec calls for a non-null assertion to document a proven invariant, expect it to be stripped by `lint:fix`; verify correctness via `tsc --noEmit` passing clean (not by the assertion surviving), and note in the completion report that the assertion was written then autofixed away rather than treating that as an error to fix.
