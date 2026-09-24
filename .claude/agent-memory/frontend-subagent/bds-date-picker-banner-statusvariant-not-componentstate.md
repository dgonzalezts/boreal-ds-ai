---
name: bds-date-picker-banner-statusvariant-not-componentstate
description: Task 35 (EOA-17662) plan text said DatePickerBanner.state reuses ComponentState, but that's incompatible with bds-banner's variant prop — implemented with StatusVariant instead.
metadata:
  type: project
---

`ai-work/plans/EOA-17662-bds-date-picker-v3.md` Task 35 explicitly said `DatePickerBanner`'s
`state` field "reuses the existing `ComponentState` type from `src/types/states.ts`" and is
"passed straight through to `bds-banner`'s `variant` prop", with a default of `'info'`.

This is internally contradictory: `ComponentState` (`src/types/states.ts`) is
`'default' | 'error' | 'disabled' | 'hover' | 'active' | 'focus' | 'visited'` — it has no
`'info'` member at all, and cannot express `bds-banner`'s actual `variant` prop type,
`StatusVariant` (`'info' | 'success' | 'warning' | 'danger'`, default `'info'`).

Implemented `DatePickerBanner.state?: StatusVariant` instead (imported from `@/types`, same
import `bds-banner.tsx` itself uses) since that's the only type that makes the rest of the
plan's own acceptance criteria true (default `'info'`, direct passthrough to `variant`).

**Why:** a plan document's prose can encode a genuine type-level contradiction that isn't caught
until you read the actual component it says to compose against. `ComponentState` and
`StatusVariant` are easy to conflate by name ("state" field ↔ `ComponentState` type) but cover
completely disjoint value sets in this codebase.

**How to apply:** when a plan says "reuse type X for a field that gets passed straight through
to prop Y of existing component Z," verify X and Y's declared types actually overlap by reading
Z's source before implementing — don't trust the plan's own type name verbatim. Flag the
discrepancy back to whoever owns the plan rather than silently picking one.
