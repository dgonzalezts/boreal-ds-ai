# Feature Pull Request — Boreal DS

## Title Format

```
feat(<scope>): <TICKET-ID> <imperative description>
```

**Example:**

```
feat(web-components): EOA-10099 add bds-text-field component
```

**Scope options:** `web-components`, `boreal-react`, `boreal-vue`, `boreal-docs`, `boreal-styleguidelines`

---

## Description

[What feature is being added? Explain the functionality and its intended purpose. What problem does this solve or what capability does it enable?]

**Example:**

> Implements the Phase 1 bds-text-field component using formAssociatedMixin and ElementInternals for native form participation. Enables text input with full FACE lifecycle support, built-in validation, and keyboard accessibility.

---

## Implementation Details

[Describe your approach to implementing the feature. Include key design decisions, patterns used, and why this approach was chosen.]

**Example:**

> - Uses formAssociatedMixin for FACE boilerplate (formDisabledCallback, formResetCallback, etc.)
> - Implements IFormControl<string> interface for consistent API across form components
> - Built-in valueMissing validator + customValidators prop for consumer-defined rules
> - Focus delegation via delegatesFocus on shadowRoot for browser focus management
> - Design tokens from boreal-styleguidelines for spacing, colors, and radii

---

## Impact Analysis

[How does this feature affect the existing codebase? Any behavioral changes, performance implications, or breaking changes?]

**Example:**

> - New component — no impact on existing components
> - Adds ~8KB to boreal-web-components bundle (gzipped)
> - Framework wrappers will auto-generate in boreal-react and boreal-vue

---

## Testing Conducted

[Detail the tests carried out to ensure the feature works as intended. Include both automated tests and manual verification steps.]

**Automated:**

- [ ] Unit tests with ≥ 90% coverage
- [ ] FACE lifecycle tests (formAssociatedCallback, formResetCallback, etc.)
- [ ] Validation tests (built-in and custom validators)
- [ ] Accessibility tests (keyboard navigation, ARIA attributes)

**Manual:**

- [ ] Tested in Chrome, Firefox, Safari
- [ ] Screen reader verification (VoiceOver/NVDA)
- [ ] Form submission with valid/invalid states
- [ ] Integration with native form reset/submit

---

## Related Changes

[List any changes in other packages or areas of the codebase]

**Example:**

> - **boreal-docs**: Added Storybook story with usage examples
> - **boreal-react**: Auto-generated wrapper with React types
> - **No changes to**: boreal-styleguidelines (reused existing tokens)

---

## Screenshots/Videos

[If applicable — attach screenshots or videos demonstrating the new feature]

---

## Additional Remarks

[Context for reviewers — non-obvious constraints, deferred items, areas needing careful attention]

**Example:**

> - Multi-line text support deferred to Phase 2 (textarea variant)
> - Password visibility toggle intentionally excluded (security pattern TBD)
> - See ai-work/plans/EOA-10099-text-field.md for full roadmap

---

## References

Refs EOA-XXXXX
[or use "Closes EOA-XXXXX" if this PR fully resolves the ticket]

---

## Checklist

### General

- [ ] Follows conventional commit format: `feat(scope): TICKET-ID description`
- [ ] Ticket reference included (`Refs` or `Closes` EOA-XXXXX)
- [ ] Code adheres to TypeScript strict mode — no `any` or implicit types
- [ ] Self-reviewed code for quality, readability, and correctness
- [ ] All tests pass locally (`.agents/scripts/with-node.sh pnpm test`)

### Boreal DS — Component Standards

- [ ] Design tokens used exclusively — no hard-coded colors, spacing, or radii
- [ ] Component tag uses `bds-` prefix
- [ ] All props have explicit TypeScript types
- [ ] Events use bare `@Event()` (no `bubbles`/`composed` unless required)
- [ ] SCSS follows `@use` pattern (no `@import`)
- [ ] Light DOM patterns documented if used

### Boreal DS — Form Components (if applicable)

- [ ] Uses formAssociatedMixin for FACE boilerplate
- [ ] Implements IFormControl<T> interface
- [ ] Includes @Method() wrappers for checkValidity() and reportValidity()
- [ ] Focus delegation configured correctly
- [ ] Validation tested with built-in and custom validators

### Testing

- [ ] Unit test coverage ≥ 90% statements
- [ ] Tests cover happy path, error cases, and edge cases
- [ ] Accessibility verified (keyboard navigation, screen readers)
- [ ] Manual testing completed in all supported browsers

### Documentation

- [ ] JSDoc added to all public APIs (props, events, methods)
- [ ] Storybook story created with usage examples
- [ ] Storybook MDX documentation added (usage, API, examples)
- [ ] README updated if component API changed

### Performance & Compatibility

- [ ] No new console warnings or errors
- [ ] Bundle size impact assessed (acceptable increase)
- [ ] Compatible across supported browsers (Chrome, Firefox, Safari, Edge)
- [ ] No regression in existing functionality
