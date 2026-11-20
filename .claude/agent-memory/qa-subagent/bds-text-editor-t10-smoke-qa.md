---
name: bds-text-editor-t10-smoke-qa
description: EOA-18739 T10 smoke QA (2026-11-19, HEAD 248a453f) all pass on Chromium/WebKit/Firefox; reusable isolation recipe and harness gotchas for text-editor forms, paste, link popover and Tab checks
metadata:
  type: project
---

T10 smoke (T5 s1-3, T6 s1, Storybook interactive form, real-Tab focus-visible, regression) passed on Chromium, WebKit 26.5 and Firefox 153 with no component defect.

**Isolation recipe (when 3333/3334 watchers are live):** a temp `stencil.qa-tmp.config.ts` in the package that spreads `./stencil.config`, keeps only a `www` target (`dir` in scratchpad) plus a `dist` target (`dir` in scratchpad; without a dist target tsc fails with "declarationMap needs declaration"), and sets `cacheDir` to scratchpad. Run `stencil build --dev --config stencil.qa-tmp.config.ts` (8s), delete the config, serve with `python3 -m http.server`. Touches no repo output.

**Harness gotchas (all false alarms I hit):**
- macOS Chromium/WebKit: `Home`/`End` scroll the page, even with focus in an `<input>`; the link popover is fixed-positioned so a page scroll detaches it and Playwright then reports "element is outside of the viewport". Use select-all + type instead.
- Rapid back-to-back ArrowLeft/ArrowRight around a chip can race ProseMirror's selection sync; add 60-100 ms waits.
- Firefox synthetic `ClipboardEvent('paste')` has empty `clipboardData` (nothing pastes); use a real copy from a scratch `<input>` then `ControlOrMeta+v`. Chromium needs `grantPermissions` + `navigator.clipboard.writeText`; WebKit accepts the synthetic event.
- WebKit counter text reads one render behind right after typing; wait 400 ms.
- Storybook `forms-text-editor--interactive-form-example` also has a required Subject field: fill it or submit is blocked by it, not by the editor.
- WebKit Tab skips buttons (editable to editable); reach toolbar buttons with a programmatic focus + a real ArrowRight/ArrowLeft (roving tabindex).

**Behaviors recorded (not defects):** native `reportValidity()`/submit flags the editor (invalid event, `aria-invalid`, error text) but does not move focus, same as `bds-text-field`; `insertText` longer than the remaining capacity is rejected whole (`filterTransaction`) while paste truncates; URLs are normalised by the sanitizer (`https://example.org` becomes `https://example.org/`); Esc on the Fields menu returns focus to the trigger, Esc on the link popover returns it to the editor; a focused toolbar button shows its own ring and the container ring.
