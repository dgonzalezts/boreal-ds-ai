---
name: mock-doc-generic-boolean-attr-property-undefined
description: a plain <button>/native element's .disabled JS property reads undefined in Stencil's mock-doc even when the disabled attribute is present — assert with hasAttribute, not the IDL property
metadata:
  type: project
---

Stencil's `mock-doc` (`@stencil/core/testing`) does not implement full IDL boolean-attribute reflection for every generic HTML element the way a real browser or full jsdom would. A native `<button disabled>` rendered by a component (e.g. `bds-button`'s inner `<button disabled={this.disabled || this.loading}>`) sets the `disabled` *attribute* correctly, but reading `buttonEl.disabled` as a JS property returns `undefined`, not `true` — there is no generic `MockHTMLElement` IDL-property mapping for `disabled` the way there is for e.g. `MockInputElement`'s specific known properties.

**Why:** found while writing `bds-date-picker.variants.spec.ts`'s "disables all three footer buttons" test — `expect(findFooterButton(...).disabled).toBe(true)` failed with `Received: undefined` even though the button correctly had `disabled=""` as an attribute; switching to `.hasAttribute('disabled')` fixed it immediately.

**How to apply:** for any spec asserting a boolean HTML attribute (disabled, readonly, checked, etc.) on a *native* element queried out of a component's rendered DOM in `newSpecPage`, prefer `el.hasAttribute('disabled')` over `el.disabled`. This is distinct from `mock-doc-mouseevent-relatedtarget`-style event-init issues — it's specifically about reading IDL properties back off already-rendered native elements. Custom Stencil elements (`<bds-button disabled>`) don't have this problem since Stencil generates real getter/setter proxies for their own `@Prop()`s — the gap is only for genuinely native tags (`<button>`, `<input>` not backed by a dedicated Mock*Element subclass with that property implemented). Candidate for promotion to `.agents/memory/` — likely to recur in any spec asserting native-element boolean attributes.
