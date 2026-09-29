# `newSpecPage().root` is the first element matching a registered component tag

## The behavior

`SpecPage.root` is **not** `document.body.firstElementChild`. It is the first element in the parsed `html` whose `tagName` matches one of the classes passed in `components` (the first registered custom element in document order). `page.rootInstance` is that element's component instance — and only that one.

Consequences:

- `<div><bds-button>Trigger <bds-popover>…</bds-popover></bds-button></div>` with `components: [BdsPopover, BdsButton]` → `page.root` is the **`bds-button`** (it appears first in document order), so `page.rootInstance` is `BdsButton`. `root.querySelector('bds-popover')` finds the popover.
- `<div id="wrapper"><input/><bds-popover …>` → since `<input>` is a native element, `page.root` is the **`bds-popover`** itself, so `root.querySelector('bds-popover')` returns `null` (can't query self). Use `page.doc.querySelector('bds-popover')`.
- `<div><bds-popover>…</bds-popover><button>…</button></div>` → `page.root` is the **`bds-popover`** (only registered custom element; native `<button>` never counts).

## How to apply

To reach a **non-root** component's instance (needed for the internals-testing pattern — spying private methods, setting private fields), restructure the fixture so the target component is the first registered custom element in document order. Otherwise `page.rootInstance` is some other component.

To query a component/child by tag, prefer `page.doc.querySelector(...)` over `page.root.querySelector(...)` — it is always correct regardless of which component ends up as `root`.

Found writing `bds-popover` focus-restoration specs (2026-09-28).
