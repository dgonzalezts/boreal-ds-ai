---
name: feedback_light_dom_selector
description: Plan specs that say :host { display: block } are wrong for Boreal DS — use direct tag selectors in light DOM components
metadata:
  type: feedback
---

Plan acceptance criteria sometimes specify `:host { display: block; }` for SCSS. This is incorrect for Boreal DS.

**Why:** `:host` requires a shadow DOM boundary and has no effect in light DOM per MDN. All Boreal DS components use light DOM. The correct selector is the component's own tag name: `bds-table { display: block; }`.

**How to apply:** When writing or reviewing SCSS for any Boreal DS component, always use the direct tag selector (e.g. `bds-table { ... }`) as the root selector, never `:host`. If a plan spec says `:host`, implement with the tag selector and note the divergence in the review.
