---
name: bds-banner-close-emits-synchronously
description: "bds-banner's bdsClose event fires synchronously on close-button click, independent of its own closing CSS transition — relevant when testing any component that composes bds-banner."
metadata:
  type: project
---

`bds-banner`'s close (`X`) button click handler (`handleCloseBanner` in `bds-banner.tsx`) sets
`isClosing = true` and calls `this.bdsClose.emit()` synchronously, in the same click handler.
The banner's own `isOpen` state (which actually removes its content from the DOM) only flips to
`false` inside `handleAnimationEnd`, gated on a real `transitionend` DOM event — which never
fires in Stencil's `mock-doc`/jsdom test environment.

**Why it matters:** a parent component that composes `bds-banner` and listens for `bdsClose` to
manage its own dismissed-state (e.g. `bds-date-picker`'s `renderBanner.tsx` / `bannerDismissed`)
does not need to simulate the close animation or wait for any transition event in a unit test —
clicking `.bds-banner__close-icon` and awaiting one `page.waitForChanges()` is sufficient to
observe the parent's reaction. Confirmed while writing `bds-date-picker.banner.spec.ts`
(EOA-17662 Task 37): the parent's own re-render (hiding the banner wrapper entirely) happens
independently of `bds-banner`'s internal `isOpen`/`isClosing` animation state, which stays
unresolved/stuck in the test environment and is irrelevant to the parent's behavior.

**How to apply:** when testing any Boreal DS component that composes `bds-banner` (or a similar
component with a CSS-transition-gated internal close animation), register the child in
`newSpecPage`'s `components` list, click its real close button, and assert on the *parent's*
resulting DOM — do not attempt to assert on the child's own `isOpen`/animation-driven visibility,
which is untestable without a real transition event.
