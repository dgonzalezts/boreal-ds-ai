# PR Title

chore(web-components): EOA-15147 improve Storybook docs with imperative API examples

---

# PR Body

## Description of Changes

Updates Storybook stories and MDX documentation across multiple components to demonstrate the imperative API pattern for setting JavaScript properties. Replaces Lit property binding syntax (`.floatingOptions={...}`) with an IIFE + `<script>` tag pattern that mirrors real-world usage and remains visible in Storybook's Source panel.

Key updates:
- **Story templates** (`component.mdx.hbs`): Improved "How to use it" section with framework-agnostic setup instructions and Framework Integration guide reference
- **Floating components** (tooltip, popover): Switched to IIFE pattern for `floatingOptions` to expose the imperative API
- **Storybook configuration**: Enhanced preview decorator with contrast scheme detection and improved theme handling
- **KeyboardDocs component**: New utility for documenting keyboard interactions
- **Story generation** (plopfile): Updated template prompts for clearer component descriptions

## Motivation

**Problem**: Lit property assignments like `.floatingOptions=${{...}}` are invisible in Storybook's Source panel, leaving developers to guess how to set JS properties in real code.

**Solution**: Demonstrating the imperative API via IIFE makes the code visible and teaches developers the exact pattern they need to use in their applications.

**Additional improvements**:
- Consistent "How to use it" sections across all component docs
- Better onboarding for new developers (setup once, use everywhere)
- Framework-specific guidance (React/Vue) via Framework Integration guide
- Fixed tooltip `stayOnHover` and `hideArrow` behavior bug during documentation review

## Implementation Details: Why IIFE Over Property Binding

**The Pattern:**

```typescript
// ❌ Before: Invisible in Storybook Source panel
const renderTooltip: Story['render'] = args => html`
  <bds-tooltip .floatingOptions=${{ placement: args.placement }}>
    Content
  </bds-tooltip>
`;

// ✅ After: Visible in Storybook Source panel and real-world code
const renderTooltip = (tooltipId: string): Story['render'] => args => html`
  <bds-tooltip id="${tooltipId}">Content</bds-tooltip>
  <script>
    (function () {
      const tooltip = document.getElementById('${tooltipId}');
      tooltip.floatingOptions = {
        placement: '${args.placement}',
        offset: ${args.offset},
      };
    })();
  </script>
`;
```

**Why IIFE?**

1. **Storybook Source Panel Visibility**: Lit property assignments (`.prop=${}`) are invisible in the generated source code, leaving developers unable to see how to replicate the behavior
2. **Real-World Accuracy**: The IIFE pattern matches how developers actually set JS properties in their code (imperative API)
3. **No Type Casting**: Eliminates TypeScript type assertions like `as FloatingPopoverProp['placement']` by using string literals
4. **Isolated Scope**: IIFE prevents global namespace pollution and ensures each story gets a unique, scoped element
5. **Copy-Paste Ready**: Developers can copy the source directly from Storybook and adapt it to their framework without translation

## Relevant Sections Updated

### Storybook Configuration
- `apps/boreal-docs/.storybook/preview.ts`
  - Enhanced `withCustomStyling` decorator with `data-sb-scheme` attribute for contrast-aware styling
  - Improved language registration for syntax highlighting
- `apps/boreal-docs/.storybook/preview.css`
  - Added `data-sb-scheme` rules for light/mid/dark backgrounds

### Story Templates & Generation
- `apps/boreal-docs/.plop-templates/story-simple/component.mdx.hbs`
  - Improved "How to use it" section with canonical setup instructions
  - Framework Integration guide callout
  - Clearer component description prompt
- `apps/boreal-docs/plopfile.js`
  - Updated description prompt to "Complete the sentence"

### Story Examples (New & Updated)
- New stories with comprehensive examples:
  - `bds-button-group` (237 lines)
  - `bds-list-menu` (737 lines)
  - `bds-toggle` (467 lines)
  - `bds-pagination` (360 lines)
  - `bds-table` (1509 lines, significant v2 documentation)
  - `bds-badge`, `bds-spinner`, `bds-status` (feedback components)
- Updated `bds-tooltip.stories.ts` and `bds-popover.stories.ts` with IIFE pattern

### New Components
- `KeyboardDocs` component and styles for documenting keyboard interactions
- Accessible keyboard event documentation across interactive components

### Documentation
- **MDX files** updated with `floatingOptions` imperative API documentation
- Consistent structure across all component docs
- Added keyboard interaction documentation

## Impact

### Consuming teams
- **Benefits**: Clearer examples of how to use floating components; consistent "How to use it" section across all docs; framework-specific guidance
- **Breaking changes**: None
- **Migration needed**: No — this is documentation/demo only

### Component behavior
- **Tooltip bug fix**: Fixed `stayOnHover` and `hideArrow` not working in Storybook (these now properly set via imperative API)
- **No functional changes** to components themselves

### CI/Build
- Added `KeyboardDocs` to the docs app component index
- Storybook stories may render slightly differently due to new decorator, but no visual regressions expected

## Testing

### Manual Verification Steps

1. **Run Storybook**:
   ```bash
   pnpm dev:docs
   ```

2. **Test floating component examples** (Tooltip, Popover):
   - Open "Overlays > Tooltip" and "Overlays > Popover" stories
   - In the Source panel (Docs tab), verify the `<script>` block is visible with property assignments
   - Switch story variants and confirm `floatingOptions` values update in the source code
   - Test interactive controls (placement, offset, etc.) update the DOM properties correctly

3. **Test new stories**:
   - Navigate to new stories (Button Group, List Menu, Toggle, Pagination, Table)
   - Verify "How to use it" section appears with setup instructions
   - Check Framework Integration callout renders with link

4. **Test "How to use it" consistency**:
   - Open several component stories (Button, Badge, Spinner)
   - Verify all have the same "How to use it" structure (setup → framework callout → usage example)

5. **Test theme/contrast**:
   - Toggle Storybook background colors (light, mid, dark)
   - Verify `data-sb-scheme` attribute updates on the story container
   - Check any theme-dependent story styling adapts correctly

### Automated Tests
- [x] Storybook builds without errors (`pnpm build:docs`)
- [x] No console errors or warnings in Storybook
- [x] All story render functions execute without runtime errors
- [x] No TypeScript type errors in story files

## Related Changes

- **Refs EOA-15149**: Tooltip bug fix (stayOnHover, hideArrow) merged during documentation review
- **Depends on**: @telesign/boreal-web-components (floating options API must exist)
- **Framework wrappers**: React/Vue wrapper teams should reference the Framework Integration guide in their docs

## Additional Remarks

### Deferred Work
- **Table v2 styling**: Full table v2 CSS alignment deferred to follow-up PR; current docs reflect current state
- **Keyboard event standardization**: KeyboardDocs component is foundation; per-component keyboard shortcuts can be expanded in future PRs

### Non-Obvious Constraints
- **Script placement**: `<script>` must be inside the `html\`...\`` template so Lit processes the string interpolations; element ID is scoped to prevent collisions
- **Storybook source filter**: `excludeDecorators: true` in parameters ensures the decorator wrapper doesn't appear in the source panel (decorator handles background; user sees clean component markup)
- **Contrast scheme**: `data-sb-scheme` is computed from Storybook's active background color, not story-controlled; updates only when background control changes

### Testing Surface
- Story render functions now return IIFE-wrapped templates — verify no memory leaks or multiple script executions on controls/args changes
- New KeyboardDocs component uses CSS `@supports` for keyboard key styling — test rendering in older browsers if applicable

## References

Refs EOA-15147

---

## Checklist

### General

- [x] Follows conventional commit format: `chore(web-components): EOA-15147 description`
- [x] Ticket reference included
- [x] Self-reviewed for clarity and correctness
- [x] No broken links or references

### Documentation Quality

- [x] Story examples are clear and demonstrate realistic use cases
- [x] "How to use it" section is consistent across all component docs
- [x] Code examples follow Boreal DS conventions (web components tag naming, prop naming)
- [x] Examples work with the actual component implementations
- [x] Tone matches existing Storybook documentation

### Storybook Specifics

- [x] All new stories render without console errors
- [x] Source panel displays correctly (decorators excluded, scripts visible)
- [x] Interactive controls (argTypes) update stories as expected
- [x] MDX documentation renders correctly with proper syntax highlighting
- [x] Framework Integration guide callout present and working

### Accuracy

- [x] IIFE pattern matches real-world imperative API usage
- [x] `floatingOptions` properties documented match component interface
- [x] `data-sb-scheme` contrast detection logic accurate
- [x] KeyboardDocs component accessibility verified

### Testing

- [x] Storybook builds without errors (`pnpm build:docs`)
- [x] No type errors in story files (TypeScript strict mode)
- [x] Manual testing of floating component examples (tooltip/popover)
- [x] Manual testing of new stories (button-group, list-menu, toggle, pagination, table)
- [x] Manual testing of "How to use it" consistency across docs

### Boreal DS Specifics

- [x] All component examples use `bds-*` tag prefix
- [x] Prop naming follows boolean convention (no `is`, `has`, `show` prefixes)
- [x] Design tokens used where applicable (colors, spacing, sizing)
- [x] No inline CSS — uses imported stylesheets or scoped styles
- [x] JSDoc on story render functions documented
</content>
