# Stencil Unit Testing Patterns

Standard patterns for `newSpecPage` spec files in `boreal-web-components`. All examples reference `bds-button-basics.spec.ts` as the canonical source.

---

## Root element access

Always assign `page.root` to a named variable with an explicit cast. Never access `page.root` inline with repeated casts.

```ts
// ✅ correct
const root = page.root as HTMLElement;
expect(root.classList.contains('bds-button--disabled')).toBe(true);

// ❌ avoid
expect((page.root as HTMLElement).classList.contains('bds-button--disabled')).toBe(true);
```

Use `HTMLElement` when you only need DOM access. Use the specific element interface when you need typed props or methods.

```ts
// typed access to component props and @Method()
const root = page.root as HTMLBdsRadioGroupElement;
root.value = 'b';
const valid = await root.checkValidity();
```

---

## Querying child elements

Query from `root`, never from `page.root` with optional chaining.

```ts
// ✅ correct
const root = page.root as HTMLElement;
const button = root.querySelector('button');
assertExists(button, 'Button element not found');
expect(button.getAttribute('type')).toBe('reset');

// ❌ avoid
const button = page.root?.querySelector('button');
assertExists(button, 'Button element not found');
```

For negative assertions (element must not exist), no `assertExists` is needed.

```ts
const root = page.root as HTMLElement;
expect(root.querySelector('bds-typography[variant="label"]')).toBeFalsy();
```

---

## QuerySelectorAll and Array.from

Query from `root` directly — no `?? []` fallback needed once `root` is typed.

```ts
// ✅ correct
const root = page.root as HTMLElement;
const dividers = Array.from(root.querySelectorAll('bds-divider[data-injected]'));
expect(dividers.length).toBe(2);

// ❌ avoid — silent false positive if root is undefined
const dividers = Array.from(page.root?.querySelectorAll('bds-divider[data-injected]') ?? []);
```

> `Array.prototype.every()` on an empty array returns `true` (vacuous truth). The `?? []` fallback can mask a missing root by silently passing orientation or count assertions.

---

## Dual-page tests

When a test spins up two spec pages to compare states, assign each root to a descriptively named variable.

```ts
const pageWithLabel = await newSpecPage({ ... });
const rootWithLabel = pageWithLabel.root as HTMLElement;
expect(rootWithLabel.getAttribute('aria-labelledby')).toBeTruthy();

const pageWithoutLabel = await newSpecPage({ ... });
const rootWithoutLabel = pageWithoutLabel.root as HTMLElement;
expect(rootWithoutLabel.getAttribute('aria-labelledby')).toBeNull();
```

---

## Runtime prop mutation

Use `(root as any).prop = value` to trigger `@Watch()` handlers in runtime tests. The `as any` cast stays on the individual assignment, not on the root declaration.

```ts
const root = page.root as HTMLElement;
expect(root.querySelectorAll('bds-divider[data-injected]').length).toBe(2);

(root as any).joined = true;
await page.waitForChanges();

expect(root.querySelectorAll('bds-divider[data-injected]').length).toBe(0);
```

---

## assertExists usage

Use `assertExists` from `@/utils` on any queried element that **must** exist for the test assertion to be meaningful. Do not use it on `page.root` itself — the root cast handles that.

```ts
import { assertExists } from '@/utils';

const root = page.root as HTMLElement;
const typography = root.querySelector('bds-typography[variant="label"]');
assertExists(typography, 'Label typography element not found');
expect(typography.textContent).toBe('My Group');
```

---

## Required spec file boilerplate (FACE components)

```ts
import { newSpecPage } from '@stencil/core/testing';
import { BdsMyComponent } from '../bds-my-component';
import { assertExists, attachInternals, suppressConsoleError } from '@/utils';

describe('bds-my-component basics', () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  // tests ...
});
```
