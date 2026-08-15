---
name: cdp-force-pseudo-state-unreliable
description: CDP CSS.forcePseudoState gave incorrect (transparent) background-color/box-shadow readings for :hover/:focus-visible/:active in bds-calendar-grid QA; real mouse/keyboard interaction is required for reliable computed-style verification
metadata:
  type: project
---

`CSS.forcePseudoState` via a raw CDP session (`page.context().newCDPSession(page)`) technically works (needs `DOM.enable` + `CSS.enable` first) but gave unreliable `background-color`/`box-shadow` reads on `bds-calendar-grid` day cells — showing `rgba(0,0,0,0)`/`none` even though the SCSS clearly sets a fill on hover/focus/active. Real mouse hover (`playwright-cli hover <locator>`) and real programmatic `.focus()` (after a `Tab` keypress to reset Chromium's input-modality heuristic so `:focus-visible` actually matches) gave correct, consistent results every time.

**Why:** Suspected timing/recalc-order issue between forcing the pseudo-class over CDP and Playwright's separate `evaluate` reading computed style in a different protocol round-trip — the two don't share a rendering-frame boundary the way a live cascade + `getComputedStyle` immediately after a real DOM event does. Not confirmed as a documented CDP limitation, just empirically unreliable here.

**How to apply:** For any future manual-state verification (hover/focus/active) on Boreal DS components, prefer real interaction: `playwright-cli hover`/`mousedown`+`mouseup` for hover/active, and `document.activeElement`-confirmed real `.focus()` (after a `Tab` press if `:focus-visible` needs to be genuinely true) for focus checks — read computed style in the SAME eval call that triggers the interaction where possible, and re-read once more if the first read looks suspicious (a second `eval` call after a real interaction reliably reflected the correct recalculated style even when the first read right after `.focus()` was still stale). Don't trust `CSS.forcePseudoState` results for background/box-shadow on this codebase without cross-checking against a real interaction.
