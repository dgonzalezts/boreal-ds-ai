---
name: Stencil spec page root element pattern
description: Standard pattern for accessing page.root in newSpecPage tests — named variable + explicit cast, never inline repeated casts or optional chaining
type: feedback
---

Always assign `page.root` to a named `root` variable with an explicit type cast. Never access it inline or with optional chaining.

```ts
// ✅ correct
const root = page.root as HTMLElement;
root.classList.contains('bds-button--disabled');

// ❌ avoid
(page.root as HTMLElement).classList.contains('bds-button--disabled');
page.root?.querySelector('button');
```

Use `HTMLElement` for DOM-only access; use the typed element interface (`HTMLBdsRadioGroupElement`) when props or `@Method()` calls are needed.

Query child elements from `root`, not from `page.root` with optional chaining:

```ts
const root = page.root as HTMLElement;
const el = root.querySelector('button');
assertExists(el, 'Button not found'); // only when element must exist
```

For `querySelectorAll` + `Array.from`, never use `?? []` fallback — it masks a missing root via vacuous truth in `every()` assertions.

Runtime prop changes use `(root as any).prop = value` — cast on the assignment, not on the root declaration.

**Why:** Centralises the type assertion, removes repetitive inline cast noise, prevents silent false positives from optional chaining + `?? []`, and matches the established `bds-button-basics.spec.ts` reference pattern.

**How to apply:** Apply to every new or modified Stencil `newSpecPage` spec file in `boreal-web-components`. Canonical reference: `packages/boreal-web-components/src/components/actions/bds-button/__test__/bds-button-basics.spec.ts`.
