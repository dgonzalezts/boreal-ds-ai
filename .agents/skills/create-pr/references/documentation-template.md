# Documentation Update Pull Request — Boreal DS

## Title Format

```
docs(<scope>): <TICKET-ID> <what documentation was updated>
```

**Example:**

```
docs(web-components): EOA-10099 add FACE integration guide to README
```

---

## Description of Changes

[Detail what documentation has been added, modified, or removed. Explain the rationale behind these changes.]

**Example:**

> Adds a comprehensive FACE (Form-Associated Custom Elements) integration guide to the README, explaining how to use formAssociatedMixin, implement validators, and handle form lifecycle events. Addresses the #1 support question from consuming teams.

---

## Motivation

[Why were these documentation changes needed? What problem do they solve?]

**Example:**

> - Support tickets show 60% of form component questions are about FACE setup
> - Existing JSDoc is thorough but lacks end-to-end usage examples
> - No single document explains the relationship between FACE, mixins, and IFormControl<T>
> - New developers need a getting-started guide, not API reference

---

## Relevant Sections Updated

[List the specific files and sections affected]

**Example:**

> - **packages/boreal-web-components/README.md**
>   - Added "Form Components" section with FACE guide
>   - Updated table of contents
> - **packages/boreal-web-components/src/mixins/README.md**
>   - Cross-linked to new FACE guide
> - **apps/boreal-docs/src/stories/guides/forms.mdx**
>   - Added live examples using bds-text-field

---

## Type of Documentation Change

- [ ] New documentation (guide, tutorial, reference)
- [ ] Updated existing documentation (corrections, clarifications, expansions)
- [ ] Removed outdated documentation
- [ ] Restructured documentation (improved organization, navigation)
- [ ] Added code examples or demos
- [ ] Fixed typos, grammar, or formatting

---

## Review Considerations

[Highlight specific areas reviewers should focus on]

**Example:**

> - **Accuracy**: Verify FACE lifecycle method descriptions match Stencil implementation
> - **Clarity**: Is the validator example clear for developers new to FACE?
> - **Completeness**: Are there common use cases not covered?
> - **Tone**: Does it match existing Boreal DS documentation style?

---

## Screenshots

[If applicable — attach screenshots of rendered documentation]

---

## Additional Remarks

[Any additional context for reviewers]

**Example:**

> - Intentionally deferred validation error message customization to Phase 2 guide
> - Examples use bds-text-field; will add bds-select examples in follow-up PR
> - Cross-referenced from ai-docs/guidelines/stencil-best-practices.md

---

## References

Refs EOA-XXXXX

---

## Checklist

### General

- [ ] Follows conventional commit format: `docs(scope): TICKET-ID description`
- [ ] Ticket reference included
- [ ] Self-reviewed for clarity and correctness
- [ ] No broken links or references

### Documentation Quality

- [ ] Content is clear, concise, and grammatically correct
- [ ] Technical terms are explained or linked to definitions
- [ ] Code examples are correct and tested
- [ ] Examples follow Boreal DS conventions
- [ ] Tone and style match existing documentation

### Accuracy

- [ ] Information is technically accurate
- [ ] Code examples run without errors
- [ ] API signatures match actual implementation
- [ ] Version numbers are correct (if mentioned)
- [ ] Links point to current, valid URLs

### Completeness

- [ ] Covers the intended topic thoroughly
- [ ] Includes common use cases and examples
- [ ] Addresses known pain points or FAQs
- [ ] Cross-referenced from related documentation
- [ ] Table of contents updated (if applicable)

### Boreal DS Specifics

- [ ] Design token usage documented correctly
- [ ] Component props/events/methods match JSDoc
- [ ] Stencil patterns (FACE, mixins, etc.) explained accurately
- [ ] Framework wrapper usage shown (React/Vue) if applicable
- [ ] Accessibility guidance included for component docs

### Formatting & Structure

- [ ] Markdown formatting is correct
- [ ] Headings follow proper hierarchy (h1 → h2 → h3)
- [ ] Code blocks use correct syntax highlighting
- [ ] Lists, tables, and images render properly
- [ ] File structure is logical and navigable

### Testing

- [ ] Documentation renders correctly in target platform (Storybook/GitHub/README)
- [ ] All code examples tested and verified working
- [ ] Links tested and valid
- [ ] Images load correctly
- [ ] No broken formatting or rendering issues
