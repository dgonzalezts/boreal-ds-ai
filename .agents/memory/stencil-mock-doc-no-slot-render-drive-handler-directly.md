# mock-doc Does Not Distribute Slots — Drive `slotchange` Handlers Directly

## The Gap

`newSpecPage` runs on `@stencil/core/mock-doc`, which has no shadow DOM and does not perform slot distribution. A component's `<slot>` elements exist in the markup, but real slotting never happens, so a native `slotchange` event is **never** fired by the environment against a `newSpecPage` fixture.

Consequence: any `onSlotchange` / `handleSlotUpdate` behavior (re-wiring a trigger from the default slot, toggling a named-slot region) is unreachable through the rendered DOM in a spec. A test that mutates the fixture's children and awaits `waitForChanges()` to trigger a slot change is a no-op — nothing re-wires.

## The Workaround

Drive the handler directly with a hand-built `slotchange` event whose `target` is the element the handler reads. `target` is not settable through `new Event(...)`, so assign it with `Object.assign`:

```ts
const slotChange = new Event('slotchange');
Object.assign(slotChange, { target: trigger });
instance.handleSlotUpdate(slotChange);
await page.waitForChanges();
```

`handleSlotUpdate` is a private arrow-function property, so it is reachable from the spec through a typed `page.rootInstance` cast. Verified pattern: `bds-popover-basics.spec.ts` — `re-wires the trigger when the default slot content changes`.

## Source

`ai-work/testing/failure-modes/bds-popover.md` FM-16 (the catalog row records the same limitation). Found while auditing `bds-popover`'s slot-trigger wiring, EOA-17662, 2026-09-28. Same class of environment gap as the other mock-doc entries in this directory (no `DragEvent`/`DataTransfer`, no focus tracking, no `getComputedStyle` custom properties).
