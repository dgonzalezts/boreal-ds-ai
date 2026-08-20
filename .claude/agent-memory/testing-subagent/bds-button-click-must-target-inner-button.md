---
name: bds-button-click-must-target-inner-button
description: bds-button's own click handler ignores event.detail === 0, so calling .click() on the <bds-button> host element itself never fires bdsClick — click the inner native <button> instead
metadata:
  type: project
---

`BdsButton.handleClick` (`packages/boreal-web-components/src/components/actions/bds-button/bds-button.tsx`) has `if (event.detail === 0) return;` before emitting `bdsClick`. Stencil's `mock-doc` `HTMLElement.prototype.click()` dispatches a `MouseEvent` with `detail: 0` on the element it's called on. So calling `.click()` directly on a `<bds-button>` host element (or any other element whose own click handler has this guard) is silently swallowed — no `bdsClick`, no visible test failure, just nothing happens.

The established, working pattern (confirmed via `bds-button`'s own `__test__/bds-button-events.spec.ts`, and reused in `bds-date-picker`'s `date-picker.test-utils.ts` `findFooterButton` helper) is to query the *inner* native `<button>` rendered inside `bds-button`'s light DOM (`bdsButtonEl.querySelector('button')`) and call `.click()` on that instead — its own click event still reaches the host's `onClick={this.handleClick}` listener via normal DOM bubbling, and inner-button clicks apparently don't carry the same `detail: 0` suppression in mock-doc's dispatch path.

**Why:** discovered while writing `bds-date-picker`'s footer-button interaction tests (Apply/Cancel/Clean) — `.click()` on the `<bds-button>` element produced zero emitted events with no error, which looked like a broken test rather than a wrong click target until cross-checked against `bds-button`'s own spec convention.

**How to apply:** whenever a spec needs to simulate a user click on any `bds-button` instance (standalone or nested inside another component's render, e.g. popover footers, calendar-grid nav), always resolve to `.querySelector('button')` first and click that, never the `<bds-button>` custom element itself. Candidate for promotion to `.agents/memory/` — this affects every component that composes `bds-button` and is tested via `newSpecPage`.
