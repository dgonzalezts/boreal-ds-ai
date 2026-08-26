---
name: stencil-css-custom-property-nested-overlay-leak
description: A direct-child selector scoping fix does not stop CSS custom property inheritance when a nested overlay (e.g. bds-select's popover) lives inside the outer overlay's own DOM subtree (e.g. bds-date-picker's popover content-band slot)
metadata:
  type: project
---

When component A composes component B inside A's own overlay (e.g. `bds-date-picker`'s `bds-popover` rendering a `bds-select` in its content-band slot, and that `bds-select` has its own internal `bds-popover`), scoping A's custom-property-setting rule with a direct-child combinator (`> bds-popover { --x: ... }`) only controls which element the property is SET on — it does NOT stop the property from cascading down via ordinary CSS custom property inheritance to B's nested popover, because B's popover is a DOM descendant of A's popover regardless of selector specificity.

**Why**: CSS custom properties inherit by default down the DOM tree from whatever ancestor last set them, independent of the selector that set it. `bds-date-picker > bds-popover { --popover-content-padding: 12px 24px; }` still leaks into `bds-select`'s nested `bds-popover` because that nested popover is inside the date-picker's own popover's DOM subtree (via the slotted time-selector), not because the original descendant selector `bds-date-picker bds-popover` was too broad in matching — verified via `getComputedStyle` returning the parent's value even after scoping to `>`.

**How to apply**: when a component sets custom properties on its own nested overlay AND that overlay's slot content can itself contain another instance of the same overlay-family component (select-in-date-picker, dropdown-in-drawer, etc.), add an explicit reset (`--x: initial;`) targeting `bds-popover bds-popover` (or the equivalent nested selector) inside the outer rule, so `var(--x, <component-default>)` falls through to the child component's own default instead of inheriting the parent's override. See fix in `bds-date-picker.scss` (Task 4, EOA-17138) — direct-child scoping alone was insufficient; the `initial` reset on the nested selector was the actual fix.

Related: [[component-interface-file-naming]] n/a — this is a CSS/Stencil pattern, not naming.
