---
name: feedback_prop_or_slot_pattern
description: Use {prop.length > 0 ? <el>{prop}</el> : <slot />} to avoid <slot-fb> DOM noise in Stencil light DOM — never put fallback children inside <slot> tags
metadata:
  type: feedback
---

In Stencil light DOM (no shadow DOM), never put fallback content inside a `<slot>` tag:

❌ `<slot name="x"><SomeFallback /></slot>` — Stencil injects `<slot-fb name="x" hidden>` into the real DOM even when the slot is filled, creating visible DOM noise.

✅ Use a string prop as the default and the slot only for rich override content:
`{this.myProp.length > 0 ? <span>{this.myProp}</span> : <slot name="x" />}`

**Why:** The `<slot-fb>` polyfill element is always rendered by Stencil's light DOM slot system; the `hidden` attribute only hides it visually. This is an implementation artifact that pollutes DevTools and the accessibility tree.

**How to apply:** For any component that needs slot fallback text, add a string `@Prop()` with a sensible default. The slot remains available for consumers who need richer content (illustrations, CTAs). Consumers activate the slot by setting the prop to an empty string. Use `prop.length > 0` (not `!!prop` or `prop`) to satisfy the `stencil/strict-boolean-conditions` ESLint rule.

**Also:** Never use `<bds-typography>` inside slot fallback content — it applies its own SCSS cascade that overrides component token styles. Use plain `<span>` or `<p>` elements styled with `$boreal-*` tokens directly.

**Examples in codebase:** `bds-radio`, `bds-radio-button`, `bds-radio-card`, `bds-checkbox-button`, `bds-checkbox-card`, `bds-table` (empty state).

[[feedback_light_dom_selector]]
