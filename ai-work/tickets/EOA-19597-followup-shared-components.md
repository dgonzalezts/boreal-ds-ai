# Follow-up ticket from EOA-19597 — shared-component pre-existing behaviour

**Source plan:** `ai-work/plans/EOA-19597-bds-search-bar-virtual-suggestions.md` (tasks T23, T27, T39, T56, T58, T60)
**Suggested project:** EOA · type: Task · components: `bds-select`, `bds-popover`, `boreal-vue`, `bds-button`, `bds-text-field`

**Status (2026-10-28):** open — nothing in this file is fixed by the EOA-19597 PR.
**Already shipped (do not re-implement):** `bds-text-field`'s focus forwarder now guards on `event.target === event.currentTarget` (`605049af`), which fixes the mock-doc recursion; §6 below is only the remaining `isDisabled` decision, not the guard itself. The search bar also tolerates a bubbled list `bdsChange` after an `items` toggle (`fb4c9c2c`) — that is a workaround, **not** a fix for §1.
**Overlaps:** §1 is the same root cause as `EOA-19597-followup-search-bar-items-toggle.md` §1 (listener bound once, list re-created); fix §1 here and the items-toggle tolerance can later be removed deliberately. §6 belongs with the `bds-text-field` work in `EOA-19597-followup-bds-tag-field-focus-guard.md` (same forwarder pattern). §2's prototype runtime shim was built, verified and reverted — do not rebuild it without deciding the option first.


## Summary

Defects uncovered while building `bds-search-bar` `items` mode. None is caused by EOA-19597; each needs its own decision or a shared-component change.

## 1. Reconnect loses listeners — OPEN (was T23; also the root cause of the items-toggle workaround)

Removing and re-appending a `bds-select` (or any overlay) stops click-to-open and item selection: `bds-select` and `bds-popover` wire listeners only in `componentDidLoad` and remove them in `disconnectedCallback`, with no `connectedCallback`. Reproduced with a plain `bds-select`, so it is not search-bar-specific.

- **Fix shape:** add `connectedCallback` re-wiring (or make the wrappers remount).
- **AC:** after a remove/re-append, click-to-open, selection, escape and keyboard all behave as on a fresh mount; specs for both components.

## 2. Vue `v-model` leaks a `modelvalue` attribute — OPEN (was T27; shim reverted, decide option first)

`@stencil/vue-output-target` declares `modelValue` as a container prop and copies every declared prop onto the element; Vue falls back to `setAttribute` because the custom element has no such property. Cosmetic: `value` and `v-model` work.

- **Evidence:** installed 0.11.8; latest 0.14.6 still spreads it; `ComponentModelConfig` has no suppression option. A runtime shim was prototyped, verified (`0` leaked attributes) and **reverted** because it forks the upstream runtime and wraps all 18 model components.
- **Decision needed:** accept + document, adopt the shim, or pursue an upstream fix/patch. Weigh the 0.11.8 → 0.14.6 upgrade at the same time (it does not fix this leak by itself).
- **AC:** one of the three options recorded and implemented; no `modelvalue` attribute in a real Vue run if the fix option is chosen.

## 3. Re-clicking an already-selected option clears the value — OPEN (was T39)

In `bds-list-menu` single-select, clicking the selected item deselects it (`value` becomes `""`). This is reachable in slotted search-bar mode when a typed query equals an item's `value` (the debounce commits it, making it selected). Identical on a plain `bds-select`.

- **Decision needed:** keep toggle-off as intended, or stop clearing on re-click.
- **AC:** documented behaviour, spec covering the chosen semantics, and `items` mode confirmed unaffected.

## 4. `bds-date-picker` icon buttons warn `No accessible name found` — OPEN (was T56)

Three warnings per picker, but steady-state DOM shows all six buttons correctly named and the unit suite produces none. This is the known hydration-race false positive in `ai-work/qa/bug-reports/2026-08-06-bds-button-accessible-name-remaining.md`.

- **Fix shape:** move `checkAccessibleName()` off `componentWillLoad` (the relocation already applied to `hasSlotContent`).
- **AC:** zero warnings on the dev server for a picker and a select popover; regression spec.

## 5. `bds-button` logs an icon-only `console.info` on every mount — OPEN (was T58)

138 lines per date-picker test run, even for buttons that have a `label`. Two date-picker specs already call `suppressConsoleInfo()` (15/15 in that folder).

- **Fix shape:** log once per instance, gate on development builds, or drop the message now that the accessible-name check is enforced.
- **AC:** a suite run of the date-picker folder needs no `suppressConsoleInfo()` shim; diagnostics preserved for genuinely unnamed buttons.

## 6. `bds-text-field` forwards focus on a disabled field — OPEN, decision only (was T60, PD-01)

The guard added in T57 checks `!readOnly` but not `!isDisabled`, so `host.focus()` on a disabled field still calls `input.focus()` (a platform no-op; an event dispatch under mock-doc).

- **Decision needed:** keep the platform no-op or add `!isDisabled` for symmetry.
- **AC:** behaviour stated in the component JSDoc/memory and covered by a spec.
