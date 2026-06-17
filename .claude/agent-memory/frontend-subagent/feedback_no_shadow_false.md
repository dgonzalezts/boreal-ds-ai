---
name: feedback_no_shadow_false
description: Never set shadow: false in @Component decorator — Stencil defaults to light DOM without it
metadata:
  type: feedback
---

Do not include `shadow: false` in the `@Component` decorator options.

**Why:** Stencil's default mode is already light DOM (no shadow root) when `shadow` is omitted. Adding `shadow: false` is redundant noise and was actively removed from `bds-table-column` during Task 3 cleanup.

**How to apply:** Write `@Component({ tag: 'bds-foo', styleUrl: 'bds-foo.scss' })` — no `shadow` key at all. Only add `shadow: true` when explicitly adopting shadow DOM, which Boreal DS does not do.
