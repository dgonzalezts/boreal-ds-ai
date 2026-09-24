---
name: bds-date-picker-presets-s1-reopen-custom-mismatch
description: dp-presets-s1 (expanded, range, presets sidebar) manual reopen check — calendar/header/trigger field all correctly reflect the applied "Today" value, but the presets sidebar itself resets to "Custom" selected instead of "Today" on reopen
metadata:
  type: project
---

Exploratory manual QA (EOA-17662, "presets sidebar" section, Scenario 1 / `dp-presets-s1`, `calendar-type="expanded" range`) on 2026-09-18, web components surface only (`packages/boreal-web-components/src/index.html`, dev server on port 3333).

Flow: open picker -> click "Today" preset -> click Apply -> re-click trigger field to reopen.

**Observed on reopen:**
- Popover header: `Start: 2026/09/18  End: 2026/09/18` — correct, matches applied value.
- Calendar: September 2026 / October 2026 dual months, Sep 18 highlighted blue — correct.
- Trigger field `.value`: `"2026/09/18 – 2026/09/18"` — correct, matches applied value.
- Presets sidebar: **"Custom" carries `bds-date-picker__preset--selected`, not "Today"** — confirmed via DOM query (`[class*=preset]` buttons' className), not just screenshot reading. Even though the applied value is exactly what "Today" produces (same-day run), the sidebar does not re-derive/re-highlight which preset (if any) the current value matches when the popover reopens — it always falls back to "Custom" selected state on a fresh open, regardless of how the previously-applied value was produced.
- No console errors (0 errors / 52 warnings, all warnings were pre-existing unrelated `bds-button` icon-only-label INFO/WARNING noise).
- No flicker, no visual re-navigation glitch — the discrepancy is purely the sidebar's preset-selection indicator, not the date/calendar data itself.

This is an **observational finding only** — reported factually per dispatch instructions, not diagnosed against source. Whether "Custom" is the intended/spec'd reopen behavior (i.e., presets are drafts, not sticky state) or a bug depends on product intent not yet confirmed with the user/plan. Flag for the plan owner before assuming either way.

Not yet checked: React/Vue parity for this same reopen flow, or whether this reproduces on the other three presets scenarios (`dp-presets-s2/s3/s4`).
