# Test Pull Request — Boreal DS

## Title Format

```
test(<scope>): <TICKET-ID> <what tests were added/fixed>
```

**Example:**

```
test(web-components): EOA-10099 add FACE lifecycle tests for bds-text-field
```

---

## Description of Test Changes

[Explain what tests are being added or modified and why they are necessary]

**Example:**

> Adds comprehensive unit tests for bds-text-field FACE (Form-Associated Custom Elements) lifecycle methods. Covers formAssociatedCallback, formResetCallback, formStateRestoreCallback, and formDisabledCallback to ensure native form integration works correctly.

---

## Motivation

[Why are these tests needed? What gaps do they fill?]

**Example:**

> - **Coverage gap**: FACE lifecycle methods were at 45% coverage (below 90% threshold)
> - **Regression risk**: No tests verified form reset behavior, causing production bug in EOA-10088
> - **Quality gate**: Mutation testing requires ≥ 90% coverage before mutation score check
> - **Compliance**: WCAG 2.1 form requirements need verified test coverage

---

## Test Coverage Added

[Detail what scenarios, edge cases, or behaviors are now tested]

**New Tests:**

- [ ] formAssociatedCallback sets initial value correctly
- [ ] formResetCallback clears value to default
- [ ] formStateRestoreCallback handles browser autocomplete
- [ ] formDisabledCallback reflects disabled state to internals
- [ ] Custom validators trigger on value change
- [ ] checkValidity() returns correct validity state
- [ ] reportValidity() shows validation UI
- [ ] Focus delegation works for invalid form submission

**Coverage Impact:**

- **Before**: 78% statements, 65% branches
- **After**: 94% statements, 91% branches

---

## Type of Test Change

- [ ] New unit tests (Stencil spec tests)
- [ ] New integration tests (E2E tests)
- [ ] Fixed failing tests
- [ ] Updated tests to match implementation changes
- [ ] Improved test quality (better assertions, edge cases)
- [ ] Refactored tests (no coverage change)

---

## Testing Approach

[Describe the testing strategy and patterns used]

**Example:**

> Uses Stencil's `newSpecPage` to render component in isolated JSDOM environment. Mocks ElementInternals API for FACE method verification. Tests both happy path (valid input) and error path (validation failures). Follows patterns from ai-docs/guidelines/stencil-unit-testing-patterns.md.

---

## Test Code Quality

[Highlight any testing patterns, helpers, or best practices applied]

**Example:**

> - Extracted `createFormContext()` helper to reduce test boilerplate
> - Used `waitForChanges()` for async validation timing
> - Applied AAA pattern (Arrange, Act, Assert) consistently
> - Mock ElementInternals using pattern from testing-knowledge skill
> - No test-specific code added to component implementation

---

## Additional Remarks

[Context for reviewers, known limitations, or follow-up testing needed]

**Example:**

> - E2E tests for cross-browser FACE behavior deferred to Phase 2
> - Mutation testing will run after this PR merges (requires ≥ 90% coverage first)
> - Related test improvements for bds-select and bds-checkbox planned in EOA-10100

---

## References

Refs EOA-XXXXX

---

## Checklist

### General

- [ ] Follows conventional commit format: `test(scope): TICKET-ID description`
- [ ] Ticket reference included
- [ ] No implementation changes (test-only PR)
- [ ] All tests pass locally

### Test Quality

- [ ] Tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Test names clearly describe what is being tested
- [ ] Each test verifies one specific behavior
- [ ] Assertions are specific and meaningful
- [ ] No flaky tests (runs 10 times without failure)

### Test Coverage

- [ ] Coverage increased or maintained (no decrease)
- [ ] Critical paths are tested (happy path + error path)
- [ ] Edge cases covered (empty values, null, undefined, boundary conditions)
- [ ] Async behavior tested correctly (waitForChanges, promises)
- [ ] Error scenarios tested (invalid inputs, validation failures)

### Boreal DS Testing Standards

- [ ] Follows patterns from `ai-docs/guidelines/stencil-unit-testing-patterns.md`
- [ ] Uses `newSpecPage` for Stencil component tests
- [ ] ElementInternals mocked correctly for FACE tests
- [ ] No hard-coded timeouts (uses waitForChanges)
- [ ] Test isolation maintained (no shared state between tests)

### Test Coverage Metrics

- [ ] Statement coverage ≥ 90%
- [ ] Branch coverage ≥ 80%
- [ ] Function coverage ≥ 90%
- [ ] Line coverage ≥ 90%
- [ ] Coverage report reviewed (no unexpected gaps)

### Test Maintainability

- [ ] Test code is readable and well-structured
- [ ] Helpers extracted for repeated setup/teardown
- [ ] Test data is clear and representative
- [ ] Tests are independent (can run in any order)
- [ ] No commented-out test code

### Performance

- [ ] Tests run quickly (< 100ms per test ideal)
- [ ] No unnecessary re-renders or waits
- [ ] Mocks used appropriately (no real network calls)
- [ ] Test suite run time acceptable

### Documentation

- [ ] Complex test logic has explanatory comments
- [ ] Test helpers documented with JSDoc
- [ ] README updated if new test patterns introduced
- [ ] Examples added for non-obvious testing scenarios
