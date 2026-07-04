---
name: stencil-registered-child-prop-lifecycle
description: Confirms a JSX prop set on a registered child custom element actually drives that child's own componentDidLoad logic in newSpecPage, not just DOM presence.
metadata:
  type: project
---

When a parent component's `render()` passes a prop via JSX to a child custom element that is registered in the same `newSpecPage({ components: [...] })` call, Stencil sets the prop as a JS property on the element **before** the child connects — so the child's own lifecycle (`componentWillLoad`/`componentDidLoad`) runs with the correct value, exactly as in a real browser. This is a stronger guarantee than `getAttribute`-based checks (see the now-removed `stencil-child-component-props-in-tests.md`, which only warned that non-reflected props are invisible to `getAttribute`) — the underlying instance property and any `@Watch`/lifecycle logic driven by it does execute correctly.

Verified case: `bds-search-bar`'s `render()` passes `loading={this.canShowLoader}` to a registered `<bds-select>`. `BdsSelect.componentDidLoad()` calls `injectSuffix()`, which reads `this.loading` to set `spinnerEl.hidden = !this.loading` at creation time (`bds-select.tsx:509-514`). A spec asserting `page.root.querySelector('.bds-select__spinner').hidden === false` when the parent renders with `loading` truthy passes — confirming the prop genuinely reached the child's real render/lifecycle path, not just a JS property sitting unused on the element.

**How to apply:** when a fix delegates behavior to a child component (e.g. "let the child render its own spinner instead of duplicating it"), you can trust a `newSpecPage` assertion on the child's *rendered DOM output* (not just prop echoing) as real proof the delegation works — no need to mock or stub the child's internals, as long as the child class is registered in `components`.
