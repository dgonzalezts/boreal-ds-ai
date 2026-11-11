# Verifying a `VirtualWindow` host in an ad-hoc spec requires four module-scope mocks (EOA-19598)

## The trap

A throwaway spec that imports only `renderItemsPage`/`windowItems` from
`bds-search-bar/__test__/search-bar-items.test-utils.ts` renders the list but
**mounts zero items** — `windowItems(root)` returns `[]` and both spacers read
`0px`, on the very first render, before any code under test has run.

Cause: `@tanstack/virtual-core`'s `observeElementRect` measures the scroll
element with `getBoundingClientRect()`, which mock-doc returns as all-zeros.
A zero-height viewport yields an empty `getVirtualItems()`, so
`VirtualWindow.getItems()` short-circuits to `[]`.

The real spec files each call this mock set at **module scope** (they are
`beforeAll`/`afterAll`-based, so they do not work inside `it`):

```ts
import { setupElementLayoutMock, setupMutationObserverMock, setupPopoverMocks, setupResizeObserverMock } from '@/utils';

setupPopoverMocks();
setupMutationObserverMock();
setupResizeObserverMock();
setupElementLayoutMock({ viewportHeight: LIST_VIEWPORT_HEIGHT, viewportWidth: 400, itemHeight: 28 });
```

`setupElementLayoutMock` patches `HTMLElement.prototype.getBoundingClientRect`
(and `offsetHeight`/`offsetWidth`) in `beforeAll`; it is the one that actually
fixes the empty window. Omitting it produces a *false negative* ("the fix did
nothing") that looks like a component bug.

With the full set, 1000 items at `scrollTop` 14000 mount 18 rows starting at
`aria-posinset="496"` — the same numbers the browser repro reported.

## Deleted-scratch verification pattern

To prove behaviour without editing a shipped spec: write
`__test__/zz-scratch-verify.spec.ts`, run
`pnpm --filter @pxglobal/boreal-web-components run test -- src/.../zz-scratch-verify.spec.ts`,
then `rm` it and confirm `git status --short` shows only the component file.
`console.log` inside `it` survives Stencil's Jest reporter and prints under
`console.log`.

## Related fact used by the same fix

Stencil's `@Watch` receives `(newValue, oldValue, propName)`, so an
append-vs-replace discriminator is `previous?.[0]?.value !== next?.[0]?.value`
— `undefined !== 'x'` correctly covers both the first assignment
(`oldValue === undefined`) and `[] → [...]`.
