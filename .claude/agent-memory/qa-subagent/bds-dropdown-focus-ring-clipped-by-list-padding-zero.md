---
name: bds-dropdown-focus-ring-clipped-by-list-padding-zero
description: EOA-18739 investigation (2026-11-19) - list-menu item focus ring is clipped on left/right/outer edges inside bds-dropdown; cause is --bds-list-menu-padding:0 plus overflow on .bds-list-menu__content; bds-select unaffected
metadata:
  type: project
---

The ring on `bds-list-menu-item` is `box-shadow: 0 0 0 1px white, 0 0 0 3px var(--boreal-focus)` (outside the box), so it needs padding room inside `.bds-list-menu__content` (`overflow-y:auto` makes overflow-x compute to `auto`, which clips). `bds-dropdown.scss` sets `--bds-list-menu-padding: 0` (commit f6a77c64, EOA-19856) so items are flush; ring shows as two stray blue bars (top/bottom between rows), none left/right, first-item top and last-item bottom fully clipped. Identical on Chromium, WebKit, Firefox. `bds-select` (padding 4px) shows a full ring. Not text-editor specific; hits every `bds-dropdown` (selectable, multiselect, menu).

**Why:** user reported "focus ring not as expected for list menu items" and blamed bds-dropdown.tsx; the TSX/keyboard logic is fine, the defect is SCSS.

**How to apply:** diagnostic that proves it without editing source: inject `.bds-list-menu__content{overflow:visible !important}` (full ring appears, overhanging popover edge) or set `--bds-list-menu-padding:8px` on the dropdown host (full ring). `active-item` has no CSS, only `:focus`/`:active` draw the ring. Playwright WebKit: a mouse click does not focus `bds-button`, so ArrowDown from the trigger needs programmatic `.focus()` then a real key press. macOS `sed -i` needs `-i ''`; use python for in-place edits. Screenshots from `run-code` ignore CDP DSF override; upscale with PIL NEAREST instead.
