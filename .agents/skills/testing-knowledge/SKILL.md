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

**No inline comments in spec files.** The project's no-inline-comments rule (`.agents/AGENTS.md` "Non-Negotiable Rules") applies to spec files exactly as it does to any other source file — there is no test-file carve-out. A test's own `describe`/`it` names and assertions must carry all the meaning a `//` comment would otherwise supply; if a name can't carry it, rewrite the name. The only sanctioned exception is accepted mutation survivor rationale, and even that does not get written as a spec-file comment — it goes in the component's mutation report instead (see "Accepted Mutation Survivors" below).

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

## Failure-Mode Catalog — Explore Before You Write Tests

**Golden rule: do not assume the current implementation is correct.** Before writing any spec file, independently audit the component's actual source and produce a failure-mode catalog — a list of the ways the component's public contract can fail, derived from reading the code itself, not from the plan's stated unit-test list. The plan's list is a claim about what to test; this catalog is an independent check on whether that claim is complete and correct. Distinct from, and additive to, a plan's own "grounded failure-mode/edge-case pass" language if present (see e.g. `ai-work/plans/EOA-17138-bds-date-picker-v2.md`'s orchestrator-level integration-gap check) — that check compares the plan against the codebase before dispatch; this one compares the component's actual behavior against its own contract, independently of the plan, before a single test is written.

### Where the catalog lives

`ai-work/testing/failure-modes/<bds-component>.md` — one file per component. `ai-work/` is tracked in this project's private scaffold remote (not `origin`; see `.git/info/exclude`), so this is a versioned, persistent artifact, not scratch output. If the file already exists from a prior session, read and extend it — do not overwrite past decisions.

### When the catalog is created

Created the first time `testing-subagent` is dispatched **for that component**, not once per plan and not once per task:

- **New component:** created at the first unit-test task, right after the first implementation task gives you real code to audit — there's nothing to audit before that.
- **Existing component under a new plan version** (e.g. a `v2`/`vN` plan adding phases to an already-shipped component): read and extend the catalog that already exists for it; do not start over. A multi-phase plan's later unit-test tasks (Phase 3, 4, 5...) keep extending the same file created at its first phase.
- **Existing component with no catalog yet** (it shipped before this pipeline existed): the first testing-subagent dispatch on it — even for an unrelated small fix — creates the catalog by auditing the component as it stands today, not just the current task's diff. Long-standing `pending-decision` rows this surfaces don't block the current task's own `confirmed` rows from getting tests; they're just now visible and tracked.

### The five failure-mode families

| Family | Covers |
| --- | --- |
| Boundary | Prop/attribute values at the edge: a numeric limit, a date one unit past `min`/`max`, a string at its max length |
| Equivalence | Input classes that should behave identically but might not: `string` vs `Date` vs an enum's declared variants for the same prop |
| Null/empty | A required prop, attribute, or slot that is `undefined`, `null`, or empty |
| Race/timing | Rapid double-fire (double-click emitting `bdsClick` twice), ordering assumptions (`componentDidLoad` vs. listener attach — see "Testing Events That Fire in `componentDidLoad`" above), reference-stability under repeated identical updates (see "Testing Reference-Stable State Updates" above) |
| Component-contract bypass | Can a `disabled`/`readonly` component still be driven — via keyboard, a direct method call, or a guard clause that doesn't actually guard? |

### Catalog row structure

```
### <ID> | <short title>
- **ID:**
- **Category:** boundary | equivalence | null-empty | race-timing | component-contract-bypass
- **Risk:** what breaks for a consumer if this goes wrong (visual, a11y, FACE/form submission, event contract)
- **Input that reveals it:**
- **Observed current behavior:** cite file:line — what the code actually does today
- **Recommended contract:**
- **Contract status:** confirmed | pending-decision
- **Why it matters:**
- **Covered by:** `<spec file path>::<test description>` (filled in once a test exists for this row; see "Generating tests" below)
```

If the intended contract can't be inferred from the code, Figma, or plan, mark it `pending-decision` — never promote today's behavior to `confirmed` just because that's what the code happens to do. A `pending-decision` row blocks a test being written for it, not the rest of the catalog.

### Reconciling against the plan

After the catalog is drafted, check it against the plan's stated unit-test behaviors for the task at hand. Flag any plan-listed test that assumes a `pending-decision` row is settled — that plan item should not be implemented as-is until the row is resolved (see next step). Also flag any failure mode the audit found that the plan's list omits entirely.

### Reconciling against a pre-existing test suite

A component that shipped before this pipeline existed already has spec files with real assertions — e.g. `bds-date-picker`'s v1 `__test__/` suite, which predates the catalog introduced here. Those existing tests are **another input to audit, not a trusted baseline**: the same golden rule applies to them as to the plan's list — a passing existing test can just as easily be documenting a bug as verifying a contract (this is the exact zero-fee-on-zero-amount failure mode the catalog exists to catch).

When the audit produces a `confirmed` row for behavior an existing test already covers with a matching assertion:

- Do not duplicate it with a new test — note in the row that it's already covered, and by which spec file/test name.

When an existing test's assertion **conflicts** with a row's `recommended contract` (i.e. the existing test appears to encode the same bug the catalog is flagging):

- Do not edit or delete the existing test as part of the audit. Mark the row `pending-decision` even if the current behavior seems clearly wrong to you, and surface the conflict explicitly to the user: cite the existing test by file/name, the row's ID, and why they disagree. Resolving which one is right is the same human-in-the-loop decision as any other `pending-decision` row (see below) — only once the user rules does the losing side (test or implementation) get changed, and that change happens in its own explicit step, never silently bundled into writing new tests for unrelated rows.

### No catalog markers in test files — the pointer lives in the catalog, not the test

`ai-work/` is tracked only in this project's private scaffold remote, never `origin` — by company policy, some teammates' checkouts never have the AI scaffold at all, permanently, not just temporarily unsynced. Any marker placed inside a test file pointing back at the catalog (an ID in the test name, a comment referencing `failure-modes.md`) would be permanently dead for that population, with no way to ever resolve it — so don't add one. The link runs one direction only: **the catalog row points at the test, the test never points at the catalog.**

- Test names stay pure specification text, exactly the existing convention (see "Test descriptions read as specifications" above) — no ID prefix, no reference to the catalog or to "failure modes" in any form.
- When you generate a test for a `confirmed` row, write the result back into that row as a `Covered by:` field — `<spec file path>::<test description>`. This is what makes the catalog self-tracing on a later audit: to check whether a row still has a valid test, read `Covered by` and jump straight to it, rather than grepping the test suite for a marker that was never allowed to exist there.
- If a `Covered by` link goes stale (the test was renamed or moved without updating the row), fall back to matching by the row's `Recommended contract` against the spec file's test descriptions — this is reliable precisely because those descriptions are already required to read as specifications, and semantic matching against clear prose survives renames a literal string/ID grep wouldn't.

### Closing `pending-decision` rows (human-in-the-loop)

Present each `pending-decision` row to the user with the contract options you can see, and wait for a ruling — do not resolve it yourself. When closing a row:

- Do not write any tests yet.
- Do not touch production code.
- Do not touch `confirmed` rows or other `pending-decision` rows.
- Record the human's decision directly in that row (update `Recommended contract` and flip `Contract status` to `confirmed`), plus the business reasoning that justified it.

### Generating tests — confirmed rows only

Write a test only for a `confirmed` row. For every `pending-decision` row still open, do not write a test for it — list it as an open question in your response instead, never in the spec file.

- Name each test after the failure mode it protects, in plain specification prose: `it("rejects a date one day past the max-selectable boundary", ...)` — no ID, no catalog reference (see "No catalog markers in test files" above). Traceability lives in the catalog's `Covered by` field, not in the test.
- Structure the test body as Arrange / Act / Assert, separated by blank lines only — no comment labels marking the blocks.
- Do not invent contracts that aren't in the catalog, and do not test internal details unconnected to a `confirmed` row.
- After writing the test, record it in that row's `Covered by` field back in the catalog file.

### When a new test fails against current code

If a test built on a `confirmed` row fails, that is a signal the implementation has a real bug — not a signal the test is wrong. Do not fix the component yourself; that's out of this subagent's scope. Hand off to `frontend-subagent` (or flag to the user/orchestrator) with the same four-rule discipline the catalog-closing step uses: don't change the test, don't change the catalog, don't add new dependencies, and only change code that traces to a `confirmed` row — if a failing test doesn't trace to one, explain why instead of forcing a fix.

---

## Accepted Mutation Survivors

Document accepted survivors when a conditional has no observable DOM consequence (e.g. `tooltipText={this.info !== '' ? this.info : undefined}` where both `''` and `undefined` are falsy in the child guard). Record the survivor in the component's mutation report at `ai-work/qa/mutation-reports/mutation-<component>.md` — not as a comment in the spec file. `ai-work/` is excluded from git (`.git/info/exclude`), so this stays local QA bookkeeping without polluting shipped test code; spec files should read the same as any other test suite, with no mutation-testing context required to understand them. Include file:line, the mutant(s), and the equivalence reasoning, following the format already used in existing `mutation-*.md` reports. If a pattern generalizes across components (not specific to one run), promote it to `.agents/memory/mutation-testing-stryker-setup.md` instead.
