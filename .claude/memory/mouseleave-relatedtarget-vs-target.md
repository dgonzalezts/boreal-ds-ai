# `mouseleave` Must Use `e.relatedTarget`, Not `e.target`, for "Stay on Hover" Logic

When implementing hover-stay behaviour on a floating element (tooltip, popover, dropdown), the `mouseleave` listener on the trigger must pass `e.relatedTarget` — the element the pointer is moving *into* — not `e.target` — the element being *left*.

**Wrong — `stayOnHover` is silently broken:**
```ts
trigger.addEventListener('mouseleave', (e: MouseEvent) =>
  this.hide(e.target as HTMLElement)
);
```

**Correct:**
```ts
trigger.addEventListener('mouseleave', (e: MouseEvent) =>
  this.hide(e.relatedTarget as HTMLElement)
);
```

`validateHide()` in `floatingMixin` checks whether the pointer is moving into the floating content (`this.floatingContent.contains(incomingElement)`). Because `e.target` is always the trigger element itself — not the incoming element — `floatingContent.contains(trigger)` evaluates to `false` and the hide is never cancelled. The feature appears to work structurally but produces no effect.

This bug was found in `bds-tooltip.tsx` and was not yet fixed as of 2026-04-13.
