# Storybook — Source Snippet Override for Non-Primitive Props

## The Problem

When a story uses Lit property binding (`.propName=${value}`) to set a **non-primitive** prop (array, object), the generated "Show code" snippet is incomplete or misleading.

**Why this happens:**

- Lit property bindings (`.value=${['a', 'b']}`) set a DOM **property**, not an HTML attribute
- Non-primitive values cannot be serialized as HTML attributes
- Storybook's source extractor only sees the serialized DOM — it cannot reconstruct the JS property assignment

**Result:** The auto-generated snippet shows only the markup, omitting the critical property assignment that makes the story work.

## When This Occurs

This pattern is required when:

1. A `@Prop()` has **no** `reflect: true` (the value never appears in the DOM as an attribute)
2. The prop type is **non-primitive** (array, object, function) — these cannot be reflected even if `reflect: true` were added
3. The story uses Lit property binding (`.propName=${...}`) rather than attribute binding

**Confirmed case:** `bds-checkbox-group` with `@Prop({ mutable: true }) value: string[] = []` — arrays cannot be serialized as attributes, and the prop does not reflect.

## The Fix

Override the auto-generated snippet using `parameters.docs.source.code` with a **manual HTML + `<script>` block** showing both the markup and the JS property assignment:

```typescript
export const WithValue: BorealStory = {
  args: {
    value: ["Option-A", "Option-C"], // Storybook control
  },
  render: (args) => html`
    <bds-checkbox-group .value=${args.value}>
      <bds-checkbox-button value="Option-A">Option A</bds-checkbox-button>
      <bds-checkbox-button value="Option-B">Option B</bds-checkbox-button>
      <bds-checkbox-button value="Option-C">Option C</bds-checkbox-button>
    </bds-checkbox-group>
  `,
  parameters: {
    docs: {
      source: {
        code: `<bds-checkbox-group id="my-group">
  <bds-checkbox-button value="Option-A">Option A</bds-checkbox-button>
  <bds-checkbox-button value="Option-B">Option B</bds-checkbox-button>
  <bds-checkbox-button value="Option-C">Option C</bds-checkbox-button>
</bds-checkbox-group>

<script>
  const group = document.querySelector('#my-group');
  group.value = ['Option-A', 'Option-C'];
</script>`,
      },
    },
  },
};
```

## Pattern Summary

1. Add a unique `id` to the component in the manual snippet
2. Show the complete markup structure
3. Include a `<script>` block demonstrating the property assignment via DOM API
4. Use descriptive variable names (`group`, `field`, `select`) that match the component type

## When NOT to Override

If the prop **does** reflect (`reflect: true`) **and** is primitive (string, number, boolean), the auto-generated snippet will be correct — no override needed.

## Cross-Reference

See `stencil-child-component-props-in-tests.md` for the test-side equivalent: JSX props on unregistered child components are set as JS properties, not HTML attributes.
