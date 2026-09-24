---
name: bds-date-picker-task39-banner-summary-wrapper-parity
description: EOA-17662 Task 39 — Phase 7 banner + footer range-summary verified identical across raw web components, React, and Vue, plus WebKit. Zero wrapper divergence. Documents two behaviors that look like bugs but are universal shipped behavior, and the footer's inclusive-day-count semantics.
metadata:
  type: project
---

EOA-17662 Task 39 (React/Vue wrapper parity for Phase 7's info banner + footer range summary)
verified via the pack-based pipeline (`dev:pack:react`, then `dev:pack:vue`, run serially per
[[dev-pack-react-vue-serial-not-parallel]]). Scenarios `task39-s1-default-banner` ..
`s4-expanded-range-time-banner` already existed in `examples/react-testapp/src/App.tsx` and
`examples/vue-testapp/src/App.vue`; the raw baseline came from
`packages/boreal-web-components/src/index.html`'s `dp-banner-s1..s4` (identical configs and
identical banner content).

**Result: all 4 scenarios pass in React and Vue, byte-identical to each other and to the raw
web-component baseline.** No wrapper-specific divergence found. Verified in Chromium (React +
Vue) and WebKit (Vue surface — same component bundle).

## Two behaviors that look like wrapper bugs but are universal

1. **Clicking the banner's close ("X") also closes the whole popover** (`aria-hidden` flips to
   `true`), not just the banner. `handleBannerClose` only sets `bannerDismissed = true`, so the
   popover close comes from `bds-popover`'s `handleFocusOutside` path (focus falls to `body`
   when the close button is removed from the DOM). **Reproduces identically in the raw web
   component**, so it is shipped behavior, not a wrapper artifact — and re-opening via the
   trigger still re-shows the banner (dismissal is draft-scoped). Task 35's memory said
   "closing/reopening the popover (Escape then re-click trigger)", which is consistent with the
   popover already being closed — it was not evidence the popover stayed open.
2. **The visible banner box is 16px wider on each side than the day grid** (banner 280px vs grid
   248px in a 296px popover). Cause: `.bds-date-picker__banner` uses `padding: padding-xs`
   (8px) while `.bds-date-picker__calendars` uses `padding: padding-s padding-l` (24px), and
   both wrappers are full-width. **Identical in raw/React/Vue.** Task 35's "banner and
   calendar-grid share identical left/right edges" was measuring the full-width banner *wrapper*
   vs. the calendars *container* (both = popover width), not the inner `bds-banner` vs. the inner
   `bds-calendar-grid`. Don't re-report this as a regression.

## Footer range-summary semantics (settles an ambiguity in Task 35's memory)

`resolveDurationRangeEndIso()` adds **+1 day to the end date when `!effectiveWithTime`** (i.e.
`basic` + range), so the summary shows an *inclusive* calendar-day count there; with `withTime`
it is raw elapsed time. Measured: `basic`, Sep 1 → Sep 5 (both 00:00) = **"Range: 5 days"** (not
4). `expanded` + `withTime`, Sep 1 09:00 → Sep 5 17:30 = "4 days, 8 hours, 30 minutes". Singular
forms confirmed at the 1/1/1 boundary: Sep 1 00:00 → Sep 2 01:01 = "1 day, 1 hour, 1 minute".
Both wrappers and the raw component produce identical strings. Task 35's "Sept 1 → Sept 18 = 17
days" must have been a with-time case; do not treat the inclusive count as a bug.

## Operational notes for this playground

- **Resize the viewport before touching the footer.** The picker popover is ~890px tall, so at
  the default 720px viewport the Apply button is below the fold and Playwright loops on
  "element is outside of the viewport - retrying click action" forever (the popover is fixed-
  positioned, so page scroll does not help). `playwright-cli -s=<name> resize 1440 1300` first.
- **`bds-popover`'s floating panel class is `.popover`, not `.bds-popover__container`.**
- **playwright-cli refs are per-snapshot.** Taking any newer snapshot invalidates refs from an
  earlier one, so extract the refs you need from the *same* snapshot invocation you then click
  from (`snapshot > /tmp/x.yml`, then `grep -oE 'ref=e[0-9]+'` into shell vars).
- Vue/React field input ids (`bds-text-field-XXXX`) are regenerated per page load — re-query
  `bds-date-picker[name=...] bds-text-field[slot=field] input` each session.
- The time-select technique from [[bds-date-picker-task35-banner-footer-summary]] (find the one
  visible `bds-list-menu[slot=list]` by `getBoundingClientRect().width > 0`, then scope the
  option click to that listbox's id) worked unchanged for both wrappers and WebKit.
- `.bds-banner__close-icon` is a native `<button>` in the light DOM, so a real Playwright click
  works (unlike `bds-button`, see [[qa-subagent-synthetic-click-vs-real-click]]).
- Both wrappers: `banner` arrives as a JS property and `hasAttribute('banner') === false`, as
  the dispatch predicted. 0 error-level console entries in either wrapper; the only error was
  the pre-existing `favicon.ico` 404 on React. Both wrappers showed the same 37 pre-existing
  `bds-button` warnings (icon-only / no-accessible-name) at page load and after every
  interaction — no new warnings from Phase 7.

## WebKit / Safari check

Mandatory for this component (flexbox layout, slotted content, FACE, native inputs, CSS
transitions). The banner's `width: 0; min-width: 100%` flexbox trick is the highest-risk item and
resolves **identically in WebKit** (wrapper computed width 296px, `min-width: 100%`, same
`getBoundingClientRect()` offsets as Chromium). Banner layout, close/reopen, presets-sidebar
geometry, and both summary formats all matched Chromium exactly; 0 console errors.

See [[kill-sandbox-boundary-for-background-tasks]] for the `lsof -ti:<port>` client-kill hazard
hit while tearing the baseline server down.
