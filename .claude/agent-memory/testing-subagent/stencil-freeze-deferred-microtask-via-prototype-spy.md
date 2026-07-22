---
name: stencil-freeze-deferred-microtask-via-prototype-spy
description: How to deterministically capture a component's pre-async-init render state in newSpecPage when the init is deferred via Promise.resolve().then() from componentDidLoad
metadata:
  type: project
---

When a Stencil component defers work out of `componentDidLoad` with a bare microtask
(`if (cond) void Promise.resolve().then(() => this.initX());` — done to avoid Stencil's dev-mode
"state changed during componentDidLoad()" warning when the deferred call itself mutates `@State()`),
that microtask has almost always already resolved by the time `await newSpecPage(...)` returns —
`await` on the outer promise flushes the whole microtask queue, including one scheduled
synchronously inside `componentDidLoad`. You cannot rely on "assert right after `newSpecPage`
resolves, before `waitForChanges()`" to observe the pre-init state; by then it's too late, and
setting a prop that changes render output (`root.data = buildRows(n)`) only re-renders using
whatever state already exists — if the deferred init already ran, you get post-init output no
matter when you assert.

**The reliable fix: spy out the private init method on the class prototype *before* calling
`newSpecPage()`, with a no-op mock implementation.** This freezes the "not yet initialized"
condition indefinitely — no timing race, no reliance on when the harness happens to flush
microtasks:

```ts
const initVirtualizerSpy = jest
  .spyOn(BdsTable.prototype as unknown as { initVirtualizer(): void }, 'initVirtualizer')
  .mockImplementation(() => {});

const page = await newSpecPage({ components: [BdsTable, ...], html: '...' });
const root = page.root as HTMLBdsTableElement;
root.data = buildRows(5000);
await page.waitForChanges();
// this.virtualizer stays undefined forever — renderBody() keeps taking the
// pre-init branch no matter how many waitForChanges() calls happen.

initVirtualizerSpy.mockRestore();
```

To then assert the *transition* into the post-init branch within the same test/component
instance (proving the fix actually swaps branches, not just that two separately-mounted pages
look different), `mockRestore()` and call the now-real private method directly via
`page.rootInstance` (see also `component-accessor-naming-conventions`-adjacent pattern of reaching
private members through `rootInstance`, already documented for other components) — this works
because a TS `private` method is only a compile-time restriction, the JS method still exists on
the prototype at runtime and `componentDidLoad`'s synchronous DOM-dependency setup (e.g. resolving
`this._tableWrapperEl` via `querySelector`) already ran normally before the spy intercepted only
the deferred call:

```ts
const instance = page.rootInstance as unknown as { initVirtualizer(): void; virtualizer?: unknown };
instance.initVirtualizer();
await page.waitForChanges();
expect(instance.virtualizer).not.toBeUndefined();
```

Verified in `bds-table.virtual.spec.ts`'s "pre-virtualizer render (placeholder)" describe block
(EOA-15507 Task 7 follow-up, 2026-07-22), regression-testing a real bug where the first render with
`virtual={true}` and no virtualizer yet fell through to rendering the *entire* dataset as real
`<tr>` nodes instead of a bounded placeholder — crashed the browser with 5,000 rows. All 4 new
tests (small dataset, large dataset, placeholder height, before/after transition) pass without any
`setTimeout`/fake-timer trickery.

Candidate for promotion to `.agents/memory/` — this pattern generalizes to any Stencil component
that defers `@State()`-mutating init work out of `componentDidLoad` via a bare microtask (not
specific to `bds-table` or `@tanstack/virtual-core`).
