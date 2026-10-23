---
ticket: —
component: bds-search-bar
status: exploring
---

# Research Spike: Approach A — Keep the positional mechanism, make it honest and cheaper

**Date:** 2026-10-21
**Bug report:** `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md`

---

## Goal

Keep `VirtualScrollController`'s contract (reposition already-mounted light-DOM `bds-list-menu-item` children, `display:none` for out-of-window ones). Fix the misleading wording, shrink the story, check whether Finding 2 (TanStack/virtual#823) can happen, and look for cheap ways to reduce instantiation cost without changing the contract. Then judge how much of the bug this resolves.

---

## Options evaluated

| # | Option | Effort | Verdict |
| - | ------ | ------ | ------- |
| A1 | Reword JSDoc, MDX and story doc to say "positioned, not unmounted" | XS | Do it |
| A2 | Shrink story from 1000 to ~100–200 items | XS | Do it; keep one larger story only if wanted for stress testing |
| A3 | Rename `VirtualScrollController` to `PositionalScrollController` (or similar) | S | Optional; private utility, one consumer |
| A4 | Verify Finding 2 by code reading and a runtime probe | S | Done by reading; the runtime probe is optional |
| A5 | `content-visibility: auto` + `contain-intrinsic-size` on items | S | Paint and layout win only; see below |
| A6 | Consumer-side chunked/idle insertion of items (rAF / `requestIdleCallback`) | M | Spreads the cost; the total is unchanged |
| A7 | Make the controller defer creation | L | Out of scope. This is the Approach B/C rewrite |

### A4 — Finding 2 analysis

- `virtual-scroll.ts` never calls `virtualizer.measureElement`, and it has no `ref`/`data-index` wiring. In `@tanstack/virtual-core@3.17.1`, the per-item `ResizeObserver` is created in the `observer` getter (index.ts ~456) and only ever `.observe()`s nodes passed to `measureElement` (~1440). So no item is observed, and a hidden item can't emit a size-0 entry.
- `observeElementRect` (index.ts ~115) observes only the scroll element, which is never `display:none` while the list is open. `estimateSize` is fixed at 28 and there is no dynamic measuring.
- **#823 does not apply to the current code.** The bug needs measured items hidden with `display:none`. This code has no measurement path.
- Real, different risks in the same code:
  - **Fixed 28px assumption.** Items that wrap, or a changed typography token, will overlap, because every item is `position:absolute` with a fixed offset. This is the actual correctness hazard, not #823.
  - **MutationObserver and `refresh()`.** `refresh()` runs `querySelectorAll` plus a style write for N items on every filter or mutation. That is O(N) per keystroke.
  - **Popup open/close.** The scroll element can be `display:none` while the popup is closed, so `observeElementRect` may report 0 height; check that the first open re-renders correctly.
- A guard against a future `measureElement` adoption: unobserve before hiding (the #531 workaround).
- Reproduction (optional, 30 min): in the story, wrap `window.ResizeObserver` with a logger and scroll. Expect zero item entries.

### A5 — content-visibility

- `content-visibility: auto` on items skips rendering work for off-screen items, but they are already `display:none`, which skips the same work. There is no gain on top of the current mechanism.
- It does not reduce custom-element upgrade cost, which is the dominant cost (Stencil constructor, `connectedCallback`, first `render()` ×1000).
- Applying it to the host `bds-list-menu` would not help either.
- **Drop A5.**

### A6 — chunked insertion

- Only the consumer can do this, in a way the story/Lit template doesn't. That means a new API (data array or async slotting) that the light-DOM children model doesn't have.
- It improves time-to-interactive (no long task) but not total work or DOM count.
- It conflicts with `.agents/memory` light-DOM slot timing: `attach()` runs in `componentDidLoad`, and `bdsListMenuEl` and its children may not exist yet when they are inserted late. The existing MutationObserver does cover late insertions, but filtering and `searcherElement` assume all items are present.
- It is not a clean "within the contract" mitigation. **Defer.**

### Naming and docs touch points

- `bds-search-bar.tsx` lines ~38-40: JSDoc says "(only items near the visible viewport are rendered/positioned)".
- `bds-search-bar.mdx` line 151: says "rendered and positioned — the rest stay in the DOM but hidden".
- `bds-search-bar.stories.ts` ~404-442: doc comment and the "...997 more items..." snippet.
- The `virtual-scroll.ts` class JSDoc is already accurate ("remain in the DOM").
- `VirtualScrollController` is used only by `bds-search-bar` (grep). `bds-select` does not import it, contrary to the bug report's "affects bds-select". Correct the report.
- No spec file exists for the controller.

---

## Findings

1. Finding 2 is **not applicable** to the current code (no `measureElement`, so no per-item `ResizeObserver`). Resolved by analysis; a cheap runtime probe can confirm.
2. The controller is honest in its own JSDoc. Only the consumer docs, MDX and story over-claim.
3. Nothing within the positional contract can reduce DOM count or instantiation cost. `content-visibility` is redundant with `display:none`. Chunked insertion needs API changes.
4. The story's 1000 items is the main driver of the Storybook slowness and deploy timeout (a hypothesis; the Known Gap about CI logs is still open).

---

## Recommendation

Do A1 + A2 (+ A3 if wanted), and record the A4 conclusion in the bug report. Do not pursue A5/A6.

**Files touched**
- `packages/boreal-web-components/src/components/forms/bds-search-bar/bds-search-bar.tsx` (JSDoc only)
- `apps/boreal-docs/src/stories/forms/bds-search-bar/bds-search-bar.mdx` (line ~151)
- `apps/boreal-docs/src/stories/forms/bds-search-bar/bds-search-bar.stories.ts` (comment, count, source snippet)
- Optional A3: `virtual-scroll.ts` (rename) plus its import and usage in `bds-search-bar.tsx`
- Bug report: correct the `bds-select` claim and add the Finding 2 conclusion

**Suggested wording**: "Only items near the viewport are positioned; all items stay mounted in the DOM but hidden. Very large lists (hundreds or more) increase initial render cost."

**Effort**: A1+A2 about 1 hour; A3 about 1–2 hours; optional probe about 30 minutes.
**Risks**: Low. Docs only. A3 has a rename-miss risk, which the compiler catches.
**Breaking changes**: None (the controller is internal, not exported publicly; confirm it is not in `index.ts` exports).
**Test impact**: None for A1/A2. A3 has no specs to update. Chromatic snapshot for `LargeSuggestionsList` changes (fewer items). Optionally add a first spec for the controller (hidden/visible style assertions).

**Verdict on the bug**
- Finding 1 (DOM count): **not fixed**. Only the misleading claim is. This is the report's own "option 1", so it is addressed as intended, not solved.
- Finding 2: **closed as not applicable** (pending an optional probe). It does not require a rewrite.
- Known Gaps: CI timeout log, profiling and real-consumer list sizes remain open. The smaller story makes the timeout likely go away (hypothesis only).
- Overall: roughly 60–70% of the report (all the cheap parts), with 0% of the real windowing goal. It is enough if no consumer passes more than about 300 items; otherwise a windowed-creation approach (the deferred spike) is still needed.

---

## Open questions

- Does any real consumer pass more than a few hundred suggestions? That decides whether Approach A is enough.
- What is the actual Storybook/Chromatic timeout (step and duration)? Does a 100–200 item story fix it?
- Is `VirtualScrollController` exported in the public package barrel? If so, the rename (A3) is breaking.
- Does the first open of the popup (scroll element transiently `display:none`) always compute a non-zero viewport? Needs a manual check.
- Should the 28px fixed estimate be validated against the typography tokens (wrapping items overlap)?
