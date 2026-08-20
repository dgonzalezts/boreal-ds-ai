---
name: bds-popover-data-hidearrow-attribute-inverted-name
description: bds-popover's rendered data-hidearrow attribute is bound to canShowArrow (the inverse), so its name is misleading — do not use attribute presence as a proxy for "arrow is hidden" in QA or debugging
metadata:
  type: project
---

Found during EOA-16692 `bds-date-picker` Task 19 QA (2026-08-19), while verifying `#date-picker-hide-arrow`.

`bds-popover.tsx` line ~635 renders `data-hidearrow={this.canShowArrow}`, where `canShowArrow` is `!this.floatingOptions.hideArrow` (line ~547). Since Stencil JSX renders a `true` boolean prop as an empty-string attribute and `false` as attribute-absent ([[stencil-jsx-boolean-aria-attr-empty-string]] applies to plain `data-*` attrs too), the attribute is backwards from its name: `data-hidearrow=""` is present when the arrow IS shown, and absent when the arrow IS hidden.

The actual arrow `<div class="popover-arrow">` element itself is gated correctly on `{this.canShowArrow && (...)}` (line ~661) — so the real visible/functional behavior (arrow renders or not) is correct in both the default and `hide-arrow="true"` `bds-date-picker` scenarios; only the diagnostic/CSS-hook attribute name is misleading.

**Why:** naming a `data-*` attribute after one concept (`hidearrow`) while binding it to the logically inverted value (`canShowArrow`) is a latent trap for anyone using it as a debugging/CSS hook or writing a Playwright/CSS selector against it.

**How to apply:** when verifying arrow visibility in `bds-popover` or any composing component (`bds-date-picker`, `bds-select`, `bds-dropdown`, `bds-search-bar`), check for the actual `.popover-arrow` DOM element (or its computed `display`), never the `data-hidearrow` attribute's presence — it means the opposite of what its name suggests. Worth a small fix (rename to `data-showarrow` or invert the bound value) but out of scope for a QA pass; flag to the component owner if seen again.
