---
name: bds-date-picker-presets-figma-token-mapping
description: EOA-17662 Task 31 — Figma-to-token mapping for bds-date-picker's presets sidebar button (_DatePickerRange, fileKey rtiE5zGA4aoOuxIQMgfD6h, node 14:23420), and the mixin/token discovery technique used to find it
metadata:
  type: project
---

Full 10-variant pull of `_DatePickerRange` (State × Selected) resolved to these exact `$boreal-*` tokens — do not re-derive from scratch if this component is touched again:

- Default/Selected=False: transparent bg (container already white), `$boreal-text-default`, no shadow.
- Default/Selected=True: `$boreal-ui-primary-base` bg, `$boreal-text-inverse` text, **regular** font-weight (not semibold — the pre-Task-31 baseline wrongly used semibold).
- Hover (either Selected): bg → `$boreal-ui-default-lighter` (False) / `$boreal-ui-primary-dark` (True), `box-shadow: $boreal-depth-box-shadow-xs` (via `bds-hover-shadow` mixin in `_interactions.scss`).
- Focus (either Selected): **visually identical to Hover for Selected=False** (same bg + shadow-xs — confirmed via two independent pulls, not a fetch artifact). For **Selected=True, Focus does NOT get the Hover background change** — it stays at Default's `primary-base` bg, only adding `box-shadow-xs`. This is the exact "non-additive" case the task's acceptance criteria warned about.
- Active (either Selected): same bg as Hover, but shadow swaps to `box-shadow: $boreal-depth-box-shadow-inset` (an inset-only shadow token, `inset 0 1px 2px rgba(black,.15)`) — **not** the `bds-focus-ring-active` mixin (`$boreal-depth-box-shadow-active`), which bundles a visible white+blue ring the Figma pull does not show for this component. Using the ring mixin here would be visually wrong despite it being the common convention in sibling list-item components (`bds-tree-menu-item`, `bds-list-menu-item`).
- Disabled/False: `$boreal-ui-disabled` bg, `$boreal-text-disabled` text.
- Disabled/True: `$boreal-ui-primary-light` bg, `$boreal-text-inverse` text (stays inverse-white text even disabled+selected).

Font size is `$boreal-typography-font-size-xs` (12px) — the Task 30 baseline used `-sm` (14px), wrong.

Sidebar container (`Ranges` node `158:175505`, pulled directly despite being a hidden layer in its default-variant ancestor — `get_design_context` on a hidden node's own id still renders it): `padding: $boreal-spatial-padding-xs` (8px all sides), **zero gap** between the 7 stacked preset buttons (no Tailwind `gap-*` class present — the Task 30 baseline's `$boreal-spatial-gap-3xs` was wrong), `background-color: $boreal-ui-inverse`, right-edge 1px hairline via `box-shadow: inset -1px 0 0 0 $boreal-stroke-default-light` (exact token-name match to Figma's `stroke/default-light` variable).

Sidebar/calendar height alignment: pulled from the shared `Body` frame (`158:175504`, not a calendarType-specific frame — Basic and Expanded reuse the same `Body` component, toggling which calendar/time-picker children are hidden). `Body` itself is `flex items-start` (not stretched); only the `Ranges` sidebar carries an explicit `self-stretch` class, so it fills the row's height via `align-self: stretch` even though its own button-stack content is shorter — background/border extend the full height, buttons stay top-anchored. Implemented as `align-self: stretch` on `.bds-date-picker__presets`, with `.bds-date-picker__body` keeping its existing `align-items: flex-start`. Confirmed this same rule covers both `basic` (single calendar) and `expanded` (dual calendar) since it's the one shared component — no separate per-layout research needed once this was found.

Sidebar/button width (128px button, 144px container) is a Figma auto-layout "hug" result for the English label set, not a design token — deliberately NOT hardcoded as a fixed pixel width; kept the pre-existing `width: 100%` inside a naturally-sized flex column instead, which reproduces the same visual proportions without a magic-number violation of the token-only rule.

Discovery technique for shadow/ring token mapping: `packages/boreal-web-components/src/styles/_interactions.scss` defines `bds-hover-shadow` (`box-shadow-xs`), `bds-focus-ring` (`box-shadow-focus`, a real ring), and `bds-focus-ring-active` (`box-shadow-active`, ring+inset combined) — grep sibling components' `.scss` for `box-shadow:` usage to find which raw token a given mixin wraps, then diff that against the Figma pull's literal Tailwind `shadow-[...]` class before picking a mixin, since two mixins can look similarly named but wrap visually different tokens (`bds-focus-ring-active` is NOT the same visual as this component's Active state).

See also [[stencil-light-dom-unscoped-selector-leak]] for the selector-nesting self-check this task's SCSS was verified against.
