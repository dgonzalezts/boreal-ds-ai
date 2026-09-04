---
name: playwright-getbyrole-ambiguous-across-multiple-open-date-pickers
description: In src/index.html, many bds-date-picker scenarios share identical accessible names ("Previous month", "Next month", "Apply"). A page-wide getByRole(...).nth(N) or .first() locator silently resolves to the wrong picker's button when more than one popover happens to be open (or left open) in the same session, producing false negatives (header appears "stuck") without any error.
metadata:
  type: project
---

**Symptom:** clicking `getByRole('button', { name: 'Previous month' }).nth(1)` (or `.first()`)
against `src/index.html` sometimes does nothing observable to the scenario under test — the
target picker's header never updates across repeated clicks, even though the click command
itself reports success with no error.

**Root cause:** `src/index.html` accumulates many `bds-date-picker`/`bds-calendar-grid` demo
scenarios on one page (by design — see the "never delete a previous scenario" convention). Many
of them use identical `aria-label`s ("Previous month", "Next month", "Apply", "Clear", "Cancel").
`getByRole(...).nth(N)` indexes into the *page-wide* DOM order of all matching elements, not
just the ones inside the picker you scrolled to — if an earlier scenario's popover is still open
(or was left open from a prior click sequence, e.g. a failed click auto-scrolled the page
elsewhere without closing it), your `.nth(1)` may resolve to a completely unrelated picker's
button.

**Fix / reliable pattern:**
1. **Always scope to the target element's id first**, then find the specific matching button
   inside it via `eval`, e.g.:
   ```js
   () => {
     const dp = document.getElementById('dp-under-test');
     const grid = dp.querySelectorAll('bds-calendar-grid')[1]; // second calendar
     const btn = grid.querySelector('.bds-calendar-grid__header button[aria-label="Next month"]');
     const r = btn.getBoundingClientRect();
     return { x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2) };
   }
   ```
2. Click via **coordinate-based mouse events** (`playwright-cli mousemove X Y`, `mousedown`,
   `mouseup`) rather than a role/text locator — coordinates are unambiguous once you've
   confirmed via `eval` which exact DOM node you're targeting.
3. `element.click()` via `eval` is unreliable for these buttons too (silently no-ops in some
   cases observed in this session) — prefer the coordinate-based real mouse click.
4. Before testing a specific scenario, consider a hard `reload` to guarantee no leftover popover
   from a previous scenario is still open and polluting page-wide role/text queries.
5. `playwright-cli snapshot` refs (`f4e362` etc.) DO correctly resolve to the exact element they
   were captured against, so a fresh snapshot immediately before clicking (reading the ref next
   to the exact header text you want) is also reliable — but refs regenerate after every DOM
   mutation, so you must re-snapshot before each subsequent click in a repeat-interaction loop
   (the coordinate approach avoids this re-snapshot overhead when the button's screen position
   is stable across clicks, e.g. a fixed-position popover header).

**Also confirms:** `bds-calendar-grid` header text lives at
`.bds-calendar-grid__header` (not any `[class*=month-year]`-style guess), and nav buttons are
`button[aria-label="Previous month"]` / `button[aria-label="Next month"]` inside that header.
