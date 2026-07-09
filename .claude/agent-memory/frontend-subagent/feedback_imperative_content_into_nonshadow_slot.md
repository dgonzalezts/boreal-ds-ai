---
name: feedback-imperative-content-into-nonshadow-slot
description: How to imperatively set slotted content on a non-shadow (shadow:false) child custom element without corrupting its own internal render output
metadata:
  type: feedback
---

Never call `el.textContent = ...` directly on the host of a non-shadow (`shadow: false`) custom
element from a parent component, when that child element has its own `render()` output (e.g.
`bds-tooltip`). For non-shadow/light-DOM components, Stencil inserts the component's own rendered
vdom output as real children of the host element itself — there is no separate shadow root. Setting
`.textContent` on the host wipes out ALL of its children, including its own internal rendered markup
(e.g. `bds-tooltip`'s `<div id="tooltip-content">` wrapper), not just the slotted content.

**Why:** Discovered while implementing `bds-table`'s shared overflow tooltip (EOA-14935 Task 14).
The singleton `<bds-tooltip manual>` needed per-hover-target text, which can't be static JSX
children (text varies per event, not per render-state). The tempting shortcut —
`this.overflowTooltipEl.textContent = someText` — would have destroyed the tooltip's own rendered
subtree since `bds-tooltip` is `shadow: false`.

**How to apply:** Render a persistent, ref'd plain element (e.g. `<span ref={el => (this.foo = el)} />`)
as a JSX child of the custom element instead — this becomes the actual light-DOM node that Stencil's
slot-relocation machinery moves into place inside the child's internal slot. Then imperatively set
`.textContent` on *that inner ref'd node*, never on the custom-element host itself. This mirrors the
existing `applyCellFormatter` pattern in `bds-table.tsx` (which also uses `ref` + imperative
`el.textContent =` / `el.appendChild`), but applied one level deeper — on a plain wrapper node inside
the slot, not on the custom element hosting the slot.

Applies to any future singleton/reused instance of a `shadow: false` component (tooltips, popovers,
etc.) whose content must be set imperatively/dynamically from a parent.
