# `newSpecPage(...).root` Is the First *Registered Component* Element, Not the First DOM Element

## The Fact

`newSpecPage({ components: [...] })` computes `page.root` with `findRootComponent(cmpTags, page.body)`. That helper (verified in the installed `@stencil/core/testing` source) scans the fixture's element tree and returns the **first element whose tag name is one of the `components` passed to `newSpecPage`**. Only when no such element exists does it fall back to `page.body.firstElementChild`.

`page.rootInstance` is then derived from `getHostRef(page.root)` — the instance of *that* component.

Consequence: when the fixture's first DOM element is **not** a registered component (e.g. `<div><button id="trigger">…</button><bds-popover>…</bds-popover></div>`), `page.root` is the `<bds-popover>`, not the wrapping `<div>`. Code that treats `page.root` as the fixture's outer wrapper, or that assumes `rootInstance` is "the component I listed first in the HTML", silently gets a different element — or `null` from `rootInstance` when the fallback element carries no host ref. There is no error; the assertion just runs against the wrong object.

## Practical Use

Rely on `page.root` / `page.rootInstance` when the fixture contains exactly one registered component, regardless of how it is wrapped — this is how `bds-popover-basics.spec.ts`'s `bds-popover positioning` block reaches the `BdsPopover` instance from a `<button>…<bds-popover>` fixture, and why `page.root as HTMLBdsPopoverElement` returns the popover, not the leading `<button>`. When a fixture mixes two registered components, identify the intended one explicitly with `querySelector` rather than assuming `root`.

## Source

Verified against the installed `@stencil/core/testing` spec-page implementation (`findRootComponent`, and the `root` / `rootInstance` getters) while auditing `bds-popover` specs, 2026-09-28.
