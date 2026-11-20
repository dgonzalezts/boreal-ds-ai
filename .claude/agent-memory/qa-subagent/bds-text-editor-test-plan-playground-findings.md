---
name: bds-text-editor-test-plan-playground-findings
description: EOA-18739 (2026-11-20, HEAD 9587e06a) test plan + playground rewrite walk; 4 behaviours found (CRLF value, toolbar Tab stops, forced colours, doc divider example) and harness gotchas for text-editor QA
metadata:
  type: project
---

Plan `ai-work/qa/test-plans/EOA-18739-bds-text-editor-test-plan.md` (50 TCs, TC-TE-01..50) and a rewritten `src/index.html` (10 `.section`s `#s1-form`..`#s10-a11y`, headings carry TC ids). Walked 10 sections in Chromium plus a WebKit spot check, all expected results held except the findings below.

**Findings (not yet bug-reported):** F-01 `value` keeps `\r\n` after `editor.value = 'a\r\nb'` (docs/ADR say normalised; only parse normalises) until the first edit. F-02 toolbar: before any arrow key every tool is a Tab stop; after the first ArrowRight/Left `bds-toolbar` goes roving (one stop). F-03 no `forced-colors` rule: chip has 0px border and vanishes. F-04 MDX example `toolbar="fields|link"` is an unknown id (divider needs `fields,|,link`).

**Harness gotchas:**
- `document.execCommand('insertText')` in a synchronous loop lands in ONE ProseMirror DOM flush, the limit plugin rejects the whole transaction (value stays ''). Yield one macrotask (`setTimeout 0`) per char to mimic fast typing.
- A native helper button (e.g. "Clear log") steals focus, so the next editor click logs a fresh `bdsFocus`; not a spurious event.
- ArrowLeft from after a chip selects it (NodeSelection); typing then replaces the chip. A second ArrowLeft puts the caret before it.
- Click at far right of a line with an end-of-line chip is fine for Backspace but stale `boundingBox()` after a scroll misses; recompute the box or use `locator.click({position})`.
- `bds-popover` selectors: the link popover is the direct child `#id > bds-popover`; `#id bds-popover` first matches the Fields dropdown's popover. `label` on bds-button is a prop, read `aria-label` of the inner `<button>`.
- `.ProseMirror` height is masked by the editable's `min-height: 69px`; measure `.ProseMirror p` (20px one line) to detect chip-at-line-end growth.
