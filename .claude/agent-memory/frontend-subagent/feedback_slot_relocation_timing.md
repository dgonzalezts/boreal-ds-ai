---
name: feedback_slot_relocation_timing
description: Non-shadow slot polyfill relocates light-DOM children before componentDidLoad — inspect this.el children in componentWillLoad instead
metadata:
  type: feedback
---

Stencil's non-shadow (`shadow` omitted) slot polyfill physically relocates default-slot light-DOM
children into their rendered position during the *first render*, which completes before
`componentDidLoad` fires. Any private method that inspects `this.el`'s direct `childNodes` (e.g.
`hasSlotContent(this.el)`) must be called from `componentWillLoad()`, not `componentDidLoad()` —
otherwise slotted text/content has already moved and the check always sees an empty host.

**Why:** found in `bds-button`'s `checkAccessibleName()` (EOA a11y docs task). Calling it from
`componentDidLoad()` produced a false-positive "No accessible name found" warning on valid
text-only buttons (`<bds-button>Delete item</bds-button>`), because by the time `componentDidLoad`
ran, the slotted text had already been relocated inside `.bds-button__content-text` and was no
longer a direct child of `this.el`.

**How to apply:** for any non-shadow-DOM component whose lifecycle logic needs to read light-DOM
children as they existed in the original markup (accessible-name checks, slot-presence checks,
prop validation derived from slotted content), call that logic from `componentWillLoad()`.
`componentDidLoad()` is only safe for logic that operates on the *rendered* DOM (post-relocation),
such as `querySelector` calls that don't care whether the match is a direct child — `querySelector`
searches the whole subtree, so attribute-selector lookups like `this.el.querySelector('[slot="icon"]')`
work correctly in either lifecycle hook, since relocation stays within the host's own subtree.

See also [[feedback_no_shadow_false]].
