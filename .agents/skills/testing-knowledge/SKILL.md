---
name: testing-knowledge
description: Domain knowledge for writing unit tests for Stencil components in Boreal DS. Covers newSpecPage patterns, spec file organisation, FACE test mocks, child component assertions, and the two-phase quality gate (≥ 90% coverage then ≥ 90% mutation score). Load proactively when writing, fixing, or reviewing unit tests.
---

# Testing Knowledge — Boreal DS

Primary references (read before writing tests):

- `ai-docs/guidelines/stencil-unit-testing-patterns.md` — canonical `newSpecPage` patterns, AAA structure, FACE boilerplate, child component assertions
- `ai-docs/guidelines/stencil-best-practices.md` §"FACE Components" — async rendering gotchas relevant to test setup

---

## Quality Gate — Two Phases (Required Order)

1. **Coverage ≥ 90%** — run `pnpm test:spec` from the monorepo root; confirm statement coverage ≥ 90% before proceeding
2. **Mutation score ≥ 90%** — invoke the `mutations-testing` skill; score < 90% requires additional tests targeting surviving mutants before the task is complete

Do not skip or reverse this order. Coverage alone does not prove the tests catch real bugs.

---

## Spec File Organisation

Split tests across up to five files per component: `{bds-component}.{type}.spec.ts`

| File                             | Create when…                                                                                                                                                                                      |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bds-component.a11y.spec.ts`     | Component renders ARIA attributes, roles, or manages focus. Always required for interactive components.                                                                                           |
| `bds-component.basics.spec.ts`   | Component has props, CSS classes, or render output verifiable in isolation. Always required.                                                                                                      |
| `bds-component.variants.spec.ts` | Component has an enum prop (`variant`, `size`, `color`, `type`) that changes rendered output — when not covered by basics.                                                                        |
| `bds-component.events.spec.ts`   | Component emits custom events or reacts to DOM events from child elements.                                                                                                                        |
| `bds-component.slots.spec.ts`    | The slot has testable behaviour beyond what other spec files cover (named slots that change output, `slotchange` handlers, conditional slots). Do NOT create for a bare unnamed passthrough slot. |

Use `.spec.tsx` only when the spec file itself contains JSX.

---

## FACE Test Boilerplate

FACE mocks live in `packages/boreal-web-components/src/utils/testing/mocks/`. Import via `@/utils`.

```typescript
import { attachInternals, suppressConsoleError } from "@/utils";

describe("bds-my-component basics", () => {
  suppressConsoleError(); // call at describe level, not inside beforeAll

  beforeAll(() => {
    attachInternals();
  });

  // tests...
});
```

- `attachInternals()` — polyfills `HTMLElement.prototype.attachInternals`; prevents `newSpecPage` throwing at construction
- `suppressConsoleError()` — silences Stencil mock-doc proxy errors on every `ElementInternals` property access; the spy still tracks calls so `expect(console.error).toHaveBeenCalledWith(...)` works alongside suppression

Apply this pattern in every spec file for a component that uses `formAssociatedMixin` or declares `@AttachInternals()`.

---

## Testing Events That Fire in `componentDidLoad`

`componentDidLoad` runs synchronously inside `newSpecPage()` — listeners attached after `await newSpecPage(...)` miss those events.

```typescript
// ✅ Correct — use page.setContent() after attaching the listener
const page = await newSpecPage({ components: [BdsRadio], html: "" });
const spy = jest.fn();
page.doc.addEventListener("bdsMount", spy);
await page.setContent('<bds-radio label="A"></bds-radio>');
expect(spy).toHaveBeenCalledTimes(1);
```

Always use `page.doc` (not `document`) to stay within the mocked environment.

---

## Child Component Prop Assertions

`getAttribute` on a child component returns `null` unless the prop has `reflect: true`. Most Boreal DS props do not. The correct approach: register the child in `components` and assert on the DOM it renders.

```typescript
const page = await newSpecPage({
  components: [BdsRadioButton, BdsTypography], // register child when asserting its rendered output
  html: `<bds-radio-button info="hint"></bds-radio-button>`,
});
const typography = page.root?.querySelector(
  "bds-typography.bds-radio-button__label",
);
expect(typography?.querySelector(".bds-typography__info-icon")).toBeTruthy();
```

Add a child to `components` only when the test needs to assert on that component's rendered DOM. Do NOT add it if only the presence/absence of the element tag is being checked.

---

## `formDisabledCallback` Test Pattern

`formDisabledCallback` is triggered by `<fieldset disabled>`, not by setting `form.disabled`. In unit tests, set `component.disabled` directly. In integration tests, toggle a `<fieldset disabled>` ancestor.

---

## Accepted Mutation Survivors

Document accepted survivors when a conditional has no observable DOM consequence (e.g. `tooltipText={this.info !== '' ? this.info : undefined}` where both `''` and `undefined` are falsy in the child guard). Record the survivor in the relevant spec file as a comment and in the task notes.
