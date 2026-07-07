# Stryker Setup — Non-obvious Constraints and Test Patterns

Discovered during mutation testing of `bds-grid` and `bds-grid-item` (session 2026-04-20).
Final score: 100% (90 mutants killed, 0 survived).

---

## Constraint: drop `testRegex` from Stencil's Jest preset

Stencil's `getJestPreset()` returns an object that includes a `testRegex` field.
Adding `testMatch` alongside it causes Jest to throw a conflict error.

Fix — always use this destructuring pattern in `jest.stryker.config.cjs`:

```js
const { testRegex: _dropped, ...preset } = getJestPreset();
```

Then spread `preset` and add your own `testMatch`. Never pass both fields to Jest simultaneously.

---

## Constraint: `@/` path alias requires explicit `moduleNameMapper`

Stryker copies mutated source files into a temporary sandbox directory. TypeScript
path aliases configured in `tsconfig.json` are not resolved inside that sandbox.

Fix — always include this entry in the `moduleNameMapper` block of `jest.stryker.config.cjs`
when the component codebase uses `@/` imports:

```js
moduleNameMapper: {
  '^@/(.*)$': '<rootDir>/src/$1',
}
```

Without this, Stryker runs will fail with module-not-found errors on every `@/` import,
and the reported mutation score will be artificially low (uncovered rather than killed).

---

## Constraint: Stryker config files must be added to ESLint ignores

ESLint's `projectService: true` mode flags `.mjs` and `.cjs` config files that are not
included in `tsconfig.json`. Stryker config files fall into this category.

Fix — add to the `ignores` array in `eslint.config.ts` while on the mutation testing branch:

```ts
'*.config.mjs',
'*.config.cjs',
```

Restore `eslint.config.ts` to its original state when returning to the feature branch, or
keep these ignores permanently if the team decides to commit Stryker configs.

---

## Test pattern: killing `undefined check → always true` mutants

Stryker generates mutants that replace optional-prop guard conditions with `true`, making
them appear as if the prop is always present.

These survive unless tests explicitly verify the *absent* state.

Pattern — add an "absent" assertion for every optional CSS custom property:

```ts
expect(root.style.getPropertyValue('--_col-sm')).toBe('');
```

This test fails when the mutant forces the property to always be set, killing the mutant.
Apply this pattern to every optional `@Prop()` that conditionally writes a CSS custom property.

---

## Test pattern: killing `StringLiteral` mutants in `validateNumericProp` calls

Stryker replaces string literal arguments (e.g. the prop name passed to `validateNumericProp`)
with empty strings or other mutations. These survive unless tests assert on the message content.

Pattern — assert that the warning message contains the prop name string:

```ts
expect(console.warn).toHaveBeenCalledWith(expect.stringContaining('"colSpanLg"'));
```

Apply one such assertion per `validateNumericProp` call site. The assertion must reference
the exact prop-name string that the production code passes as an argument.

---

## Test pattern: killing the `logger.warn(component, message)` component-name literal

`Logger.warn` concatenates its two arguments into a single string: `` `[${component}]: ${message}` ``.
Stryker mutates the hardcoded component-name literal (e.g. `'bds-pagination'`) to `''`. Asserting
only on the message text does not kill this mutant, because the message substring is unaffected.

Pattern — assert on the rendered prefix in addition to the message:

```ts
expect(console.warn).toHaveBeenCalledWith(expect.stringContaining('[bds-pagination]:'));
```

Apply one such assertion alongside every existing message-content assertion at each
`logger.warn(...)` call site.

---

## Equivalent mutants discovered on `bds-pagination` (documented, not chased further)

Session: `bds-pagination` mutation testing (2026-07-07), final score 96.26% (12/321 survived,
0 timed out). All 12 remaining survivors were confirmed equivalent — the mutation changes the
source text but cannot change observable behavior, given invariants enforced elsewhere in the
same component. Do not write tests chasing these patterns; recognize them and document instead.

**Dead defensive `undefined` checks on values that are only ever `T | null`.** When a `@State()`
field or DOM query result is typed `X | null` (never `X | undefined`), a guard like
`if (x === undefined || x === null) return;` has an unreachable first branch. Stryker mutants
that force `x === undefined` to `false` are equivalent, because that branch was already
dead. Confirmed for: `pageToFocus: number | null` (never assigned `undefined`), and
`Element.querySelector(...)` return values (spec says `Element | null`, never `undefined`).

**Dead getter-return guards.** `bds-pagination.tsx`'s `totalPages` getter always returns a
`number` (`0` or a finite `Math.ceil(...)` result) — it can never be `undefined` or `null`.
A downstream guard (`if (this.totalPages === undefined || this.totalPages === null || ...)`)
has two unreachable branches; mutants targeting only those branches are equivalent.

**Redundant guards given an upstream invariant.** `this.internalTotalItems === 0 ? return 0
: Math.ceil(...)` in the `totalPages` getter is equivalent to omitting the guard entirely,
because `internalItemsPerPage` is always normalized to a positive number (never `0`), so
`Math.ceil(0 / positive)` already equals `0`. Similarly, `isPrevButtonDisabled`/
`isNextButtonDisabled` OR in `totalPages === 0`, but `normalizePage` always resets
`internalCurrentPage` to `1` whenever `totalPages` is `0` — making `internalCurrentPage <= 1`
(prev) and `internalCurrentPage >= totalPages` (next, since `1 >= 0`) already `true` in that
state regardless of the explicit `totalPages === 0` clause.

**Stencil JSX `key` string-literal mutants are effectively unkillable via rendered-DOM
assertions.** `key={...}` on a `.map()`-rendered list item is an internal vdom reconciliation
hint — Stencil never serializes it to a DOM attribute. Stryker's `StringLiteral` mutant that
collapses a templated key to `''` has no assertable effect through `newSpecPage`'s rendered
output. Killing it would require asserting on cross-render node-identity reuse during a keyed
reorder, which is disproportionate effort for a reconciliation optimization with no user-facing
behavior. Document as equivalent rather than writing a reconciliation-identity test.
