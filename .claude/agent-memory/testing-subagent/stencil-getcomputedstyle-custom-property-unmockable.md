---
name: stencil-getcomputedstyle-custom-property-unmockable
description: getComputedStyle() calls inside a component under newSpecPage cannot be made to reflect CSS custom property overrides from a Jest spec — mock-doc's own getComputedStyle stub always returns an empty string regardless of the element, and it is bound to a separate global reference from window.getComputedStyle before any test runs, so jest.spyOn(window, 'getComputedStyle') never intercepts it.
metadata:
  type: project
---

Investigated (2026-08-10, `bds-table` `getMinColumnWidth`) after a bare `getComputedStyle(this.el)` call inside the component was changed to read `--bds-table-decorator-width` / `--bds-table-resize-handle-width` / `--bds-table-label-min-width` custom properties, falling back to TS constants. A unit test setting these properties via inline `style` on the `<bds-table>` element, and via `jest.spyOn(window, 'getComputedStyle')`, always saw the TS-fallback value — never the override.

**Root cause, confirmed by reading `@stencil/core/mock-doc` source and a controlled reproduction:**

1. Stencil's Jest `setupGlobal(global)` (called once in `jest-setuptestframework.js`, before any test runs) does `global.getComputedStyle = win.getComputedStyle.bind(win)` — a pre-bound copy of `MockWindow.prototype.getComputedStyle`. The bare `getComputedStyle` identifier a component references (compiled/bundled global scope) resolves to this bound copy, **not** to `window.getComputedStyle`. Reproduced directly: `getComputedStyle !== window.getComputedStyle` returns `false`/`true` — they are different function references once bound.
2. Because `.bind()` captures the original method before any spec file runs, `jest.spyOn(window, 'getComputedStyle')` only replaces the `window.getComputedStyle` property — it has zero effect on the already-bound `global.getComputedStyle` the component actually calls.
3. Independent of (1)/(2), `MockWindow.prototype.getComputedStyle(_)` (in `mock-doc/index.js`) ignores its argument entirely and returns a static stub object whose `getPropertyValue()` always returns `''` — it never reads the element's inline `style`, computed cascade, or any custom property. So even a correctly-targeted spy would still need to fully replace the return value; nothing in mock-doc reads real CSS.

Verified interactively: `getComputedStyle(elWithInlineCustomProp).getPropertyValue('--foo')` returns `''` both before and after `jest.spyOn(window, 'getComputedStyle')`, while `window.getComputedStyle(...)` reflects the spy — proving the two are disconnected. (Direct `npx jest` without Stencil's config doesn't even have `document`/`getComputedStyle` globals at all — must load `@stencil/core/testing`'s jest preset, e.g. via `stencil test --spec`/`npm test`, to reproduce this correctly.)

**How to apply:** Do not attempt to unit-test "a CSS custom property override changes JS behavior" via `newSpecPage` — there is no way to intercept the component's `getComputedStyle` call from a spec file, and mock-doc's own implementation can't reflect inline/cascaded styles even if it could be spied on. Only assert the TS-constant-fallback code path (i.e., what happens when the custom property is absent/unparseable — which is exactly the real behavior in this test environment). Route actual CSS-custom-property-override verification to Storybook/manual/visual testing, and note this gap explicitly in the task report so it doesn't look like an oversight. Related to `stencil-no-scss-assertion-pattern.md` (no CSSOM in `newSpecPage`) but this is a distinct, narrower issue: it is `getComputedStyle()` specifically that is unmockable, not just "CSS isn't loaded."

Candidate for `.agents/memory/` promotion if another component hits the same "assert getComputedStyle-derived CSS override" pattern.
