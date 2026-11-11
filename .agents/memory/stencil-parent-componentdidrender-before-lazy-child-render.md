---
name: stencil-parent-componentdidrender-before-lazy-child-render
description: "A parent's componentDidRender runs before a lazy child component has rendered its internal DOM, so work mounted into a child's internals must retry on a bounded rAF loop instead of assuming a single attempt succeeds."
---

# A parent's `componentDidRender` runs before a lazy child renders its internals

**The ordering.** Parent and child are separate (lazy) Stencil components. On the render that first introduces a child such as `<bds-select>` → `<bds-popover>` → `<bds-list-menu>`, the parent's `componentDidRender` runs while the child has not yet produced its internal DOM. A selector aimed at a child's internals (`.bds-list-menu__content`) therefore misses on exactly that render.

**Symptom seen:** `bds-search-bar` mounted its `VirtualWindow` from `componentDidRender`, gated on `.bds-search-bar__list .bds-list-menu__content`. The first items-mode render missed, the mount returned early, and nothing retried — so `items` assigned after mount (React/Vue prop update, `el.items = …`, a live reload) left the suggestion list permanently empty. The playground masked it because an unrelated render happened to follow (EOA-19597 T30).

**Pattern for any parent mounting work into a child's internal DOM:**

1. Keep an exactly-once flag (`virtualWindowMounted`); the mounted utility's own `mount()` should also no-op on a second call.
2. On a miss, schedule **one** `requestAnimationFrame` retry, guarded by the pending handle so repeated `componentDidRender` calls do not stack.
3. Cap the chain with a named frame budget (`ITEMS_MODE_MOUNT_MAX_FRAMES = 120` in `bds-search-bar/utils/constants.ts`); on success `cancelAnimationFrame` and reset the budget.
4. Cancel and reset from the disposal path — both `disconnectedCallback` and "the data prop became `undefined`" funnel there. Never leave a scheduled frame alive past disconnect.
5. Bump any `@State` version from a microtask after the mount, not synchronously inside `componentDidRender`.

**Testability.** mock-doc implements `requestAnimationFrame` as `setTimeout(…, 0)` and `cancelAnimationFrame` as `clearTimeout`, so the retry is deterministic with a settle helper (`settleFrames()` in `bds-search-bar/__test__/search-bar-items.test-utils.ts`) or `setupAnimationFrameMocks()`. `jest.spyOn(VirtualWindow.prototype, 'mount')` proves exactly one mount for items-before-mount and items-after-mount, and zero after `items = undefined` or `remove()`.

**Not the same as slot-relocation timing.** `stencil-non-shadow-slot-relocation-timing.md` covers content relocated *before* the first render completes; this entry covers a child's own internals appearing *after* the parent's render.

**Source:** EOA-19597 T30, reproduced under `newSpecPage` and in Chrome/WebKit.
