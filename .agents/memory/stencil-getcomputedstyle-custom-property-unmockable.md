# `getComputedStyle()` calls cannot be mocked from a Jest spec in Stencil's `newSpecPage`

A component under `newSpecPage()` (Stencil's `@stencil/core/testing` Jest preset) that calls a bare `getComputedStyle(this.el)` cannot have that call intercepted or made to reflect a CSS custom property override from a spec file — neither via `jest.spyOn(window, 'getComputedStyle')` nor by setting the property inline via `el.style.setProperty(...)`.

**Root cause, confirmed by reading `@stencil/core/mock-doc` source and a controlled reproduction:**

1. Stencil's Jest setup (`jest-setuptestframework.js`'s `setupGlobal(global)`, run once before any test) does `global.getComputedStyle = win.getComputedStyle.bind(win)` — a pre-bound copy of `MockWindow.prototype.getComputedStyle`. The bare `getComputedStyle` identifier a component references resolves to this pre-bound global, **not** to `window.getComputedStyle`. Verified directly: `getComputedStyle !== window.getComputedStyle` is `true` — they are different function references once bound.
2. Because `.bind()` captures the original method before any spec file runs, `jest.spyOn(window, 'getComputedStyle')` only replaces the `window.getComputedStyle` property — it has zero effect on the already-bound `global.getComputedStyle` the component actually calls.
3. Independent of (1)/(2), `MockWindow.prototype.getComputedStyle(_)` ignores its argument entirely and returns a static stub whose `getPropertyValue()` always returns `''` — it never reads the element's inline style, computed cascade, or any custom property. Even a correctly-targeted spy would still need to fully replace the return value; nothing in mock-doc reads real CSS.

Verified interactively: `getComputedStyle(elWithInlineCustomProp).getPropertyValue('--foo')` returns `''` both before and after `jest.spyOn(window, 'getComputedStyle')`, while `window.getComputedStyle(...)` reflects the spy — proving the two are disconnected. (A direct `npx jest` run without Stencil's own preset doesn't even have `document`/`getComputedStyle` globals at all — reproduce this only via `stencil test --spec`/`npm test`, which load `@stencil/core/testing`'s preset.)

**How to apply**: do not attempt to unit-test "a CSS custom property override changes JS behavior" via `newSpecPage` — there is no way to intercept the component's `getComputedStyle` call from a spec file, and mock-doc's own implementation can't reflect inline/cascaded styles even if it could be spied on. Only assert the TS-constant-fallback code path (i.e. what happens when the custom property is absent/unparseable, which is exactly the real behavior in this test environment). Route actual CSS-custom-property-override verification to Storybook/manual/visual testing, and state this gap explicitly in the task report rather than silently omitting that coverage.

Found while implementing `bds-table`'s dynamic column minimum-width calculation (`getMinColumnWidth()`), which reads `--bds-table-decorator-width` / `--bds-table-resize-handle-width` / `--bds-table-label-min-width` custom properties with TS-constant fallbacks.

**Source**: EOA-16000 `bds-table` v4 dynamic column min-width feature. Promoted from per-scope memory at `.claude/agent-memory/testing-subagent/stencil-getcomputedstyle-custom-property-unmockable.md` (original left unmodified).
