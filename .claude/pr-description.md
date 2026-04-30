# PR Title

feat(web-components): EOA-12334 add bds-radio leaf component

---

# PR Body

Adds `bds-radio`, the private building-block element that `bds-radio-group` will compose. Also defines the `IRadio` and `IRadioGroup` TypeScript interfaces.

`bds-radio` is intentionally not form-associated and carries no Storybook entry — it fires `bdsMount` (bubbling) on load so the parent group can register it without imperative DOM queries, and `bdsChange` (bubbling) on selection so the group can enforce single selection. For a single binary choice, consumers should use `bds-checkbox` instead.

The hidden native `<input type="radio" aria-hidden>` exists solely so FormData picks up the name/value pair when the element is used inside a plain `<form>` outside a group. ARIA `role="radio"` and `aria-checked` are stamped in `componentDidLoad`; Space key selection is wired alongside click handling.

`bds-radio-group` (the public FACE orchestrator, keyboard navigation, Vue v-model registration, and Storybook docs) lands in a follow-up PR. `IRadioGroup.ts` is committed here so the interface is in place when the group is implemented.

Refs EOA-12334
