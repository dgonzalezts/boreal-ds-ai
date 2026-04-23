# Stencil — FACE Component Test Mocks

## Where Shared FACE Mocks Live

Browser API test doubles for Form-Associated Custom Elements (FACE) belong in:

```
packages/boreal-web-components/src/utils/testing/mocks/
```

The `mocks/` folder is separate from `helpers/`, which holds assertion utilities and DOM query helpers. The distinction is:

- `helpers/` — test utilities that assist with assertions and DOM queries (e.g. `assertExists`)
- `mocks/` — test doubles that replace real browser or runtime APIs

All mocks are re-exported through `src/utils/testing/index.ts` → `src/utils/index.ts`. Import via `@/utils`.

Do not inline FACE mocks inside individual spec files.

## Required Exports from `mocks/elementInternals.ts`

### `attachInternals()`

Polyfills `HTMLElement.prototype.attachInternals` so that `newSpecPage` does not throw when a FACE component calls `@AttachInternals()` at construction time. Call inside `beforeAll`.

### `suppressConsoleError()`

Installs `jest.spyOn(console, 'error').mockImplementation(() => {})` in `beforeEach` and calls `jest.restoreAllMocks()` in `afterEach`. Silences the `console.error` that Stencil's mock-doc generates on every `ElementInternals` property access.

**Why this suppression is necessary:** Stencil's mock-doc intercepts every property read on `ElementInternals` instances via a Proxy getter and logs `console.error` before any optional-chain (`?.`) check can prevent it. A guard like `this.internals.setFormValue?.()` does not help — the getter fires on the property access itself, before the call decision is made. Suppressing the console output is the only viable approach inside `newSpecPage`.

**Note:** `suppressConsoleError()` uses `jest.spyOn` — the mock still tracks calls. `expect(console.error).toHaveBeenCalledWith(...)` assertions work alongside suppression.

## Usage Pattern for Every FACE Spec File

```typescript
import { attachInternals, suppressConsoleError } from "@/utils";

describe("bds-[name] ...", () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  // tests...
});
```

Call `suppressConsoleError()` at `describe` block level (not inside `beforeAll` or `it`). Call `attachInternals()` inside `beforeAll`.

Apply this pattern in every spec file for a component that uses `formAssociatedMixin` or declares `@AttachInternals()`.
