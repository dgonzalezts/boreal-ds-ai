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

`validateHide()` (defined on the component, e.g. `bds-tooltip.tsx`, invoked via `floatingMixin`'s `onBeforeHide` hook chain) checks whether the pointer is moving into the floating content (`this.floatingContent.contains(incomingElement)`). Because `e.target` is always the trigger element itself — not the incoming element — `floatingContent.contains(trigger)` evaluates to `false` and the hide is never cancelled. The feature appears to work structurally but produces no effect.

**Status: fixed.** This bug was found in `bds-tooltip.tsx:170` and fixed on 2026-07-01 (`e.target` → `e.relatedTarget`). See `ai-work/qa/bug-reports/EOA-15147-bds-tooltip-bug-001.md` for the full retrospective report, including a compounding bug found in the same session (`bds-tooltip.stories.ts` was silently stringifying boolean/number `floatingOptions` values via unquoted-vs-quoted template-literal interpolation, masking `stayOnHover`'s real behavior and independently breaking `hideArrow`). If this pattern resurfaces in another floating component (`bds-popover`, a future dropdown/menu), check both: (1) `e.target` vs `e.relatedTarget` on the hide listener, and (2) whether any story/demo layer is silently stringifying boolean/number props before they reach the component.
