---
name: stencil-parent-componentdidrender-child-internals-missing
description: A parent's componentDidRender runs before lazy child components have rendered their internal DOM, so mount work keyed on a child's internal selector must retry on a bounded rAF loop rather than assume it runs once
metadata:
  type: project
---

Found in EOA-19597 T30 (`bds-search-bar` `items` mode), reproduced under `newSpecPage` as well as in the browser.

**Symptom:** the windowed suggestions list stayed permanently empty when the `items` prop was assigned after mount (React/Vue prop update, `el.items = …` from the console, or any later render). The playground masked it because its own renders happened to retry.

**Root cause:** `bds-search-bar` creates its `VirtualWindow` in `componentWillRender` but mounts it from `componentDidRender`, gated on `this.el.querySelector('.bds-search-bar__list .bds-list-menu__content')`. On the render that first introduces the list, that element does not exist yet: `bds-select` → `bds-popover` → `bds-list-menu` are separate (lazy) components and their internal render happens *after* the parent's `componentDidRender`. `mountVirtualWindow()` returned early, and nothing retried until an unrelated render — which never came. Same shape in `newSpecPage`: the child's render is flushed by `waitForChanges()` after the parent already ran `componentDidRender`.

**Fix pattern (any parent mounting work into a child's internal DOM):**

- Keep the `virtualWindowMounted` boolean as the exactly-once guard; `VirtualWindow.mount()` itself also no-ops on a second call.
- When the selector misses, schedule **one** `requestAnimationFrame` retry (guard on an already-pending handle so repeated `componentDidRender` calls don't stack), and cap the retry chain with a frame budget constant (`ITEMS_MODE_MOUNT_MAX_FRAMES = 120` in `bds-search-bar/utils/constants.ts`; 40 was the existing `ITEMS_NAV_MAX_FRAMES` precedent but is marginal for a lazy-chunk fetch on a slow network).
- On success: `cancelAnimationFrame` the pending handle, reset the budget, mount, then bump the version state in a microtask so the first windowed render happens.
- Cancel and reset the budget from `disposeVirtualWindow()` — that covers both `disconnectedCallback` and "`items` became `undefined`", since both funnel through it. Never leave a scheduled frame alive past disconnect.
- There is no SSR/hydrate output target in this repo, so a bare `requestAnimationFrame` is safe; mock-doc implements `requestAnimationFrame` as `setTimeout(…, 0)` and `cancelAnimationFrame` as `clearTimeout`, so the retry is testable with the existing `settleFrames()` helper in `bds-search-bar/__test__/search-bar-items.test-utils.ts` (or `setupAnimationFrameMocks()`).

**Verification technique:** `jest.spyOn(VirtualWindow.prototype, 'mount')` counts mounts — assert one mount for items-before-mount, items-after-mount, and after `settleFrames()` beyond the retry budget, and zero after `items = undefined` or `root.remove()` while a retry is pending.
