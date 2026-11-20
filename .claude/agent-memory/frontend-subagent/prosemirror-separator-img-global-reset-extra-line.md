---
name: prosemirror-separator-img-global-reset-extra-line
description: bds-text-editor chip at end of line renders an extra line and no caret because boreal.css `img { display: block }` overrides ProseMirror's separator img; prosemirror.css is never loaded
metadata:
  type: project
---

`prosemirror-view` 1.42.9 does not inject its stylesheet and the repo never imports `prosemirror.css`, so every rule in it is absent, including `img.ProseMirror-separator { display: inline !important }`. The global reset in `boreal.css` (`img, picture, video, canvas, svg { display: block; max-width: 100% }`) then turns the two separator `<img>` elements PM puts around a trailing inline atom into block boxes: the editor grows by one line and the DOM caret (anchored after the second separator, before the trailing `<br>`) is drawn on the empty second line or not at all. Typing replaces the hack nodes, so the extra line "disappears".

**Why:** Prior QA checked only `document.activeElement` and typing with a chip mid-line, where PM emits no separators. Focus and selection were correct the whole time, so the deferred-focus hypothesis was a red herring.

**How to apply:** The fix is `img.ProseMirror-separator { display: inline; border: none; margin: 0 }` nested under `.ProseMirror` in `bds-text-editor.scss`. Any other PM CSS that matters (`.ProseMirror-selectednode`, `.ProseMirror-hideselection`) is also missing; T7 must style them deliberately. Verify caret visibility in a real browser by setting `caret-color: #f00` and scanning screenshots (Playwright's default `caret: 'hide'` and the blink phase hide it otherwise); headless Chromium, WebKit (webkit-2368 via `executablePath` `pw_run.sh`) and Firefox all paint it. `newSpecPage` cannot catch this (no layout).
