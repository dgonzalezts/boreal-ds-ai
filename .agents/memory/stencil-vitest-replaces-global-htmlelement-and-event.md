# `@stencil/vitest` swaps the global `HTMLElement` and restores Node's `Event`

Verified on `@stencil/vitest` 1.16.1, Vitest 5.1.0, Stencil 4.45.2 (EOA-20193 spike, 2026-11-13).

## The Problem

Under the `stencil` environment, `@stencil/vitest`:

- replaces the global `HTMLElement` with a subclass of mock-doc's `MockHTMLElement`;
- restores Node's global `Event`.

Consequences for specs written for Stencil's Jest runner:

- Specs that patch `HTMLElement.prototype` (`focus`, `showModal`, `attachInternals`) never reach elements created by mock-doc.
- Specs that build events with global constructors get events whose handlers do not fire.

## The Fix

In a setup file, reset the global `HTMLElement` to the base class (the prototype of the wrapper). This fixed about 27 of 52 failing files. A Proxy that swaps `.prototype` was worse: it broke 361 of 377 files. Setting the global `Event` to mock-doc's `Event` made no difference. The remaining failures were not fully classified.

```ts
const wrapper = globalThis.HTMLElement as unknown as { new (): HTMLElement };
const base = Object.getPrototypeOf(wrapper) as typeof wrapper;
Object.defineProperty(globalThis, 'HTMLElement', { configurable: true, writable: true, value: base });
```

## How to verify

Run a spec that patches `HTMLElement.prototype.focus` (for example `focus.spec.ts`) under Vitest before and after the reset.

Related: [[stencil-vitest-plugin-fails-on-mixin-components]], [[stencil-mock-doc-no-activeelement-focus-tracking]].
