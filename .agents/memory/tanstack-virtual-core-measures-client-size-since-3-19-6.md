# `@tanstack/virtual-core` 3.19.6+ measures the scroll element with `clientHeight`/`clientWidth`

Verified on `@tanstack/virtual-core` 3.19.11 (EOA-20193, 2026-11-13).

## The Problem

From 3.19.6 the virtualizer reads the scroll element with `clientWidth` and `clientHeight` and observes it with a ResizeObserver `content-box` (3.19.5 and earlier read `offsetWidth`/`offsetHeight` with `border-box`). If the mock-doc layout mock defines only `offset*`, the viewport size is `NaN` and the window collapses to its overscan: 11 rows instead of 13 and a top spacer of 13832px instead of 0px.

## The Fix

`src/utils/testing/mocks/layout.ts` (`setupElementLayoutMock`) must define `clientHeight` and `clientWidth` as well as `offsetHeight`/`offsetWidth` and a fixed `getBoundingClientRect()`. Keep all of them when changing the mock.

## How to verify

Run the `bds-search-bar` items-mode and `bds-table` virtual specs; the first render must mount a non-empty window. Ad-hoc spec checklist: `.claude/agent-memory/frontend-subagent/stencil-virtual-window-adhoc-spec-verification.md`.

## Real-browser check (3.19.11)

Verified in Chromium and WebKit: windowing, scroll, keyboard, resize and filtering of a 1,000-item search bar and a 5,000-row virtualized table. Three pre-existing `bds-table` virtualization quirks, identical on 3.17.1, were found and drafted as tickets, not fixed: Tab focus loss at the window shift; End/Home stopping short because the row estimate is 48px against 55px real; a small `scrollTop` drift.

Related: [[stencil-windowed-list-data-ownership]], [[stencil-windowed-list-keyed-diff-focus]], [[playwright-webkit-is-not-safari]].
