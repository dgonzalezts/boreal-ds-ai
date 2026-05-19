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
