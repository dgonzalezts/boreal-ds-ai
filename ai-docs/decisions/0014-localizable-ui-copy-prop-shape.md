# ADR 0014 — Prop shape for localizable UI copy

**Date:** 2026-09-08
**Status:** Proposed

---

## Context

`bds-date-picker` is the only component in the library that localizes its own UI copy through a single bundled-object prop:

```ts
@Prop() labels?: DatePickerFooterLabels;
// merged against an English default:
const labels = { ...DEFAULT_FOOTER_LABELS, ...this.labels };
```

`DatePickerFooterLabels` currently covers `clean`/`cancel`/`apply`/`hour`/`minute`/`start`/`end` (7 keys), and Phase 6 (presets list text) and Phase 7 (banner/footer-summary text) will each add more.

A repo-wide `labels?:` grep across every component in `packages/boreal-web-components/src/components/` returns exactly one hit — `bds-date-picker.tsx`. Every other localizable component instead exposes one flat string `@Prop()` per label, each with its own English default:

- `bds-search-bar.searchButtonLabel`
- `bds-table.selectionLabel`
- `bds-pagination.perPageLabel`
- `bds-banner.closeButtonLabel`
- `bds-tag.closeButtonLabel`

`bds-date-picker` diverged from this convention when Clean/Cancel/Apply were first added (v1), and nothing has reconciled the two shapes since. This was flagged as an unscheduled, design-system-wide inconsistency in [`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`](../../ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md#unscheduled--labels-prop-pattern-inconsistency-design-system-wide-new-2026-09-08), which recommended resolving it via ADR before Phase 6/7 add more strings under either shape by default.

Separately (out of scope for this ADR — see Non-Goals): a repo-wide audit found several components with hardcoded, non-localizable English strings and *no* prop of either shape (`bds-pagination`'s nav-button labels, `bds-calendar-grid`'s "Previous/Next month", `bds-toast-item`, `bds-color-picker`, `bds-breadcrumb`, `bds-drawer-header`, `bds-setting-step-item-header`, `bds-popover`). This ADR governs the shape for *new* localizable props; it does not itself add coverage to those components.

---

## Non-Goals

- Does not add localization coverage to components that currently have none (tracked separately, see Context).
- Does not solve pluralization. No plural-rule mechanism exists anywhere in the codebase today, and a flat string prop cannot express one (Phase 7's footer summary needs "1 day" vs. "18 days"). This needs its own ADR once a component actually requires it.
- Does not introduce a project-wide i18n/message-catalog mechanism. No such mechanism exists today (confirmed via repo-wide search for "i18n"/"translation"/"locale-catalog"/"ICU"); consumers currently pass every string individually per instance, with no way to supply "the Spanish set" once. This is a larger, separate architectural question.
- Does not touch `locale` (`DateEngineLocale`, a `date-fns` `Locale` alias). `locale` and UI-copy `labels` are two fully disconnected systems today — `locale` drives date-fns formatting (weekday/month names) only, never UI copy — and this ADR does not merge them.

---

## Options Considered

### Option A — Conform `bds-date-picker` to the flat-per-prop convention

Break `bds-date-picker`'s own precedent; split `labels` into `cleanLabel`, `cancelLabel`, `applyLabel`, `hourLabel`, `minuteLabel`, `startLabel`, `endLabel`, plus new flat props for every Phase 6/7 addition.

Matches five existing components. But `bds-date-picker` already has 7 keys and is still growing — a flat prop per string does not scale past a handful of labels: each new locale-dependent string becomes a new prop (API surface growth), and a consumer wanting to supply a full non-English label set must wire every prop individually rather than pass one object. Phase 6/7 would each add more individual props under this option, compounding the API surface every phase. Rejected.

### Option B — Adopt the bundled-object shape design-system-wide

Convert `bds-search-bar.searchButtonLabel`, `bds-table.selectionLabel`, `bds-pagination.perPageLabel`, `bds-banner.closeButtonLabel`, `bds-tag.closeButtonLabel` to bundled-object props to match `bds-date-picker`.

Reverses precedent for five shipped, in-use components purely for consistency — a breaking API change for each, with no functional upside, since each of those components only ever needs a single string. Migrating shipped components for consistency alone, with no reported pain point driving it, is scope beyond what this ADR needs to resolve. Rejected as a required migration; not rejected as a future option if one of those components ever grows a second localizable string (see Decision).

### Option C — Threshold rule: bundled-object for ≥2 localizable strings, flat prop for exactly 1

`bds-date-picker` keeps its bundled `labels` object (7+ keys, growing). Existing single-string components (`bds-search-bar`, `bds-table`, `bds-pagination`, `bds-banner`, `bds-tag`) are left as-is — no forced migration. Any *new* component, or any *existing* component that grows past one localizable string, adopts a bundled-object prop from that point forward.

No breaking changes to shipped components. Gives Phase 6/7 (and any future component) an unambiguous rule to follow without re-litigating per task. Accepted.

---

## Decision

Adopt **Option C**: a component with exactly one localizable string uses a single flat `@Prop() <name>Label: string` with an English default. A component with two or more localizable strings uses a single bundled-object prop (naming convention: `labels?: <ComponentName>Labels`, merged against a `DEFAULT_<COMPONENT_NAME>_LABELS` constant, matching `bds-date-picker`'s existing `{ ...DEFAULT_FOOTER_LABELS, ...labels }` pattern).

This is not retroactive for components currently below the threshold: `bds-search-bar`, `bds-table`, `bds-pagination` (existing `perPageLabel`), `bds-banner`, and `bds-tag` keep their flat props unless and until one of them needs a second localizable string, at which point it converts to the bundled shape rather than adding a second flat prop.

`bds-pagination`'s hardcoded nav-button strings ("Jump pages", "Go to first/previous/next/last page") are a pre-existing coverage gap, not a shape decision — if and when that gap is fixed, the resulting props push `bds-pagination` over the 1-string threshold and it converts to a bundled `labels` prop under this rule rather than adding four more flat props.

---

## Consequences

- **Phase 6/7 unblocked**: date-picker's presets list text and banner/footer-summary text extend the existing `DatePickerFooterLabels`/`DEFAULT_FOOTER_LABELS` pattern — no new prop-shape decision needed at task time.
- **No breaking changes**: nothing shipped today changes as a direct result of this ADR.
- **A visible two-shape system persists by design**: `bds-tag.closeButtonLabel` (flat) and `bds-date-picker.labels` (bundled) are both correct under this rule, for different reasons (string count), not inconsistency. Document the threshold in the component-authoring conventions (`.agents/memory/` or the Stencil component-knowledge skill) so future component authors don't rediscover this ADR from scratch.
- **Coverage gaps remain**: the eight components with zero localization props today (see Context) are unaffected by this ADR and need their own tracked follow-up work to add props under this rule.
- **Pluralization and a locale-catalog mechanism remain open**: any component needing plural forms (Phase 7's footer summary) needs a follow-up ADR before that specific string ships, since neither prop shape in this decision expresses plural rules.
