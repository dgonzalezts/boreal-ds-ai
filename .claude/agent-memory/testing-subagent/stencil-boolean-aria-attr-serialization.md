# Stencil serializes boolean ARIA attrs as empty-string / omits them, not "true"/"false"

When a component renders `aria-selected={someBoolean}` (a plain JSX boolean attribute, not a
string-valued one like `aria-current={cond ? 'date' : undefined}`), Stencil's `setAccessor`
(`update-element.ts` in `@stencil/core/internal/{testing,client}`) treats it like any other
boolean attribute (same code path as `disabled`):

- `true` → `elm.setAttribute('aria-selected', '')` — attribute present with an **empty string**
  value, not `"true"`.
- `false` → the attribute is **removed entirely** (`elm.removeAttribute(...)`), not set to
  `"false"`.

Confirmed on `bds-calendar-grid`'s `aria-selected={cell.isoDate === this.selectedDate}`
(EOA-16692 Task 11). Asserting `getAttribute('aria-selected')).toBe('true')` fails with
`Received: ""`.

**Correct test pattern:** assert presence/absence, not string value:

```typescript
expect(selectedCell.hasAttribute('aria-selected')).toBe(true);
expect(otherCell.hasAttribute('aria-selected')).toBe(false);
```

This differs from a string-valued conditional attribute (e.g. `aria-current={isToday ? 'date' :
undefined}`), which renders normally as `aria-current="date"` / attribute absent — `getAttribute`
comparisons work fine there.

Note this is arguably a real ARIA authoring bug in the component (`aria-selected=""` is not a
valid `true`/`false` ARIA value per spec) — but it's the framework's actual runtime behavior for
a boolean JSX prop bound to an `aria-*` attribute name, not a test bug. Fixing it would require
the component to explicitly stringify (`aria-selected={String(cond)}`), which is a component-code
change, out of scope for a test-only task. Flag it to the component's implementer rather than
silently working around it if this behavior is caught again on another component's a11y tests.
