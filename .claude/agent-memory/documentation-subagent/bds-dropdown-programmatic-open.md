---
name: bds-dropdown-programmatic-open
description: Synthetic .click() on a bds-button doesn't open a bds-dropdown (event.detail===0 guard) — call the child bds-popover's openPopover() method directly instead, queried lazily.
metadata:
  type: project
---

To open a `bds-dropdown` in response to an event from a different, unrelated element (e.g. a
`bds-table` toolbar button that isn't inside the dropdown's own `slot="trigger"`), the natural idea
is to give the dropdown a hidden/invisible trigger `bds-button` and call
`trigger.querySelector('button').click()` on it programmatically. **This does not work**:
`bds-button`'s `handleClick` (`bds-button.tsx`) contains `if (event.detail === 0) return;` — a
guard meant to filter out non-pointer synthetic clicks — and a plain DOM `.click()` call dispatches
a `MouseEvent` with `detail: 0`, so `bdsClick` never fires and the dropdown's internal
`forcePopoverOpen` listener never runs.

**How to apply:** query the dropdown's own `bds-popover` child (`dropdown.querySelector('bds-popover')`)
and call its public `openPopover()` method directly — `bds-dropdown` renders with
`<bds-popover managed={true}>`, and its own JSDoc states "the consumer is responsible for calling
openPopover/closePopover manually" in managed mode, so this is the supported path, not a workaround.
Must be queried lazily (inside the event handler), not once at page-load time — Stencil custom
elements upgrade asynchronously, so `bds-popover` may not exist as a DOM child yet when a `<script>`
block runs synchronously after page load.

Used in the `WithColumnVisibilityDropdown` story (`bds-table.stories.ts`, EOA-16000 Task 13) to open
a `bds-dropdown` anchored to `bds-table`'s internal (non-slotted) Column-visibility toolbar button by
positioning the dropdown host (`position: fixed`) at that button's `getBoundingClientRect()` before
calling `openPopover()`.
