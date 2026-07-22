---
name: stencil-mockdoc-no-scope-selector
description: "@stencil/core/mock-doc (used by newSpecPage) throws a hard error on the :scope CSS pseudo-class — cannot use `col.querySelector(':scope > [slot=\"x\"]')` in component code covered by unit tests"
metadata:
  type: project
---

`newSpecPage` (from `@stencil/core/testing`) does not render against real jsdom — it uses Stencil's own `@stencil/core/mock-doc` DOM implementation. That implementation's selector engine does not support the `:scope` pseudo-class at all: any `querySelector`/`querySelectorAll` call containing `:scope` throws `Error: At present jQuery does not support the :scope selector` (mock-doc vendors a jQuery-Sizzle-style selector engine).

**Why this matters:** a plan or design doc may specify a selector like `col.querySelector(':scope > [slot="footer"]')` to mean "direct child with this attribute." If implemented literally, every `newSpecPage` test that renders the component throws immediately — not a soft failure, an uncaught exception.

**How to apply:** never use `:scope` in component `.tsx` selector strings. For "direct child matching X" semantics, iterate `element.children` (an `HTMLCollection`, elements only) and test the attribute directly, e.g.:

```ts
Array.from(col.children).find(child => child.getAttribute('slot') === 'footer')
```

This works identically in mock-doc, jsdom, and real browsers, and is what `bds-table`'s slot-based column footer (`hasFooter`/`footerNode`, EOA-15507 Task 3) uses instead of the plan's literal `:scope` wording.

See also [[stencil-node-relocation-breaks-on-rerender]] for a related gotcha discovered in the same feature.
