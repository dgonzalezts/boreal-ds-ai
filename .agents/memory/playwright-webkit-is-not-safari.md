---
name: playwright-webkit-is-not-safari
description: "Playwright's WebKit build is not Safari.app — compositing, Tab-to-button and autofill behaviour all differ — and a scripted loop of key events inside one call is not the same as repeated real presses. Label the evidence accordingly."
---

# Playwright WebKit is not Safari.app, and scripted key loops are not real presses

WebKit automation is a reasonable proxy for layout and the general rendering pipeline, but it has repeatedly diverged from real Safari.app on this library:

- **Compositing and animation timing** — a Safari-only paint or transition artifact may not appear in WebKit automation, and a WebKit artifact may not appear in Safari (`safari-virtualized-row-transition-on-remount.md` was found in Safari.app).
- **Tab order** — macOS Safari's default "Tab highlights each item" setting is off, so `keyboard.press('Tab')` skips `<button>` elements under WebKit; focus-visible modality also differs from Chromium.
- **Autofill appearance** — native autofill styling is Safari-specific and does not reproduce under automation.

Consequences for QA reporting: say "Chrome and Playwright WebKit" when that is what ran; keep Safari-only claims as explicit manual steps for the user; never describe a WebKit pass as "Safari verified". The reverse also holds — do not reopen a Safari bug because WebKit does not reproduce it.

**Scripted key loops.** Repeating key events inside a single scripted call (a loop in one `evaluate`, or a tight loop of `page.keyboard.press`) does not reproduce OS key-repeat: no `repeat` flag, no inter-key delay, no frame between presses. Anything rAF-gated, or behaviour that depends on holding a key (auto-scroll, repeat navigation), can therefore differ from a human holding it. When a checklist says "hold ArrowDown past the window", use separate presses with a short wait rather than an in-page loop.

**Source:** EOA-19597 T14/T17 (WebKit pass followed by a separate Safari.app confirmation by the user), plus earlier Safari-vs-WebKit divergences in EOA-17138 and EOA-17662.
