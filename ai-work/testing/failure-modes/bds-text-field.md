# Failure-Mode Catalog — `bds-text-field`

Audited against `packages/boreal-web-components/src/components/forms/bds-text-field/` as of 2026-10-26 (branch `fix/EOA-19598-search-bar-virtual-scroll-feature_DG`, fix for plan task T57 of `EOA-19597` applied, uncommitted). Rows are derived from reading `bds-text-field.tsx` and the pre-existing five-file spec suite — not from the plan's stated test list.

Scope of this first audit: the container→inner-input focus forwarding contract that T57 fixes, because that is the area this dispatch covers. The rest of the component (validation timing, FACE callbacks, action buttons, footer rendering) is already exercised by the existing 100-test suite and was read only to cross-check that no focus row contradicts it. Later audits of this component should extend this file with the remaining families rather than start over.

Rows marked `pending-decision` have no test; they are reported to the user and must be ruled on before any test or source change lands.

---

### FM-01 | Container focus forwards to the inner input exactly once

- **ID:** FM-01
- **Category:** component-contract-bypass
- **Risk:** a11y/functional — the host is the tab stop consumers see (`tabIndex={-1}` plus click-to-focus composites); if focus lands on the host and never reaches the input, typing does nothing and `bdsFocus` never fires. Forwarding twice is the same defect class as not forwarding: a re-entered handler re-focuses the input mid-interaction.
- **Input that reveals it:** a `focus` event dispatched on the host element itself (`bds-text-field.tsx:423-427`).
- **Observed current behavior:** the `Host` `onFocus` forwarder runs only when `event.target === event.currentTarget && !this.readOnly`, then focuses the first `input` descendant (`bds-text-field.tsx:423-427`).
- **Recommended contract:** focusing the host container forwards focus to the inner input exactly once.
- **Contract status:** confirmed
- **Why it matters:** it is the reason the forwarder exists; the T57 fix must not trade the forward for the recursion guard.
- **Covered by:** `src/components/forms/bds-text-field/__test__/bds-text-field-events.spec.ts::focusing the host container forwards focus to the inner input exactly once`

---

### FM-02 | A bubbling `focus` event from the inner input must not re-enter the forwarder

- **ID:** FM-02
- **Category:** race-timing
- **Risk:** test-only in a real browser (real `focus` does not bubble), but in mock-doc `MockElement.focus()` dispatches `focus` with `bubbles: true`, so an unguarded forwarder re-enters itself from its own `input.focus()` call until `RangeError: Maximum call stack size exceeded` — swallowed and printed by mock-doc's listener `try/catch` (`console.error(err)`), so the suite stays green while leaking 4 stack-overflow lines per date-picker run.
- **Input that reveals it:** a `new Event('focus', { bubbles: true })` dispatched from the inner input after the host received focus; or any real `input.focus()` under `newSpecPage`.
- **Observed current behavior:** the forwarder early-exits unless `event.target === event.currentTarget` (`bds-text-field.tsx:424`), so a bubbled event from the input is ignored. Without that clause the handler re-enters (verified: reverting it makes this row's test fail with 2 forward calls).
- **Recommended contract:** a `focus` event whose target is not the host never triggers forwarding.
- **Contract status:** confirmed
- **Why it matters:** the T57 regression guard — the suite must fail if the target check is removed, since the visible symptom is only console noise.
- **Covered by:** `src/components/forms/bds-text-field/__test__/bds-text-field-events.spec.ts::a focus event bubbling up from the inner input does not forward focus to it again`

---

### FM-03 | `readonly` suppresses container→input forwarding

- **ID:** FM-03
- **Category:** component-contract-bypass
- **Risk:** functional — a read-only field that still accepts focus into its input lets assistive tech and selection state imply the value is editable; the component's own `handleMouseDown` and `tabIndex={-1}` handling already treat `readOnly` as "do not interact".
- **Input that reveals it:** a `focus` event on the host with `readonly` set (`bds-text-field.tsx:425`, prop at `:94`).
- **Observed current behavior:** the `!this.readOnly` clause short-circuits before the `querySelector`/`focus()` call.
- **Recommended contract:** no forwarding when `readOnly` is true.
- **Contract status:** confirmed
- **Why it matters:** the guard is part of the same boolean chain T57 edited; a rewrite that keeps only the target check would silently regress it.
- **Covered by:** `src/components/forms/bds-text-field/__test__/bds-text-field-events.spec.ts::readonly prevents the host container from forwarding focus to the inner input`

---

### FM-04 | Forwarding survives a missing inner input

- **ID:** FM-04
- **Category:** null-empty
- **Risk:** runtime throw — the forwarder runs inside a mock-doc/Stencil event listener; a `TypeError` there is swallowed by mock-doc's `catch` in tests and would surface as an unhandled listener error in a browser if the input were ever absent (e.g. mid-render teardown).
- **Input that reveals it:** a `focus` event on the host while `querySelector('input')` returns `null` (`bds-text-field.tsx:426`).
- **Observed current behavior:** optional chaining (`?.focus()`) makes the call a no-op.
- **Recommended contract:** host focus never throws when no inner input is present.
- **Contract status:** confirmed
- **Why it matters:** keeps the guard chain total; the T57 edit rewrote this line and could have dropped the `?.`.
- **Covered by:** `src/components/forms/bds-text-field/__test__/bds-text-field-events.spec.ts::focusing the host container when no inner input exists does not throw`

---

### PD-01 | Should a `disabled` field forward host focus to its (disabled) input?

- **ID:** PD-01
- **Category:** component-contract-bypass
- **Risk:** behavioural ambiguity only. Browsers refuse to focus a `disabled` input, so the current code's call is a no-op there; under mock-doc it dispatches focus events, which can surprise a test author. The forwarder's boolean chain checks `readOnly` but not `isDisabled`.
- **Input that reveals it:** `root.focus()` on `<bds-text-field disabled="true">` — the forwarder still calls `input.focus()`.
- **Observed current behavior:** `!this.readOnly` is the only guard; `isDisabled` is not consulted (`bds-text-field.tsx:423-427`).
- **Recommended contract:** undecided — either keep relying on the platform no-op (current behavior, zero browser risk, no source change) or add `!this.isDisabled` for symmetry with `!this.readOnly`. Both are defensible; the component has shipped with the former.
- **Contract status:** pending-decision
- **Why it matters:** no user-visible defect found, so no test is written; the row exists so a future rewrite of the guard chain makes a deliberate choice.
- **Covered by:** —
