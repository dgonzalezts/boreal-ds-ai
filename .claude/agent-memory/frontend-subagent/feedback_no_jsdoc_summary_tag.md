---
name: feedback_no_jsdoc_summary_tag
description: Never use @summary in JSDoc — the Stencil CEM compiler ignores it entirely; the leading prose before any @ tags is the sole source of the component description field
metadata:
  type: feedback
---

Never use `@summary` in JSDoc blocks on Stencil components.

**Why:** `@summary` is a valid tag in the CEM analyzer spec (it maps to a `"summary"` field described as "a markdown summary suitable for display in a listing"), but the Stencil CEM compiler does not emit it. Verified against the generated `packages/boreal-web-components/custom-elements.json`: no component entry contains a `"summary"` key, even for components like `bds-banner` that carry `@summary` in source. The `"description"` field in the output is populated exclusively from the leading prose of the JSDoc block — the text before the first `@` tag. Writing `@summary` therefore produces a JSDoc tag that is silently discarded, adding noise without any effect on the manifest. The scope of the problem is wide: as of 2026-06-17 at least 22 component `.tsx` files in the codebase contain `@summary` (grep confirms: `bds-banner`, `bds-tag`, `bds-button`, `bds-dialog`, `bds-tooltip`, and more).

**How to apply:** Place the component description as leading prose in the JSDoc block, before any `@slot`, `@attr`, `@fires`, or other tags. Remove any `@summary` tag and promote its text into the first sentence of the leading prose if it adds information not already present. The leading prose (first paragraph before any `@` tag) becomes `"description"` in the manifest.

**See also:** [[feedback_no_jsdoc_default]] — same class of problem (JSDoc tag that duplicates or conflicts with the authoritative source of truth).
