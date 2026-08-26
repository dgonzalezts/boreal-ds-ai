---
name: meta-args-defaults-defeat-unset-prop-demos
description: A shared render function that unconditionally forwards args.X onto the element silently defeats any story meant to demonstrate X's "left unset" default behavior, because meta-level args.X still supplies a non-empty value
metadata:
  type: project
---

When a `.stories.ts` file's `meta.args` sets a non-empty default for a prop (e.g.
`format: 'yyyy/MM/dd'` in `bds-date-picker.stories.ts`) and the shared render function forwards it
unconditionally (`format=${args.format || nothing}`), every story built on that render function —
including ones that never override `format` in their own `args` — silently gets that default value
set as an explicit attribute. This defeats any story meant to demonstrate behavior that only kicks
in when the prop is genuinely left unset (e.g. `bds-date-picker`'s `format` auto-switching to
`'yyyy/MM/dd HH:mm'` when left unset and `with-time` is set — `effectiveFormat` only auto-switches
when `this.format === undefined`, and an attribute value equal to the plain-date default still
counts as "explicitly set").

Caught live via `pnpm dev:docs` + playwright-cli: a `WithTime` story that documented the
auto-switch in its JSDoc was actually rendering `format="yyyy/MM/dd"` (no time shown in the
trigger) because it inherited `meta.args.format` unchanged. Reading `el.value` on the trigger field
via `playwright-cli --raw eval "el => el.value"` showed `"2026/08/24"` with no `HH:mm`, not the
`"2026/08/24 08:30"` the story was supposed to demonstrate.

**How to apply:** When a new story needs to demonstrate "prop left at its true unset default"
behavior, explicitly override that prop to `''`/`undefined` in the story's own `args` — don't
assume omitting it from the story's `args` object is enough if `meta.args` already supplies a
non-empty default. Verify by reading the actual rendered DOM property (`el.value`,
`el.getAttribute(...)`), not just the Source panel or a snapshot's visible text, since a stale
attribute value can look plausible without actually confirming the specific default-vs-explicit
codepath being documented.
