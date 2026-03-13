# Stencil — FACE Component Test Mocks

## Where Shared FACE Mocks Live

Browser API test doubles for Form-Associated Custom Elements (FACE) belong in:

```
packages/boreal-web-components/src/utils/__test__/mocks.ts
```

This file is separate from `helpers.ts`, which holds assertion utilities and DOM query helpers. The distinction is:

- `helpers.ts` — test utilities that assist with assertions and DOM queries (e.g. `getInner`)
- `mocks.ts` — test doubles that replace real browser or runtime APIs

Do not inline FACE mocks inside individual spec files. Do not add mocks to `helpers.ts`.

## Required Exports in `mocks.ts`

### `mockElementInternals()`

Polyfills `HTMLElement.prototype.attachInternals` so that `newSpecPage` does not throw when a FACE component calls `@AttachInternals()` at construction time.

### `suppressElementInternalsErrors(): () => void`

Suppresses `console.error` output that Stencil's mock-doc generates when any property on an `ElementInternals` instance is accessed. Returns a teardown function that must be called in `afterAll` to restore the original `console.error`.

**Why this suppression is necessary:** Stencil's mock-doc intercepts every property read on `ElementInternals` instances via a Proxy getter and logs `console.error` before any optional-chain (`?.`) check can prevent it. A guard like `this.internals.setFormValue?.()` does not help — the getter fires on the property access itself, before the call decision is made. Suppressing the console output is the only viable approach inside `newSpecPage`.

## Usage Pattern for Every FACE Spec File

```typescript
import { mockElementInternals, suppressElementInternalsErrors } from '@/utils/__test__';

let teardown: () => void;

beforeAll(() => {
  mockElementInternals();
  teardown = suppressElementInternalsErrors();
});

afterAll(() => {
  teardown();
});
```

Apply this block at the top of the `describe` body in every spec file for a component that uses `formAssociatedMixin` or declares `@AttachInternals()`.
