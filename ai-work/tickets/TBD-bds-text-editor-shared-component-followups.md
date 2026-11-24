# Follow-up ticket from EOA-18739 — shared-component defects and decisions

**Ticket:** TBD (draft, not in Jira; rename this file with the ID once created)
**Source plan:** `ai-work/plans/EOA-18739-bds-text-editor-v1.md` (tasks T12, T14, T15, T17, T18, T19, T20)
**Suggested project:** EOA · type: Task · components: `bds-button`, `bds-popover`, `bds-dropdown`, `bds-button-group`, `bds-toolbar`, shared `useFormField`

**Status (2026-11-24):** open — nothing in this file was fixed by the EOA-18739 merge (`55cb2f08` on `release/current`).
**Overlaps:** §3 re-enables the link popover arrow in `bds-text-editor` once fixed (remove `LINK_POPOVER_OPTIONS`). §4 and §5 share the keyboard handling of `bds-button-group` and `bds-toolbar`; decide them together. §6 is why the editor builds its toolbar group per render (`group-${index}-${tools}` keys).

## Jira fields (copy when creating)

- **Summary:** Shared components: fix defects found while building `bds-text-editor`
- **Type:** Task (umbrella; split into sub-tasks or separate tickets when picked up)
- **Links:** found during EOA-18739 (v1); related to EOA-21589 (v2)

## Summary

Pre-existing defects and open decisions in shared components, found while building and testing `bds-text-editor` v1. None is caused by the editor. Each item has its own acceptance criteria and can be picked up alone. §4 was planned for the next sprint (2026-11-20) and may be better as its own ticket.

## 1. Localizable validation messages across form components (was v1 T12)

`valueMissing` and `tooLong` messages in `bds-text-editor`, `bds-text-field`, `bds-color-picker`, `bds-date-picker` and `bds-file-picker` are English literals. Consumers localize them today through `errorMessage`.

- **Needs an ADR first:** placeholder syntax for `tooLong` (`{max}`) and plurals are not covered by ADR 0014. The v2 plan proposes ADR 0025 for strings with numbers or plurals; settle both together.
- **AC:** ADR accepted; then per-component work in its own plan.
- Effort: large (cross-cutting). Priority: medium.

## 2. `bds-button` accessible name and empty text (was v1 T14)

- With `experimentalSlotFixes`, `hasSlotContent(this.el)` in `componentWillLoad` is empty for default-slot text, so a text-only `bds-button` warns "No accessible name found".
- `bds-button` does not re-detect removed slot text, so the `--is-empty` class stays off. Visible effect in the editor: switching `fieldsButton` back to `icon` at runtime leaves the Fields trigger about 8px wider. `--is-empty` is only ever turned off from `handleTextSlotChange`, which does not fire when the text is removed.
- **AC:** no warning for a text-only button; removing the text restores `--is-empty`; specs for both.
- Effort: small. Priority: medium.

## 3. `bds-popover` arrow position (was v1 T15)

`bds-popover.setArrowPosition` hardcodes `left: 20px` for `top-start` and `bottom-start`, ignoring the trigger-centred `arrowData.x` from floating-ui. The editor's link popover hides its arrow because of this (`floatingOptions={ hideArrow: true }`).

- **Recommended:** use `arrowData.x` with only a minimum inset from the corner. Own commit, specs, stories and QA for every `top-start` and `bottom-start` popover.
- **Alternative (editor only):** `placement="bottom"`; the 320px popover overhangs the small button on both sides.
- `floatingOptions.offset` is a distance only, so it cannot align the arrow.
- **AC:** the arrow points at the centre of the trigger for every start placement; decide with design whether the link popover shows an arrow, then re-enable it in the editor.
- Effort: medium. Priority: low.

## 4. Dropdown menu keys leak to ancestor roving handlers (was v1 T18)

Pre-existing; reproduces on the EOA-20193 base (`4774509f`) in Chromium, WebKit and Firefox.

- **A.** With a `bds-dropdown` menu open, ArrowLeft, ArrowRight, Home and End close the menu and move focus to a `bds-button-group` or `bds-toolbar` button. This also happens with a dropdown directly in a `bds-toolbar`, with no group. Cause: the container's roving handler is bound on the host in the bubble phase with no check on the event target, and the dropdown does not stop these keys; with focus on a menu item the index lookup fails and focus moves anyway. Proposed fix: bind the menu keys in `bds-dropdown.tsx` and stop propagation for keys whose target is inside the list (the `stopPropagation` option on the dropdown's own bindings is untested).
- **B.** In a vertical `bds-button-group`, ArrowDown and ArrowUp on the dropdown trigger open the menu and the group then moves focus away: the menu ends closed in Chromium and WebKit and open in Firefox. Arrow navigation inside the menu is also taken by the group. Enter, Space and Tab still work. Needs a design decision (for example, the dropdown does not open on Up and Down inside a vertical group).
- **Evidence:** manual scenarios BG-01 to BG-07 (temporary playground section, no longer on `release/current`); agent memory notes `bds-button-group-dropdown-keyboard-hijack` and `base-vs-head-worktree-build-pnpm-symlink-hazard`.
- **AC:** with a menu open, none of the four keys moves focus out of it, in all three browsers; a decision recorded for B.
- Effort: medium. Priority: high (keyboard accessibility defect).

## 5. `bds-toolbar` Tab-stop model (was v1 T20)

In `bds-toolbar`, every tool is its own Tab stop until the first arrow key is used; afterwards the toolbar is a single Tab stop at the tool last reached. The editor docs describe the real behaviour (`2e13b6d1`). A single Tab stop with roving tabindex from the start is the usual toolbar pattern.

- **AC:** intended model decided, fixed in the shared `bds-toolbar`, specs, and the editor docs updated if the behaviour changes.
- Effort: small to medium. Priority: medium.

## 6. `bds-button-group` ignores children added after load (was v1 T19)

Validation, prop propagation and roving setup run once in `componentDidLoad`. A `bds-button` or `bds-dropdown` appended later gets no `size`, `color` or `variant` from the group, is an extra Tab stop (no roving `tabindex`), and a late wrapped child gets no warning. The button-group MDX describes the prop limitation ("Group children").

- **Proposed fix:** a `MutationObserver` or `slotchange` handler in `bds-button-group.tsx` that re-runs the three steps.
- **AC:** a child appended after load receives the group props, joins the roving order and warns when wrapped; specs; the MDX limitation note removed.
- Effort: small to medium. Priority: low.

## 7. Focus on `reportValidity()` and blocked submit (was v1 T17)

Native `reportValidity()` and a blocked submit flag the editor but leave focus where it was. `bds-text-field` behaves the same way in Chromium, so a fix belongs in the shared `useFormField` and affects every form component.

- **AC:** decide whether the first invalid control takes focus; if yes, implement it in `useFormField` with specs for every form component that uses it, and a real `<form>` submit check in Chromium, WebKit and Firefox.
- Effort: medium. Priority: medium (affects every form component).
