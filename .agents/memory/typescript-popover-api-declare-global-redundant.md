# `declare global` Popover API Augmentation is Dead Code Since TypeScript 5.2

`showPopover()`, `hidePopover()`, and `togglePopover()` were added to TypeScript's `lib.dom.d.ts` in TypeScript 5.2. The project uses `^5.9.3`.

Any block of this form found in component files is dead code and must be deleted:

```ts
declare global {
  interface HTMLElement {
    showPopover(): void;
    hidePopover(): void;
    togglePopover(force?: boolean): void;
  }
}
```

These blocks were written when the Popover API was only available in Chrome behind an experimental flag and TypeScript had not yet shipped its types. TypeScript merges duplicate interface declarations silently, so there is no compiler warning alerting to the redundancy.

Confirmed: `bds-tooltip.tsx` contained one such block; it was removed and the component compiled correctly. `bds-popover.tsx` compiles without any such block.
