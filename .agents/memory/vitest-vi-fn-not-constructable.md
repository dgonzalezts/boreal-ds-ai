# In Vitest 4 and 5, `vi.fn(() => x)` cannot be called with `new`

Verified on Vitest 5.1.0 (EOA-20193 spike, 2026-11-13).

## The Problem

A mock built from an arrow function, such as `jest.fn(() => ({ observe }))` used as a `ResizeObserver` constructor, throws when called with `new` under Vitest 4 and 5. Under Jest it works. In the spike this failed 59 spec files.

## The Fix

Give the mock a `function` expression implementation. In `src/utils/testing/mocks/observers.ts`:

```ts
const mock = jest.fn().mockImplementation(function () {
  return methods;
});
```

For a suite migrated without editing every spec, a setup file can wrap every implementation passed to `vi.fn` / `mockImplementation` in a `function` (shim in the spike document).

## How to verify

Run a spec that mounts a component using `ResizeObserver` (for example `bds-pagination`) under Vitest: before the change `TypeError: ... is not a constructor`, after it green.

Related: [[stencil-vitest-plugin-fails-on-mixin-components]], spike `ai-work/research/2026-11-13-EOA-20193-stencil-vitest-migration-spike.md`.
