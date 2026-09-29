# mock-doc does not render `<slot>` elements — `slotchange` on a real slot is untriggerable

## The gap

A probe (`popover.querySelectorAll('slot').length`) returns **0** under `@stencil/core/mock-doc@4.42.1` for a non-shadow (light DOM) component, even though the compiled render clearly emits `<slot>` (and `<slot onSlotchange={...}>`) elements. So a spec cannot locate a slot element to `dispatchEvent(new Event('slotchange'))` on, and an `onSlotchange` handler bound to a slot never fires in `newSpecPage`.

This is consistent with the separate finding that Stencil relocates slotted children and that `hasSlotContent`-style checks behave differently in mock-doc (see `stencil-non-shadow-slot-relocation-before-componentdidload.md`).

## Workaround for covering an `onSlotchange` handler

Reach the handler directly and hand it an event whose `target` you set yourself. `MockEvent.target` is a plain writable field (assigned during dispatch), so `Object.assign` works:

```ts
const slotChange = new Event('slotchange');
Object.assign(slotChange, { target: someElement });
(instance as unknown as { handleSlotUpdate: (e: Event) => void }).handleSlotUpdate(slotChange);
```

This executes the real handler body (including the `handleSlotChange(e, show, hide)` delegation and its listener wiring), which is otherwise unreachable in mock-doc. Note in the spec/catalog that the DOM path itself is only verifiable in a browser.

Found hardening `bds-popover`'s `handleSlotUpdate` (2026-09-28).
