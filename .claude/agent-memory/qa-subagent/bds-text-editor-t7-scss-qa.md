---
name: bds-text-editor-t7-scss-qa
description: EOA-18739 T7 SCSS manual QA (Chromium/WebKit/Firefox) - two real cross-browser defects (WebKit absolute placeholder blocks typing, Firefox never matches :active on contenteditable) plus reusable Playwright caret/engine techniques
metadata:
  type: project
---

EOA-18739 Task 7 (uncommitted SCSS) QA, 2026-11-19. All Figma-state/ruling/ring/chip/theme checks passed in Chromium, WebKit and Firefox 153 except two real defects:

1. **WebKit: an empty editor WITH a placeholder cannot be typed into and shows no caret.** Cause is `position: absolute` on `.bds-text-editor__placeholder` (the ProseMirror `contenteditable=false` widget inside the `<p>`). WebKit gets `keydown`/`keypress` but no `beforeinput`, value stays `''`. Bisected by injecting CSS: `position: static` fixes it; `user-select`/`pointer-events` do not. `position: relative` and `display:inline-block; width:0; white-space:nowrap; overflow:visible` also fix typing; `float:left; width:0` does not. Committed pre-T7 SCSS had no placeholder rule, so it is a T7 regression.
2. **Firefox: `:active` never matches a `contenteditable` element** (plain div works), so the Active inner shadow (`.bds-text-editor__editable:active`) never shows. Probe: `el.matches(':active')` during `mouse.down()`.

**Why:** both are invisible in Chromium-only QA and in computed-style checks.

**How to apply (reusable):**
- Playwright `screenshot()` defaults to `caret: 'hide'`; pass `caret: 'initial'` and sample several frames (caret blinks) to see a caret; detect it as a thin vertical dark column. Firefox screenshots never show the caret.
- Caret after a chip at line end: Chromium draws it inside the pill's right padding (4px short of the edge, 15px tall); WebKit draws it after the pill (18px).
- Verify "can type" with a real `keyboard.type` on an EMPTY editor in every engine; populated editors hide the bug.
- In `run-code` there is no `require`/`fs`: create output dirs with `mkdir -p` beforehand.
- `locator('bds-list-menu-item:visible', {hasText})` times out in WebKit even though the dropdown is open; find the item via `page.evaluate` bounding box and `page.mouse.click`.
- Element screenshots with `pad` get clipped by the viewport edge (a 160 vs 164 height is not a real size difference).
- Playwright WebKit skips buttons on Tab; Shift+Tab to a toolbar tool is not valid there.
- `text-default-darker` resolves to `#595d64` in the engage theme in this repo while Figma shows `#131316`; bds-text-field uses the same token, so the editor text looks lighter than the frames (token value, not component).
- `p { margin: 2em }` still reaches `bds-typography`'s label/helper/counter `<p>` (host +96px), not the editor text.
