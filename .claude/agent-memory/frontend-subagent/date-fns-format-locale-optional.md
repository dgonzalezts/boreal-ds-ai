---
name: date-fns-format-locale-optional
description: date-fns@4.4.0's format() takes options as a whole-object optional param, and locale within FormatOptions is optional too — passing { locale: undefined } is safe and falls back to date-fns's default English locale without throwing.
metadata:
  type: project
---

Verified against the installed `date-fns@4.4.0` type declaration (`node_modules/.pnpm/date-fns@4.4.0/node_modules/date-fns/format.d.ts`): `format(date, formatStr, options?: FormatOptions)` — the whole `options` object is optional, and `FormatOptions extends LocalizedOptions<...>` which makes `locale` itself optional inside it. So `format(date, formatStr, { locale })` with `locale: undefined` is safe and falls back to date-fns's built-in default (English) locale — never throws.

**Why:** confirmed while implementing `packages/boreal-web-components/src/services/date-engine/format.ts` (Task 5 of the `bds-date-picker` plan, EOA-16692) — the task explicitly asked to verify this via the actual type signature rather than assume it, to avoid adding unnecessary defensive `locale ?? undefined` guards.

**How to apply:** any `date-engine` (or other date-fns-consuming) function that accepts an optional `DateEngineLocale` can pass it straight through as `{ locale }` to date-fns's `format`/`startOfWeek`/etc. without an extra undefined-check — this matches the existing pattern already used in `grid.ts` (`format(referenceMonth, 'LLLL yyyy', { locale })`, `startOfWeek(referenceMonth, { weekStartsOn, locale })`).
