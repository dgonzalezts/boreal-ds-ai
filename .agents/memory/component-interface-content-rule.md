---
name: Component Interface Content Rule
description: IComponent.ts interfaces contain only consumer-settable @Prop() members — @Event() outputs, group-propagated props, and internal props are excluded
type: feedback
---

`IComponent.ts` interfaces describe only what the **consumer configures** — the set of publicly settable `@Prop()` members.

The following are NOT part of the interface:

- **`@Event()` outputs** (`EventEmitter<T>` members) — these are declared on the component class body and documented via JSDoc. Putting them in the interface would force the type to reference `EventEmitter<T>`, which is an internal output abstraction consumers never set.
- **Group-propagated props** — props that the parent group component writes imperatively (e.g. `name`, `showDivider`, `isFirst`) are implementation details of the parent-child coordination pattern. Consumers set `name` on `<bds-radio-group>`, not on individual `<bds-radio>` children.
- **`@State()` mirrors** — internal reactive state (`isDisabled`, `isOpen`, etc.) is never part of the public API.

**Why:** Interfaces serve as the contract for what the consumer configures when authoring HTML or using the Vue/React wrapper. Keeping them prop-only makes the interface a reliable, minimal API surface that matches prop tables in MDX documentation.

**Example — correct:**

```typescript
export interface IRadioButton {
  value: string;
  label: string;
  info: string;
  checked: boolean;
  disabled: boolean;
  error: boolean;
}
```

**How to apply:** When writing a new `IComponent.ts`, start from the Storybook prop table: if a consumer would set it in HTML or via a framework prop binding, it belongs in the interface. If it is an output or group-internal concern, it stays on the class body only.

## Interface Members Must Be Optional When the Prop Has a Default

If the component assigns a default value to a prop, the consumer never has to pass it — so the interface must declare it as optional (`?`). A required interface member implies the consumer **must** always supply the value explicitly.

```typescript
// ✅ Correct — all props with component-side defaults are optional in the interface
export interface IRadioGroup {
  name: string; // no default on the component — required
  value?: string; // default = ''
  disabled?: boolean; // default = false
  orientation?: Orientation; // default = 'vertical'
}

// ❌ Wrong — disabled has a default of false, marking it required is misleading
export interface IRadioGroup {
  name: string;
  disabled: boolean; // component defaults to false; consumer need not set it
}
```

This also matters for booleans specifically: if the interface declares `disabled: boolean` (required), the React wrapper will type the prop as `boolean`, forcing consumers to write `disabled={false}` explicitly. With `disabled?: boolean`, the prop is truly optional and the bare-attribute pattern (`<bds-radio-group disabled>`) works as expected.
