# `bds-table` virtual scroll: what the painted-lag fix covers, and how it was measured

Context: `bds-table` virtual mode showed a blank body band when scrolling faster than the ~550 px
overscan buffer (EOA-19598 T61). The fix fills the uncovered viewport region with skeleton
placeholder rows (`getUncoveredRange` + `renderPlaceholderRows`, spacers shrink by the same height).

## Measured (real Chrome, 400 px viewport, 5 000 rows, 55 px rows, overscan 10)

Per-frame programmatic scroll (`scrollTop += speed` each rAF, sampler reads the DOM each rAF):

| px per frame | before (blank frames / avg blank px) | after     | placeholders render |
| ------------ | ------------------------------------ | --------- | ------------------- |
| 500          | 0 %                                  | 0 %       | never needed        |
| 640          | —                                    | 4 % / 0px | yes                 |
| 800          | 95 % / 147 px                        | 4 % / 8px | yes (23/25 frames)  |
| 1 600        | 71 % / 254 px                        | 72 %      | **never**           |
| 3 200        | 62 % / 220 px                        | 60 %      | **never**           |
| wheel 100/300| 0 %                                  | 0 %       | never needed        |

Why it stops helping above ~800 px/frame: at those rates Chrome stops delivering a scroll event per
frame, so the *render itself* is a whole frame behind — it reads the **old** `scrollTop` as well as
the old window, so the gap math has nothing to detect. No DOM-side gap fill can cover a scroll
position the component cannot observe yet (would need the *next* scroll offset). Single jumps
(scrollbar-thumb granularity) also show no measurable difference before/after: the one blank frame
per jump is the frame painted before any render for that offset exists — inherent, not fixable in
the component.

Do not "fix" this by widening overscan: the rows physically exist only at their windowed content
offsets, so more overscan changes nothing about which content the next scroll frame shows.

## Verification harness (no Playwright config needed)

`playwright-cli` (global, `--browser=chrome`; the bundled `chromium` build is version-mismatched and
refuses to launch) driving a harness page served from a symlinked `www/build` + `www/css`:

- Settle with `scrollTop = X`, 8 × `requestAnimationFrame`, then a short `setTimeout`.
- Meter "blank px" per frame in-page: union the viewport-space intervals of `tbody tr` that are
  `[data-index]` **plus** `.bds-table__row--placeholder`, subtract from `clientHeight - theadHeight`.
- Sample *before* the next jump in the same rAF: that reading is the frame the user would see.
- Chrome headless `--dump-dom --virtual-time-budget` is **not** usable here: virtual time starves
  both rAF and scroll-event delivery (the DOM froze at 19 rows across 9 600 px of scroll).

## Invariants the fix holds (measured)

- `scrollHeight`, mounted data-row count and settled `firstVisibleDataIndex` identical to the
  unfixed build at top / middle / bottom.
- Placeholder rows: `aria-hidden="true"`, no `data-index`, no focusable descendants, `pointer-events:
  none`, `.bds-skeleton { animation: none }`, `td { padding-block: 0; border-bottom: none }` (so the
  inline pixel height is exact — padding/border would otherwise grow the row and change
  `scrollHeight`).
- Pinned placeholder cells carry the same `data-pinned` attrs and inline `left` offset as real cells
  and keep the opaque pinned background.
- Row height comes from the adjacent windowed item's `size`, which is the 48 px *estimate* until that
  row has been measured; placeholder rows then render 48 px instead of 55 px. Harmless (the spacer is
  reduced by exactly what was rendered) but it is why heights are never taken from the stylesheet.
