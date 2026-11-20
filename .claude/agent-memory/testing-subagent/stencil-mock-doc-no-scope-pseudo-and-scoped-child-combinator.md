---
name: stencil-mock-doc-no-scope-pseudo-and-scoped-child-combinator
description: mock-doc querySelector rejects :scope and cannot match a selector that begins at the element it is called on; direct-child assertions must query from page.body
metadata:
  type: reference
---

In `newSpecPage`, `el.querySelector(':scope > x')` throws "unsupported pseudo: scope" (jQuery/Sizzle under mock-doc).
`root.querySelector('bds-foo > bds-bar')` also returns null when `bds-foo` is `root` itself, because matching is scoped to descendants.

**How to apply:** to assert a direct-child structure, query from `page.body` (`page.body.querySelector('bds-button-group > bds-dropdown > bds-button[slot="trigger"]')`), or compare `Array.from(root.children).map(c => c.tagName.toLowerCase())`.
Found writing `bds-button-group` slot specs (2026-11-19).
