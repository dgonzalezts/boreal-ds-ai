# Breaking Change Pull Request — Boreal DS

## Title Format

```
<type>(<scope>)!: <TICKET-ID> <breaking change description>
```

**Example:**

```
feat(web-components)!: EOA-10099 rename bds-input to bds-text-field
```

**Note:** The `!` after scope signals a breaking change per conventional commits spec.

---

## ⚠️ BREAKING CHANGE Notice

**Type:** [Select one]

- [ ] API change (prop/method/event renamed or removed)
- [ ] Component renamed or removed
- [ ] Behavior change (same API, different behavior)
- [ ] Minimum version requirement change (Node.js, browsers, dependencies)
- [ ] Build output change (package structure, exports)

**Impact Level:** [Select one]

- [ ] **High** — Affects all/most consumers, requires code changes
- [ ] **Medium** — Affects subset of consumers, requires some code changes
- [ ] **Low** — Affects edge cases, easy migration path

---

## Description of Breaking Change

[Explain what is changing and why this breaking change is necessary]

**Example:**

> Renames `bds-input` component to `bds-text-field` to align with WCAG naming conventions and reduce confusion with native `<input>` element. All functionality remains identical — only the component name and import path change.

---

## Justification for Breaking Change

[Why is this breaking change worth the migration cost? What problem does it solve?]

**Example:**

> - **Consistency**: Aligns with WCAG 2.1 terminology (text field vs. input)
> - **Clarity**: "bds-input" was ambiguous (input field? input group? input wrapper?)
> - **Standards**: Matches naming in Material Design, Carbon, and other major design systems
> - **User feedback**: 12 support tickets about "input vs text-field" confusion
> - **Timing**: Better to fix now (v2.x) before v3.0 LTS

---

## Migration Path

[Provide clear, step-by-step migration instructions for consumers]

### For Web Components

**Before:**

```typescript
import { BdsInput } from '@telesign/boreal-web-components';
<bds-input value="example" />
```

**After:**

```typescript
import { BdsTextField } from '@telesign/boreal-web-components';
<bds-text-field value="example" />
```

### For React

**Before:**

```tsx
import { BdsInput } from "@telesign/boreal-react";
<BdsInput value="example" />;
```

**After:**

```tsx
import { BdsTextField } from "@telesign/boreal-react";
<BdsTextField value="example" />;
```

### For Vue

**Before:**

```vue
import { BdsInput } from '@telesign/boreal-vue';
<bds-input value="example" />
```

**After:**

```vue
import { BdsTextField } from '@telesign/boreal-vue';
<bds-text-field value="example" />
```

---

## Automated Migration Tools

[Provide codemod, scripts, or find/replace patterns to automate migration]

**Example:**

**Find/Replace (Regex):**

```regex
Find:    import \{ BdsInput \} from '@telesign/boreal-(web-components|react|vue)';
Replace: import { BdsTextField } from '@telesign/boreal-$1';

Find:    <bds-input
Replace: <bds-text-field

Find:    </bds-input>
Replace: </bds-text-field>

Find:    <BdsInput
Replace: <BdsTextField

Find:    </BdsInput>
Replace: </BdsTextField>
```

**Codemod (if provided):**

```bash
npx @telesign/boreal-codemod rename-input-to-text-field ./src
```

---

## Affected APIs

[Document all API changes in detail]

| Old API                     | New API                          | Notes                    |
| --------------------------- | -------------------------------- | ------------------------ |
| `<bds-input>`               | `<bds-text-field>`               | Component tag renamed    |
| `BdsInput` (class)          | `BdsTextField`                   | TypeScript class renamed |
| `bds-input-change` (event)  | `bds-text-field-change`          | Event name auto-renamed  |
| `src/components/bds-input/` | `src/components/bds-text-field/` | File path changed        |

**No changes to:**

- Props (all props remain identical)
- Events (behavior unchanged, only naming)
- Methods (checkValidity, reportValidity, etc.)
- Validation logic
- FACE integration

---

## Deprecation Period

[If applicable, explain deprecation timeline]

**Example:**

> - **v2.5.0** (this release): `bds-input` deprecated with console warning
> - **v2.6.0 - v2.9.0**: Parallel support for both `bds-input` and `bds-text-field`
> - **v3.0.0**: `bds-input` removed entirely

**Deprecation Warning:**

```
⚠️  Warning: bds-input is deprecated and will be removed in v3.0.0.
    Please migrate to bds-text-field. See migration guide: [URL]
```

---

## Estimated Migration Effort

[Help consumers understand the scope of work required]

**Example:**

| Codebase Size         | Estimated Effort                 |
| --------------------- | -------------------------------- |
| Small (< 10 usages)   | 15 minutes (find/replace)        |
| Medium (10-50 usages) | 1 hour (codemod + manual review) |
| Large (50+ usages)    | 2-4 hours (codemod + testing)    |

**Factors that increase effort:**

- Dynamic component rendering (requires code changes, not just find/replace)
- E2E tests with hardcoded selectors
- Custom CSS targeting `bds-input`

---

## Testing Conducted

[Verify breaking change works as intended and migration path is valid]

**Automated:**

- [ ] All tests updated to use new API
- [ ] Deprecated API triggers console warning
- [ ] New API functions identically to old API
- [ ] Migration codemod tested on sample codebases

**Manual:**

- [ ] Tested migration in 3 real consumer apps
- [ ] Verified console warning appears correctly
- [ ] Confirmed no functionality lost
- [ ] Documentation renders correctly

---

## Additional Remarks

[Context for reviewers, related breaking changes, or follow-up work]

**Example:**

> - **Follow-up**: bds-select and bds-checkbox will also adopt `-field` suffix in v3.0.0 for consistency
> - **Related tickets**: EOA-10100 (bds-select rename), EOA-10101 (migration guide)
> - **Communication plan**: Announcement in #design-system Slack, email to all teams, changelog entry

---

## References

Refs EOA-XXXXX
See migration guide: [URL when published]

---

## Checklist

### General

- [ ] Follows conventional commit format with `!`: `type(scope)!: TICKET description`
- [ ] BREAKING CHANGE footer in commit message
- [ ] Ticket reference included
- [ ] All tests pass with new API
- [ ] Self-reviewed for correctness

### Breaking Change Management

- [ ] Breaking change clearly documented in PR description
- [ ] Justification provided (why breaking change is necessary)
- [ ] Impact level assessed (high/medium/low)
- [ ] All affected APIs documented
- [ ] Migration path provided with examples

### Migration Support

- [ ] Step-by-step migration instructions written
- [ ] Automated migration tools provided (codemod/scripts)
- [ ] Estimated migration effort documented
- [ ] Migration tested on real codebases
- [ ] Before/after code examples included

### Communication

- [ ] Changelog updated with BREAKING CHANGE section
- [ ] Migration guide published (README or separate doc)
- [ ] All consuming teams notified
- [ ] Slack announcement drafted
- [ ] Release notes include prominent breaking change warning

### Deprecation (if applicable)

- [ ] Deprecation timeline established
- [ ] Console warnings implemented for deprecated API
- [ ] Parallel support provided during deprecation period
- [ ] Removal scheduled for specific version

### Testing

- [ ] All tests updated to use new API
- [ ] Migration codemod tested and verified
- [ ] Deprecated API still works (if parallel support)
- [ ] Console warnings tested
- [ ] No regressions in functionality

### Boreal DS Standards

- [ ] Design tokens preserved
- [ ] TypeScript types updated correctly
- [ ] Component conventions maintained
- [ ] Storybook examples updated
- [ ] JSDoc updated with deprecation notices (if applicable)

### Documentation

- [ ] README updated with new API
- [ ] Storybook stories updated
- [ ] Migration guide complete and clear
- [ ] Changelog entry includes migration instructions
- [ ] All code examples updated across docs

### Version Planning

- [ ] Semver major version bump planned (or deprecation period defined)
- [ ] Release notes drafted
- [ ] Rollback plan documented
- [ ] Breaking change communicated to release manager
