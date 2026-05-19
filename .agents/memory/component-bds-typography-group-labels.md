# bds-typography for Group-Level Labels and Helper Text

Group components (e.g. `bds-radio-group`) that own a `label` and `helperText` must render them via `<bds-typography>`, not plain `<span>` elements.

**Why:** `bds-typography` variant `label` provides a required indicator (`*`) and a tooltip icon out of the box. variant `helper` handles error/disabled state coloring via its `state` prop — no custom SCSS needed.

**Full pattern (aligned with `bds-text-field`):**

```tsx
render() {
  const labelId = `${this._id}-label`;
  const helperId = `${this._id}-helper`;
  const typographyState = this.disabled ? 'disabled' : this.error ? 'error' : 'default';

  return (
    <Host
      aria-labelledby={this.label ? labelId : undefined}
      aria-describedby={this.helperText ? helperId : undefined}
    >
      {this.label && (
        <bds-typography
          id={labelId}
          variant="label"
          state={typographyState}
          required={this.required}
          tooltipText={this.info !== '' ? this.info : undefined}
        >
          {this.label}
        </bds-typography>
      )}
      {/* options slot */}
      {this.helperText && (
        <bds-typography id={helperId} variant="helper" state={typographyState}>
          {this.helperText}
        </bds-typography>
      )}
    </Host>
  );
}
```

**Key details:**
- `private readonly _id = createId('bds-radio-group');` — unique ID per instance, never hardcoded
- Tooltip prop at the API level is named `info` (matches `bds-text-field`); mapped to `tooltipText` on `bds-typography` with an empty-string guard: `tooltipText={this.info !== '' ? this.info : undefined}`
- `state` is computed once as `typographyState` and passed to **both** label and helper typography elements
- `aria-describedby` only set when `helperText` is non-empty
- `aria-labelledby` only set when `label` is non-empty
- Use camelCase `tooltipText` on `bds-typography` (JSX prop), not kebab-case `tooltip-text`

**Consequences:**
- Add `info: string` to the group component's interface and as a `@Prop()` — **not** `tooltipText`
- Import `createId` from `@/utils`
- Drop `.group__label` and `.group__helper` SCSS rules — `bds-typography` handles all token application internally
- Add `BdsTypography` to the `components` array in every spec file that tests the group

**Individual leaf labels** (e.g. `bds-radio`, `bds-checkbox`) stay as plain `<span>` — only group-level labels use `bds-typography`. Confirmed: `bds-checkbox` uses `<span class="bds-checkbox__label">`.

Source: EOA-12334 radio Figma review (node 211:20862); pattern confirmed by `bds-text-field.tsx`.
