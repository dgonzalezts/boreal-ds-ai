---
name: storybook-docs-page-double-iframe-popover-positioning
description: How to diagnose floating/popover (bds-dropdown, bds-popover) mispositioning that only reproduces on the Storybook Docs page, not the standalone Canvas tab
metadata:
  type: project
---

The Storybook Docs page (`?path=/docs/<id>`) renders each `<Canvas of={...}/>` story inside `iframe[title="storybook-preview-iframe"]` — one extra nesting level versus the standalone Canvas tab (`iframe.html?id=...&viewMode=story`), which has none. A floating-positioned element (e.g. `bds-dropdown`, `bds-popover`) that computes its own coordinates via manual `getBoundingClientRect()`/`style.left/top` math instead of a proper anchor API can end up thousands of pixels off-page in the double-nested Docs context, while looking perfectly anchored in the plain Canvas tab — this is a real, reproducible bug class, not a fluke of one component.

**Diagnostic steps that worked** (confirmed EOA-16000 Task 13's `WithColumnVisibilityDropdown` bug and its fix):
1. Reproduce on plain Canvas first: `goto http://localhost:6006/iframe.html?id=<story-id>&viewMode=story`, click the trigger, and read the floating element's `getBoundingClientRect()` — this is the "known good" baseline.
2. Reproduce on the Docs page: `goto http://localhost:6006/?path=/docs/<docs-id>` (get the correct docs id from `curl -s http://localhost:6006/index.json` filtered to `"type":"docs"` — guessing `<component>--docs` is often wrong; this project's id was `data-visualization-table--overview`), then `document.querySelector('iframe[title="storybook-preview-iframe"]').contentDocument` to reach into the nested frame's DOM directly via `eval`.
3. **Scope every selector to the specific dropdown/popover instance's `id`** (e.g. `frame.querySelector('#dropdown-col-vis-xxxxx')`), not a bare `[role="menu"]`/`[role="listbox"]` — a large MDX docs page has dozens of matching elements from unrelated stories on the same page, and an unscoped query silently returns the wrong one (looked like `{x:0,y:0,w:0,h:0}`, i.e. "still broken," when the real element was actually correctly positioned two DOM queries away).
4. Compare button vs. floating-element rects: correct anchoring shows an exact edge match (e.g. floating element's right edge == button's right edge for bottom-end placement, floating element's top == button's bottom for a directly-below placement). A broken case shows `y` in the thousands/tens-of-thousands or `w:0,h:0` persisting even when scoped correctly.

The actual fix in this case: replacing manual `getBoundingClientRect()`/`style.left/top` positioning in the story script with `bds-popover`'s `setAnchorElement()` API resolved it — the manual math was computing offsets relative to the wrong window/frame context when double-nested.
