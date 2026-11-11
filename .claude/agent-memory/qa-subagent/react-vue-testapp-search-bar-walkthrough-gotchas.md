---
name: react-vue-testapp-search-bar-walkthrough-gotchas
description: Concrete playwright-cli sequencing gotchas for driving bds-search-bar in examples/react-testapp and examples/vue-testapp — windowed items unmount when the popover hides, an open popover blocks clicks on the next section's input, and the <html> gutter is at the bottom of the viewport, not the left edge
metadata:
  type: project
---

Found during EOA-19597 Task 18 (2026-10-26, Chrome, ports 5181/5182):

- **Windowed `bds-list-menu-item`s unmount the moment the popover hides.** Any probe of
  "mounted count / firstValue / scrollTop" has to run while the popover is open. A bare
  `document.querySelectorAll('bds-list-menu-item').length` after any outside click returns 0 and looks
  like the empty-dropdown bug (T30) when it is not.
- **Open popovers block the next widget.** Clicking section B's input while section A's popover is open
  times out (`locator.click` 30 s, "attempting click action" forever) because the floating panel overlaps
  it. Dismiss first — clicking the `<html>` gutter works since T33: `page.mouse.click(20, 990)`.
- **The `<html>` gutter in these apps is at the BOTTOM, not the left/right edge.** `main`/`#app` are
  centred with `max-width`, but `body` is only ~936 px tall in a 1600×1000 viewport, so every point with
  `y > 936` resolves to `<html>`; x = 0…20 at y ≈ 500 resolves to `DIV#root` or `#app`. Probe
  `document.elementFromPoint(x, y).tagName` before asserting a click-outside test.
- **Wait ~2.5 s after `goto`/`reload` before the first click.** Clicking the search field before Stencil
  hydration attaches listeners silently does nothing: `document.activeElement` stays `BODY`,
  `aria-expanded` stays `false`, later `keyboard.type` lands nowhere and the field stays empty with no
  console error. Two consecutive probes then read misleading state.
- **Don't reuse one page across sub-checks.** Typed text accumulates (`99` + `99` = `9999`, 0 matches,
  empty list). Reload between checklist items, or select-all before typing.
- **Counting events per interaction:** clear the in-app event log first, but the log's "Clear log" button
  is outside the popover, so it closes the popover — clear first, then open the bar and act.
- Exit codes for `pnpm validate:pack:react|vue` are easiest read from Turbo's `N successful, N total`
  line (zsh's `$PIPESTATUS[0]` is empty; zsh uses `$pipestatus[1]`).
