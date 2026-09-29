# ADR 0018 — `bds-date-picker` external (non-field) trigger scope

**Date:** 2026-09-28
**Status:** Proposed

---

## Context

A teammate requested either documentation for `bds-calendar-grid` or a way to open the date-picker calendar from an external component such as a button. The reference screenshot (a "Client secret expiration" step) shows a segmented button group — `3 months`, `6 months`, `12 months`, `18 months`, `24 months`, `Custom date` — where activating **Custom date** opens a single-date calendar anchored to that button. The chosen date is rendered by the consumer as a sentence ("Client secret will expire on Sep 15, 2026"), not inside a text field. The month quick-picker visible in the screenshot already exists inside `bds-calendar-grid`.

This pattern is **not covered by the current designs**: the Figma spec for `bds-date-picker` only defines a text-field trigger.

The current implementation cannot serve it:

- **The trigger is hard-wired to `bds-text-field`.** `bdsField` queries `bds-text-field` only (`bds-date-picker.tsx:665`). In `componentDidLoad` the popover's listen and anchor elements are set to that field's inner `.bds-text-field__container` (`:339-344`), and click/keydown listeners are attached to the field (`:346-347`).
- **Opening is private and stateful.** `listenClickTrigger` (`:612`) re-hydrates the draft from `value`, resolves the display month, resets the banner, re-matches presets, and only then calls `openPopover()`. There is no public `open()`/`close()` `@Method()` — the only public methods are `checkValidity`/`reportValidity`.
- **Refocus, validation and `required` assume a field.** `closePopoverAndRefocus` returns focus to the field's `<input>` (`:689`); `validityAnchor` targets that input (`:990`); `syncFieldRequired`/`syncFieldError`/`syncFieldValue` write onto the field.
- **`bds-calendar-grid` is not consumable standalone.** Its required `grid` prop expects a precomputed `MonthGrid` produced by `generateMonthGrid` in `@/services`, which is not part of the package's public exports (`src/index.ts` exports only `ToastService`; the `./types` subpath does not include `services`). It is fully parent-controlled — month navigation, `min`/`max` nav guards, and expanded-mode focus hand-off all live in `bds-date-picker`. The MDX already describes it as "an internal implementation detail with no dedicated Storybook entry".
- **`bds-button` swallows native `click`.** `bds-button` calls `event.stopPropagation()` and re-emits `bdsClick` (`bds-button.tsx:188-197`), so any button-trigger support must listen for `bdsClick`, not `click`.

---

## Non-Goals

- Does not add a design for the button-triggered calendar — that belongs to the design team.
- Does not make `bds-calendar-grid` or the date engine (`@/services/date-engine`) part of the public API.
- Does not change `bds-date-picker`'s behavior for the existing text-field trigger.
- Does not implement anything in this ADR; it scopes documentation now and a follow-up feature later.

---

## Options Considered

### Option A — Document the limitation only (accepted, short term)

Add a "Known limitations" note to `bds-date-picker.mdx` and a one-line clarification to the `field` slot JSDoc stating that `bds-text-field` is the only supported trigger and `bds-calendar-grid` is not usable standalone.

**Pros:**
- ~0.5 day; answers the teammate's question directly and in the place consumers look first.
- No new public API to maintain.

**Cons:**
- Does not unblock the screenshot's use case.

---

### Option B — Document a workaround via internal elements (rejected)

Either forward a button's `bdsClick` to `picker.querySelector('bds-text-field').click()`, or call `picker.querySelector('bds-popover').openPopover()` directly.

**Pros:**
- No component changes.

**Cons:**
- The popover stays anchored to the text field; hiding the field breaks positioning, showing it contradicts the design.
- Calling `openPopover()` directly bypasses draft hydration in `listenClickTrigger`, showing stale selection state.
- Both depend on internal light-DOM structure the MDX explicitly declares non-public — documenting them would turn internals into an implicit contract.

---

### Option C — Generic trigger + public `open()`/`close()` on `bds-date-picker` (accepted, follow-up)

Accept a non-field element (e.g. `bds-button`) as the trigger — via a widened `field` slot or a new `trigger` slot — anchor/listen on it, and expose `open()`/`close()` `@Method()`s routed through the same hydration path as `listenClickTrigger`.

**Pros:**
- Covers the screenshot with `calendarType="default"` (single date, commit on click, quick-picker included).
- Reuses all existing calendar, validation and form-association logic; `bds-calendar-grid` stays internal.

**Cons:**
- ~3–5 days including tests, docs and React/Vue parity.
- Field-less mode needs answers for: display of the committed value (consumer via `bdsChange`), validation-error surface, `required` forwarding, refocus target, and trigger ARIA (`aria-haspopup="dialog"`, `aria-expanded`).

---

### Option D — New public standalone calendar component (rejected for now)

A `bds-calendar` that computes its own grid from `year`/`month`/`min`/`max`/`value`, embeddable inline or inside a consumer-owned `bds-popover`.

**Pros:**
- Maximum flexibility (inline calendars, custom overlays).

**Cons:**
- ~6–10 days; a new component with its own API, docs and test gate.
- Duplicates navigation/nav-guard logic currently owned by `bds-date-picker` unless it is extracted first.
- No design spec and no second concrete use case justifying it yet.

---

## Decision

**Short term: Option A.** Document in `bds-date-picker.mdx` and the `field` slot JSDoc that the text field is the only supported trigger and that `bds-calendar-grid` is internal and not usable standalone. Do not document any workaround (Option B).

**Follow-up: Option C**, tracked as its own ticket and **gated on a design spec** for the button-triggered calendar (popover alignment relative to the button, header/footer presence, how the committed value is shown).

Option C is preferred over D because it satisfies the only concrete use case while keeping `bds-calendar-grid` and the date engine private. D should be revisited only when a need appears that a trigger-based popover cannot serve (e.g. an always-visible inline calendar).

| What | Where / How |
|---|---|
| Consumer-facing limitation | `bds-date-picker.mdx` "Known limitations" + `field` slot JSDoc |
| Feature request | Jira ticket for Option C (link from the MDX without ticket IDs in the text) |
| Design gap | Design request / Figma comment for the button-triggered pattern |
| Reasoning | This ADR (local) — mirror to Confluence if the team needs it shared |

---

## Consequences

**Positive:**
- Consumers get a clear, accurate answer instead of relying on internal DOM.
- `bds-calendar-grid` and the date engine keep freedom to change without breaking consumers.
- The follow-up feature starts from a scoped list of open questions rather than rediscovery.

**Trade-offs / obligations:**
- The screenshot's flow stays unsupported until Option C ships; teams needing it now must use the text-field trigger.
- When Option C is implemented, the MDX limitation note must be updated, and trigger-agnostic handling must cover `bdsClick` from `bds-button`.
- If Option D is ever pursued, the navigation/nav-guard logic in `bds-date-picker` (`computeNavGuard`, `handleMonthNavigate`, `tryHandOffFocus`) should be extracted first to avoid duplication.
- `ai-docs/` is excluded from git (`.git/info/exclude`), so this ADR is not visible to teammates; the shared record must live in Jira/Confluence.
