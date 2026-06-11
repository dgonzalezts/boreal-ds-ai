# Stencil Unit Testing Patterns

Standard patterns for `newSpecPage` spec files in `boreal-web-components`. All examples reference `bds-button-basics.spec.ts` as the canonical source.

**Coverage target:** every component must reach ≥ 90% statement coverage before a PR is merged.

---

## Spec file organisation

### File naming

Split each component's tests across up to five spec files — one per functional concern. The naming convention is `{bds-component}.{type}.spec.ts`:

| File                             | Create when…                                                                                                                             |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `bds-component.a11y.spec.ts`     | Component renders ARIA attributes, roles, or manages focus. Always required for interactive components.                                  |
| `bds-component.basics.spec.ts`   | Component has props, CSS classes, or render output that can be verified in isolation. Always required.                                   |
| `bds-component.variants.spec.ts` | Component has a `variant`, `size`, `color`, or equivalent enum prop that changes rendered output — when not already covered by `basics`. |
| `bds-component.events.spec.ts`   | Component emits custom events or reacts to DOM events from child elements.                                                               |
| `bds-component.slots.spec.ts`    | The slot has testable behaviour beyond what other spec files cover (see criteria below).                                                 |

**When to create `slots.spec.ts`** — create the file only when at least one of these is true:

1. The component has **named slots** and their presence or absence changes rendered output or component state.
2. A `slotchange` handler updates component state or the DOM in a way that can be independently asserted.
3. A slot renders **conditionally** based on props (e.g. shown only when a certain prop is set).

**Do not create** `slots.spec.ts` for a bare unnamed passthrough slot (`<slot />`) whose only side-effect is a CSS layout variable (e.g. `--layout-count`). That slot is already exercised incidentally by any test that passes child elements, and the CSS variable has no observable behaviour to assert.

Use `.spec.tsx` instead of `.spec.ts` only when the spec file itself uses JSX syntax.

> `bds-button` uses the legacy hyphen form (`bds-button-basics.spec.ts`) — that predates this convention. All components added after `bds-button-group` follow the dot form.

### Describe and it structure

- One `describe` block per spec file, named after the component: `describe('bds-toggle basics', () => { ... })`.
- One `it` per distinct behaviour — not per line of code.
- Test descriptions must read as specifications, not labels:

```ts
// ✅ reads as a specification
it('renders as disabled when the disabled prop is true', async () => { ... });

// ❌ too vague
it('disabled test', async () => { ... });
```

---

## Test structure: Arrange-Act-Assert

Use the AAA pattern in every `it` block. Three labelled comments keep the phases visually distinct, making it immediately obvious which phase failed when a test breaks.

```ts
it("should emit bdsChange when value changes", async () => {
  // Arrange
  const page = await newSpecPage({
    components: [BdsTextField],
    html: `<bds-text-field></bds-text-field>`,
  });
  const root = page.root as HTMLBdsTextFieldElement;
  const spy = jest.fn();
  root.addEventListener("bdsChange", spy);

  // Act
  (root as any).value = "hello";
  await page.waitForChanges();

  // Assert
  expect(spy).toHaveBeenCalledTimes(1);
  expect(spy).toHaveBeenCalledWith(
    expect.objectContaining({ detail: "hello" }),
  );
});
```

Omit the phase comments only when the test is trivially short — a single assertion on a static default, for example.

---

## Root element access

Always assign `page.root` to a named variable with an explicit cast. Never access `page.root` inline with repeated casts.

```ts
// ✅ correct
const root = page.root as HTMLElement;
expect(root.classList.contains("bds-button--disabled")).toBe(true);

// ❌ avoid
expect(
  (page.root as HTMLElement).classList.contains("bds-button--disabled"),
).toBe(true);
```

Use `HTMLElement` when you only need DOM access. Use the specific element interface when you need typed props or methods.

```ts
// typed access to component props and @Method()
const root = page.root as HTMLBdsRadioGroupElement;
root.value = "b";
const valid = await root.checkValidity();
```

---

## Querying child elements

Query from `root`, never from `page.root` with optional chaining.

```ts
// ✅ correct
const root = page.root as HTMLElement;
const button = root.querySelector("button");
assertExists(button, "Button element not found");
expect(button.getAttribute("type")).toBe("reset");

// ❌ avoid
const button = page.root?.querySelector("button");
assertExists(button, "Button element not found");
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
const dividers = Array.from(
  root.querySelectorAll("bds-divider[data-injected]"),
);
expect(dividers.length).toBe(2);

// ❌ avoid — silent false positive if root is undefined
const dividers = Array.from(
  page.root?.querySelectorAll("bds-divider[data-injected]") ?? [],
);
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
expect(root.querySelectorAll("bds-divider[data-injected]").length).toBe(2);

(root as any).joined = true;
await page.waitForChanges();

expect(root.querySelectorAll("bds-divider[data-injected]").length).toBe(0);
```

---

## assertExists usage

Use `assertExists` from `@/utils` on any queried element that **must** exist for the test assertion to be meaningful. Do not use it on `page.root` itself — the root cast handles that.

```ts
import { assertExists } from "@/utils";

const root = page.root as HTMLElement;
const typography = root.querySelector('bds-typography[variant="label"]');
assertExists(typography, "Label typography element not found");
expect(typography.textContent).toBe("My Group");
```

---

## Required spec file boilerplate (FACE components)

Browser API test doubles for FACE components live in:

```
packages/boreal-web-components/src/utils/testing/mocks/
```

The `mocks/` folder holds test doubles that replace real browser or runtime APIs. The `helpers/` folder holds assertion utilities and DOM query helpers. All mocks are re-exported through `src/utils/testing/index.ts` → `src/utils/index.ts`. Import via `@/utils`.

**Required exports from `mocks/elementInternals.ts`:**

- `attachInternals()` — polyfills `HTMLElement.prototype.attachInternals` so `newSpecPage` does not throw when a FACE component calls `@AttachInternals()` at construction. Call inside `beforeAll`.
- `suppressConsoleError()` — installs a `jest.spyOn(console, 'error').mockImplementation(() => {})` in `beforeEach` and restores in `afterEach`. Stencil's mock-doc logs `console.error` on every `ElementInternals` property access via a Proxy getter before any optional-chain can prevent it. Suppressing the output is the only viable approach. The spy still tracks calls, so `expect(console.error).toHaveBeenCalledWith(...)` assertions work alongside suppression.

Do not inline FACE mocks inside individual spec files.

```ts
import { newSpecPage } from "@stencil/core/testing";
import { BdsMyComponent } from "../bds-my-component";
import { assertExists, attachInternals, suppressConsoleError } from "@/utils";

describe("bds-my-component basics", () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  // tests ...
});
```

---

## Child Component Prop Assertions

When a child custom element is **not** listed in the `components` array of `newSpecPage`, Stencil treats it as an unknown HTML element and sets JSX props as JavaScript properties — not HTML attributes. `getAttribute` returns `null` even if the prop is set.

Even when the child IS registered, `@Prop()` values are not reflected to HTML attributes unless the prop has `reflect: true`. Most Boreal DS props do not have `reflect: true`, so `getAttribute` returns `null` in both cases.

**The correct pattern: assert on the DOM the child renders, not its prop values.**

Register the child component and assert on the DOM it produces:

```typescript
const page = await newSpecPage({
  components: [BdsRadioButton, BdsTypography], // ✅ child registered
  html: `<bds-radio-button info="hint"></bds-radio-button>`,
});
const typography = page.root?.querySelector(
  "bds-typography.bds-radio-button__label",
);

// Assert on what bds-typography renders when tooltipText is set
expect(typography?.querySelector(".bds-typography__info-icon")).toBeTruthy(); // ✅
```

**When to add a child to `components`:**

- The test needs to assert on the child's rendered DOM output (classes, child elements, ARIA attributes produced by its render function).
- Or it needs the child's props to reflect properly to attributes.

Do NOT add it if only presence/absence of the element tag is being asserted — unknown elements render fine for tag-name queries.

**Accepted survivors:** If a conditional `tooltipText` prop has no visible DOM consequence (because the default empty string and `undefined` are both falsy in the child's guard), surviving Stryker mutants in that conditional should be documented and accepted.
