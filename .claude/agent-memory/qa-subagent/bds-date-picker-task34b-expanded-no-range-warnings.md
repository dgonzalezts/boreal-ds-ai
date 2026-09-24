---
name: bds-date-picker-task34b-expanded-no-range-warnings
description: Task 34b manual QA — expanded+range=false dev warnings and duplicate-highlight fix confirmed passing; also documents a style-guidelines dist-missing dev-server failure mode distinct from the known stale-index.html issue.
metadata:
  type: project
---

Task 34b (EOA-17662) manual QA on `dp-expanded-no-range-s1` (`calendar-type="expanded" with-time`, `range` omitted, value Sept 30 — a date that also renders as a leading filler day in October's grid): all three checklist items plus the regression sanity check passed.

- Both new `[bds-date-picker]` warnings (wasted-calendar, time-selector-fallback) fire exactly once each on load, confirmed via `console warning` grep counts.
- Duplicate-highlight fix confirmed via DOM: September's grid shows `bds-calendar-grid__day--selected` on day 30; October's grid (where Sept 30 also appears as a leading filler cell) shows zero selected cells.
- MDX (`bds-date-picker.mdx`) has the dedicated `<Callout variant="warning">` under `## Calendar types` → `### Expanded` covering both warnings, plus the cross-reference line under `## Range selection`'s intro — matches plan spec exactly.
- Regression check on `dp-presets-s4` (`expanded + range + with-time`): neither new warning fired (console warning count unchanged after opening), and range highlighting (`--range-start`/`--in-range`/`--range-end`) worked normally across Sept 5–10 — confirms the fix is scoped strictly to `range=false`.

Unrelated dev-server gotcha hit during this run: **[[stencil-dev-server-index-html-no-rewatch]]** covers stale `index.html`, but this session additionally hit a build FAILURE (`sass error: Can't find stylesheet to import` + `ENOENT ... @telesign/boreal-style-guidelines/dist/...`) on `stencil build --watch --serve` restart — root cause was `packages/boreal-styleguidelines/dist/` missing entirely (not just stale), likely from a concurrent build elsewhere. Fixed by running `pnpm --filter @telesign/boreal-style-guidelines build` directly before retrying the Stencil dev server. If a dev-server restart fails with ENOENT on this package's dist, rebuild it directly rather than assuming the Stencil build itself is broken.

Teardown: stopped the port-3333 dev server at the end of this task since the dispatch gave no lifecycle instruction (default-to-teardown per qa-subagent protocol) — the plan has further tasks (34c, 34d) after 34b, so the next manual-QA dispatch in this plan will need to restart it, budgeting for the style-guidelines rebuild if dist is missing again.
