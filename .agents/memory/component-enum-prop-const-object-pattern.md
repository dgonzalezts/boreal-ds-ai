---
name: component-enum-prop-const-object-pattern
description: String-literal-union props belong in types/enum.ts as a const object + derived type, paired with validatePropValue — never an inline union on the @Prop() line
---

Any `@Prop()` whose type is a closed set of string literals (a "variant"/"size"/"type" prop) must be declared in that component's `types/enum.ts` as a `const`-object + derived type, not inline on the `@Prop()` declaration.

```typescript
// types/enum.ts
export const CALENDAR_TYPE = {
  DEFAULT: 'default',
  BASIC: 'basic',
  EXPANDED: 'expanded',
} as const;

export type CalendarType = (typeof CALENDAR_TYPE)[keyof typeof CALENDAR_TYPE];
```

```typescript
// component.tsx
@Prop() readonly calendarType: CalendarType = CALENDAR_TYPE.BASIC;

componentWillLoad() {
  validatePropValue(Object.values(CALENDAR_TYPE), CALENDAR_TYPE.BASIC, this.el as HTMLElement, 'calendarType');
}
```

Confirmed across 14+ components (`bds-dialog`'s `DIALOG_SIZES`/`DIALOG_VARIANT`/`DIALOG_LAYOUT`, `bds-popover`'s `POPOVER_TRIGGER_MODE`/`POPOVER_WIDTH`/`POPOVER_ROLE`, `bds-text-field`, `bds-slider`, `bds-tab-group`, etc.) — one `enum.ts` per component holding every such const for that component, not one file per enum.

**Why the const-object pairs with `validatePropValue`:** an inline TS union (`'default' | 'basic' | 'expanded'`) has no runtime representation — a consumer setting the attribute via plain HTML/JS with a typo gets no warning. `Object.values(CONST)` is the runtime source of truth `validatePropValue` (from `@/utils`) checks against in `componentWillLoad`, falling back to a default value and `console.warn`-ing on an invalid value. Skipping the const-object form means silently skipping this validation too.

**JSDoc on the const object is allowed when values need explanation** (see `bds-popover`'s `POPOVER_ROLE`) — this is an exception to the general "no JSDoc on type/interface files" rule (`feedback_no_jsdoc_types_interfaces.md`), which is about plain field-listing interfaces (`IComponent.ts`), not enum value documentation.

**Source:** `bds-date-picker`'s `calendarType` prop (EOA-17138) initially shipped as an inline union; caught in review, moved to `CALENDAR_TYPE`/`CalendarType` in the component's existing `types/enum.ts` alongside `FOOTER_ACTION`/`FooterAction`.
