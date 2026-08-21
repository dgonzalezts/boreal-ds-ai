---
name: testing-knowledge
description: Domain knowledge for writing unit tests for Stencil components in Boreal DS. Covers newSpecPage patterns, spec file organisation, FACE test mocks, child component assertions, and the two-phase quality gate (≥ 90% coverage then ≥ 90% mutation score). Load proactively when writing, fixing, or reviewing unit tests.
---

# Testing Knowledge — Boreal DS

## Primary Reference

[`ai-docs/guidelines/development-standards.md`](../../../ai-docs/guidelines/development-standards.md) is the project's primary rules document. Read the sections relevant to your task before starting. This skill provides scope-specific patterns and gotchas that complement — not replace — those rules.

**Directional rule:** procedures and patterns (how to write a test, how to structure spec files) → live here. Rules, rationale, and constraints (component API contracts, event emission rules) → live in `development-standards.md`.

Also read before writing tests:

- `ai-docs/guidelines/stencil-unit-testing-patterns.md` — canonical `newSpecPage` patterns, AAA structure, FACE boilerplate, child component assertions
- `ai-docs/guidelines/stencil-best-practices.md` §"FACE Components" — async rendering gotchas relevant to test setup

**No inline comments in spec files.** The project's no-inline-comments rule (`.agents/CLAUDE.md` "Non-Negotiable Rules") applies to spec files exactly as it does to any other source file — there is no test-file carve-out. A test's own `describe`/`it` names and assertions must carry all the meaning a `//` comment would otherwise supply; if a name can't carry it, rewrite the name. The only sanctioned exception is accepted mutation survivor rationale, and even that does not get written as a spec-file comment — it goes in the component's mutation report instead (see "Accepted Mutation Survivors" below).

---

## Quality Gate — Two Phases (Required Order)

1. **Coverage ≥ 90%** — run `pnpm test:coverage` from the monorepo root; confirm statement coverage ≥ 90% before proceeding
2. **Mutation score ≥ 90%** — invoke the `mutations-testing` skill; score < 90% requires additional tests targeting surviving mutants before the task is complete

Do not skip or reverse this order. Coverage alone does not prove the tests catch real bugs.

---

## Running the Spec Suite Scoped to One Component

Full rationale and verified failure modes: `.agents/memory/stencil-scoped-test-invocation.md`. Summary:

- Use a bare positional path, not `--testPathPattern` — Stencil's CLI wrapper mangles that flag into a matches-almost-everything character-class regex.
- Pass `--collectCoverageFrom` explicitly with a `**/*.tsx` glob matching all component source files, or the coverage % is computed against the project-wide default and looks misleadingly low.
- Use `pnpm --filter <package> run <script>` from the repo root, not `cd <package> && ...` — `with-node.sh` resets cwd to repo root internally, so a preceding `cd` has no effect.
- Pass `--coverageReporters` **twice** (e.g. `--coverageReporters=text --coverageReporters=text-summary`) — Stencil parses a single value as string, Jest needs array; single flag causes `coverageReporters.forEach is not a function`.

```bash
.agents/scripts/with-node.sh pnpm --filter boreal-web-components run test:coverage -- \
  src/components/overlays/bds-tooltip \
  --collectCoverageFrom="src/components/overlays/bds-tooltip/**/*.tsx" \
  --coverageReporters=text --coverageReporters=text-summary
```

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

## Suppressing Console Noise Across Sibling Spec Files

`suppressConsoleWarn()` (same file as `suppressConsoleError()`, `src/utils/testing/mocks/console.ts`) silences `console.warn` for the enclosing `describe` block via `beforeEach`/`afterEach` spies. Call it if the component under test can trigger `console.warn` during normal test execution — most commonly:

- Stencil's dev-mode "Prop `X` is immutable but was modified from within the component" warning
- This project's `Logger.warn` fallback path

```typescript
import { suppressConsoleWarn } from "@/utils";

describe("bds-my-component basics", () => {
  suppressConsoleWarn();
  // tests...
});
```

**Convention: check sibling spec files before adding a new one.** When a component's `__test__/` directory already has spec files calling `suppressConsoleWarn()`/`suppressConsoleError()`, any new spec file added for that component must call the same hook — the warning is triggered by the component itself, not the specific spec file, so a new file omitting it leaks console noise even though the convention is established next to it. No lint/CI check catches this; verify by grepping the target `__test__/` directory for `suppressConsole` before writing a new spec file.

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

## Accessing Internal (Non-`@Prop`) Members for Precise Mutant Killing

Plain class getters/methods (not decorated with `@Prop()`/`@Method()`, e.g. an internal `options`/`hooks` getter, or a `private` method) aren't part of the custom element's public API type, but TypeScript's `private` is compile-time only — the member still exists at runtime. `newSpecPage()` returns `rootInstance`, the actual class instance, which is the correct way to reach these members directly instead of routing through DOM events and `waitForChanges()` timing:

```typescript
const page = await newSpecPage({ components: [BdsTooltip], html: "..." });
const instance = page.rootInstance as unknown as {
  hooks: AnchoredHooks;
  subscribe: (trigger?: HTMLElement) => void;
};
instance.hooks.onPositionUpdate(positioningResult); // call directly — no async positioning engine involved
expect(() => instance.subscribe(undefined)).not.toThrow(); // exercise a guard clause directly
```

This is the established pattern for testing internals (see `bds-popover-methods.spec.ts`'s `(instance as unknown as { listenTarget: HTMLElement }).listenTarget`). Prefer it over triggering a real `mouseenter`/`autoUpdate` cycle when the code under test doesn't otherwise depend on the DOM event pipeline — it's deterministic and avoids depending on whether an async positioning library actually resolves inside `waitForChanges()`.

**Watch for placeholder objects that silently pass validation but don't exercise a guard.** When testing an optional-chaining or `undefined`-check mutant, use an actual `undefined`/missing value, not a mostly-empty object — `{}` and `undefined` both read as "falsy" downstream but only `undefined` triggers the difference between `obj?.prop` and `obj.prop`. Passing `{}` where the mutant needs `undefined` leaves that specific mutant surviving even though the test "looks" like a negative-path test (caught during a real Stryker run on `bds-tooltip`, where a test named "when middlewareData is absent" used `middlewareData: {}` and missed the corresponding `OptionalChaining` mutant).

---

## Testing Reference-Stable State Updates

Any reducer-style setter that rebuilds a `@State()`/mutable `@Prop()` via `{ ...x, ... }` needs a companion test asserting that a no-op update returns the *same* reference, not just an equal-valued one — use `.toBe()` (reference equality), not `.toEqual()` (deep equality), since `.toEqual()` passes even when the update wastefully allocated a new object:

```typescript
it('keeps the same draft reference when reselecting the already-selected day', async () => {
  const page = await newSpecPage({ components: [BdsDatePicker], html: '...' });
  const instance = page.rootInstance as unknown as { draft: DatePickerDraftState };
  const draftBefore = instance.draft;

  await page.rootInstance.bdsDayClick.emit({ date: draftBefore.selectedDate });
  await page.waitForChanges();

  expect(instance.draft).toBe(draftBefore); // same reference — no redundant re-render
});

it('replaces the draft reference when selecting a genuinely different day', async () => {
  // ...
  expect(instance.draft).not.toBe(draftBefore);
  expect(instance.draft.selectedDate).toBe(newDate);
});
```

Pair this with an idempotency test for any handler that triggers an imperative action (open/navigate/reset) on interaction: fire the same event twice and assert the second call is a no-op (e.g. a spy on the imperative method was called exactly once, not twice).

See `bds-date-picker.events.spec.ts`'s "reselecting the same day keeps same draft reference" / "repeat click doesn't call `showPopover` again" tests for the full pattern, and `ai-docs/guidelines/stencil-best-practices.md` → "Reference-Stable State Updates" for the underlying bug class.

---

## Accepted Mutation Survivors

Document accepted survivors when a conditional has no observable DOM consequence (e.g. `tooltipText={this.info !== '' ? this.info : undefined}` where both `''` and `undefined` are falsy in the child guard). Record the survivor in the component's mutation report at `ai-work/qa/mutation-reports/mutation-<component>.md` — not as a comment in the spec file. `ai-work/` is excluded from git (`.git/info/exclude`), so this stays local QA bookkeeping without polluting shipped test code; spec files should read the same as any other test suite, with no mutation-testing context required to understand them. Include file:line, the mutant(s), and the equivalence reasoning, following the format already used in existing `mutation-*.md` reports. If a pattern generalizes across components (not specific to one run), promote it to `.agents/memory/mutation-testing-stryker-setup.md` instead.
