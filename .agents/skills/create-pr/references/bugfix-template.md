# Bug Fix Pull Request — Boreal DS

## Title Format

```
fix(<scope>): <TICKET-ID> <imperative description of what was fixed>
```

**Example:**

```
fix(web-components): EOA-10099 prevent focus trap when modal closes
```

---

## Description of the Bug

[Brief overview of the bug being fixed. What was the issue and in what context did it occur?]

**Example:**

> When bds-modal closed, keyboard focus was not restored to the trigger element, leaving focus on <body> and breaking keyboard navigation for screen reader users.

---

## Steps to Reproduce

1. [Step 1]
2. [Step 2]
3. [Step 3]

**Example:**

1. Open bds-modal by clicking a button
2. Tab through focusable elements in the modal
3. Press Escape to close the modal
4. Observe that focus is on <body>, not the button

---

## Root Cause

[Explain why the bug occurred — what was wrong in the code or logic?]

**Example:**

> The disconnectedCallback() cleanup ran before the modal's close animation completed, clearing the stored focusTriggerElement reference before it could be restored.

---

## Description of the Fix

[Describe how the bug was fixed. Explain the approach and why it resolves the issue.]

**Example:**

> Moved focus restoration logic to the end of the close animation (onAnimationEnd callback) rather than in disconnectedCallback(). This ensures focusTriggerElement is still available when focus is restored.

---

## Impact of the Fix

[Discuss how this fix affects existing functionality. Any behavior changes, performance implications, or side effects?]

**Example:**

> - Fixes WCAG 2.4.3 (Focus Order) violation
> - No breaking changes — modal close behavior unchanged
> - Existing unit tests updated to verify focus restoration timing

---

## Testing Conducted

[Detail the tests performed to ensure the bug is fixed and no regressions introduced]

**Automated:**

- [ ] Unit tests added to verify focus restoration
- [ ] Existing tests still pass
- [ ] Regression tests for modal open/close cycle

**Manual:**

- [ ] Tested focus restoration in Chrome, Firefox, Safari
- [ ] Verified with keyboard navigation only (no mouse)
- [ ] Validated with VoiceOver and NVDA screen readers
- [ ] Confirmed no console errors

---

## Screenshots/Videos

[If applicable — attach before/after videos demonstrating the fix]

---

## Additional Remarks

[Any supplementary context for reviewers]

**Example:**

> - Bug only occurred when close was triggered via Escape key, not close button
> - Edge case: rapid open/close cycles tested and working correctly
> - Related to earlier focus management work in EOA-10088

---

## References

Closes EOA-XXXXX
[Use "Closes" if this PR fully resolves the bug ticket]

---

## Checklist

### General

- [ ] Follows conventional commit format: `fix(scope): TICKET-ID description`
- [ ] Ticket reference included (`Closes EOA-XXXXX`)
- [ ] Code adheres to TypeScript strict mode — no `any`
- [ ] Self-reviewed code for quality and correctness
- [ ] All tests pass locally

### Bug Fix Verification

- [ ] Root cause identified and documented
- [ ] Fix addresses the root cause, not just symptoms
- [ ] Steps to reproduce verified before and after fix
- [ ] Bug no longer reproducible with the fix applied
- [ ] No new bugs introduced by the fix

### Testing

- [ ] Regression tests added to prevent bug from returning
- [ ] Existing unit tests updated if behavior changed
- [ ] Edge cases tested (rapid actions, async timing, etc.)
- [ ] Tested across supported browsers
- [ ] Accessibility verified (keyboard, screen readers)

### Boreal DS Standards

- [ ] Design tokens preserved — no style regressions
- [ ] Component API unchanged (unless required for fix)
- [ ] Events and lifecycle methods work correctly
- [ ] No console warnings or errors introduced

### Documentation

- [ ] JSDoc updated if API changed
- [ ] Storybook story updated if needed
- [ ] Code comments added to explain non-obvious fix logic
- [ ] README updated if user-facing behavior changed

### Impact Assessment

- [ ] Performance impact assessed (no degradation)
- [ ] Bundle size unchanged or minimally increased
- [ ] No breaking changes introduced
- [ ] Backward compatibility maintained
