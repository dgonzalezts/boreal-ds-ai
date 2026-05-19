---
status: done
---

# Plop.js Story Generator Implementation Plan

## Overview

Implement a Plop.js-based code generator to scaffold Storybook stories (`.stories.ts` + `.mdx`) that automatically comply with Section 5.3 standards in the boreal-ds project.

**Tool**: Plop.js v4.0.1
**Location**: `apps/boreal-docs/`
**Estimated Time**: 2.5 hours
**Output**: Type-safe, pattern-compliant Storybook stories

---

## Implementation Steps

### Step 1: Verify Installation & Add Scripts (5 min)

**Status**: ✅ `plop@4.0.5` already installed in `apps/boreal-docs/package.json`

**Verification**:

```bash
cd apps/boreal-docs
pnpm list plop
# Expected: plop@4.0.5
```

**Update**: `apps/boreal-docs/package.json`

Add scripts (if not already present):

```json
{
  "scripts": {
    "generate:story": "plop story",
    "generate": "plop"
  }
}
```

**Note**: Package has `"type": "module"` (line 5), so `plopfile.js` will use ES module syntax (`export default`)

---

### Step 2: Create Plopfile Configuration (30 min)

**Create**: `apps/boreal-docs/plopfile.js`

**Syntax**: ES module (package.json has `"type": "module"`)

```javascript
export default function (plop) {
  // generator configuration
}
```

**Configuration includes**:

- 6 interactive prompts (name, category, description, additional stories, categories toggle)
- Validation (name required, PascalCase warning, category format)
- Handlebars helpers via `plop.setHelper()` (titlePath, eq, dateFormat)
- 2 file actions with `type: 'add'`
- Dynamic actions array as function: `actions: (data) => { return [...] }`
- `skipIfExists: true` on add actions (silently skip existing files)

**Prompts** (using Inquirer.js):

1. Component name - `type: 'input'`, `validate` function (required, PascalCase warning)
2. Category - `type: 'list'`, choices array with '**custom**' option
3. Custom category - `type: 'input'`, `when: (answers) => answers.category === '__custom__'`
4. Description - `type: 'input'`, default value from component name
5. Include additional stories? - `type: 'confirm'`, default: false
6. Story names - `type: 'input'`, `when` condition, `filter` to transform input
7. Include ArgTypes categories? - `type: 'confirm'`, default: true

**Data transformations in actions function**:

- Use built-in Plop helpers: `kebabCase`, `pascalCase`, `camelCase`
- Custom helper for titlePath: `plop.setHelper('titlePath', (cat, name) => ...)`
- Normalize stories array: Always include "Default" + user variants
- Set computed properties: `hasMultipleStories`, `finalCategory`

---

### Step 3: Create Story Template (45 min)

**Create**: `apps/boreal-docs/.plop-templates/story-simple/Component.stories.ts.hbs`

**Template matches Button.stories.ts pattern**:

- Imports: `html, css` from lit, `formatHtmlSource`, types from `@/types/stories`
- `StoryArgs` type definition with TODO
- `BorealStoryMeta<StoryArgs>` configuration
- `parameters.docs.source` with formatHtmlSource
- `parameters.__sb` for custom styling
- `argTypes` with TODO for categories
- `render` function with Lit templates
- `styles` with css template literal
- Multiple story exports (Default + variants)

**Key considerations**:

- Use `\${styles}` to escape Lit templates (Handlebars sees `{{}}`, Lit uses `${}`)
- Include TODO comments for user guidance
- Support multiple story variants via `{{#each stories}}`
- Match exact Button.stories.ts structure

---

### Step 4: Create MDX Template (20 min)

**Create**: `apps/boreal-docs/.plop-templates/story-simple/Component.mdx.hbs`

**Template matches Button.mdx pattern**:

- Imports: Storybook blocks (Meta, Canvas, ArgTypes)
- Import all stories from .stories file
- `<Meta of={...} />` tag
- Component title and description
- Component Preview section with Default story
- Configurations section with ArgTypes
- Conditional Story Variants section (if multiple stories)

**Features**:

- Conditional "Story Variants" section via `{{#if hasMultipleStories}}`
- References all stories from .stories file
- Clean, scannable structure

---

### Step 5: Test Generator (30 min)

**Test scenarios**:

1. **Simple component**:

   ```bash
   pnpm generate:story
   # Input: TestButton, Components, Default story only
   ```

2. **Multiple stories**:

   ```bash
   pnpm generate:story
   # Input: TestCard, Components, Default + Disabled + WithImage
   ```

3. **Custom category**:

   ```bash
   pnpm generate:story
   # Input: TestModal, "Overlays" (custom)
   ```

4. **Conflict handling**:
   ```bash
   pnpm generate:story
   # Re-generate TestButton (should skip with message)
   ```

**Verification checklist**:

- [ ] Files created at: `src/stories/{Category}/{ComponentName}/`
- [ ] Two files: `{ComponentName}.stories.ts` and `{ComponentName}.mdx`
- [ ] TypeScript compiles without errors: `pnpm lint`
- [ ] Imports resolve (@ path alias works)
- [ ] Stories render in Storybook: `pnpm dev` → localhost:6006
- [ ] MDX displays correctly with Canvas blocks
- [ ] Multiple story exports work
- [ ] TODO comments present for user guidance
- [ ] Kebab-case used in CSS classes
- [ ] PascalCase used in file names and exports

---

### Step 6: Document Usage (15 min)

**Update**: `apps/boreal-docs/README.md`

Add section:

````markdown
## Generating Stories

To scaffold a new Storybook component story:

```bash
pnpm generate:story
```
````

Follow the interactive prompts to create `.stories.ts` and `.mdx` files.

**Post-generation steps**:

1. Define your `StoryArgs` type (replace TODO)
2. Configure `argTypes` with controls and descriptions
3. Implement the `render` function with component markup
4. Add default `args` for each story
5. Run `pnpm dev` to preview in Storybook

**Example**:

```bash
$ pnpm generate:story
? Component name: MyButton
? Select category: Components
? Component description: A customizable button component
? Include additional stories? Yes
? Story names: Disabled, Loading, WithIcon
? Include ArgTypes categories? Yes

✨ Done!
📂 Location: src/stories/Components/MyButton/

📝 Next steps:
1. Open MyButton.stories.ts
2. Implement StoryArgs, argTypes, render
3. Run 'pnpm dev' to preview
```

See existing stories (Button, Icons) for implementation examples.

## File Structure

**New files created**:

```tree
apps/boreal-docs/
├── plopfile.js                                              # NEW
├── .plop-templates/                                         # NEW
│   └── story-simple/                                        # NEW
│       ├── Component.stories.ts.hbs                         # NEW
│       └── Component.mdx.hbs                                # NEW
└── package.json                                             # MODIFIED
```

**Generated output structure**:

```
apps/boreal-docs/src/stories/{Category}/{ComponentName}/
├── {ComponentName}.stories.ts
└── {ComponentName}.mdx
```

**Example** (ComponentName="MyButton", Category="Components"):

```
apps/boreal-docs/src/stories/Components/MyButton/
├── MyButton.stories.ts
└── MyButton.mdx
```

---

## Critical Files

### 1. plopfile.js

**Path**: `apps/boreal-docs/plopfile.js`
**Purpose**: Core generator configuration
**Content**: Prompts, actions, helpers, validation

### 2. Component.stories.ts.hbs

**Path**: `apps/boreal-docs/.plop-templates/story-simple/Component.stories.ts.hbs`
**Purpose**: Template for .stories.ts file
**Must match**: `src/stories/Button/Button.stories.ts` pattern

### 3. Component.mdx.hbs

**Path**: `apps/boreal-docs/.plop-templates/story-simple/Component.mdx.hbs`
**Purpose**: Template for .mdx file
**Must match**: `src/stories/Button/Button.mdx` pattern

### 4. package.json

**Path**: `apps/boreal-docs/package.json`
**Changes**: Add plop dependency, add generate:story script

### 5. README.md

**Path**: `apps/boreal-docs/README.md`
**Changes**: Add "Generating Stories" section

---

## Reference Files

**Existing patterns to match**:

- `/Users/dgonzalez/projects/src/boreal-ds/apps/boreal-docs/src/stories/Button/Button.stories.ts`
- `/Users/dgonzalez/projects/src/boreal-ds/apps/boreal-docs/src/stories/Button/Button.mdx`

**Type definitions used**:

- `/Users/dgonzalez/projects/src/boreal-ds/apps/boreal-docs/src/types/stories.ts`
  - `BorealStoryMeta<T>`
  - `BorealStory<T>`

**Utilities used**:

- `/Users/dgonzalez/projects/src/boreal-ds/apps/boreal-docs/src/utils/formatters.ts`
  - `formatHtmlSource` (async function)

---

## Technical Notes

### Handlebars Escaping for Lit Templates

**Challenge**: Handlebars uses `{{}}`, Lit uses `${}`

**Solution**: Use backslash escape in templates

```handlebars
<style>\${styles}</style>
```

**Result**: Generates correct Lit syntax

```typescript
<style>${styles}</style>
```

### Path Aliases

Templates use `@/` imports:

```typescript
import { formatHtmlSource } from "@/utils/formatters";
import type { BorealStory, BorealStoryMeta } from "@/types/stories";
```

These resolve correctly in Storybook context (configured in `tsconfig.json`).

### Async formatHtmlSource

The `formatHtmlSource` utility returns a Promise. Storybook handles async transforms automatically in `parameters.docs.source.transform`.

### Category with Spaces

Categories like "Images & Icons" are supported. Directories are created with exact category name (no normalization).

---

## Validation Steps

### 1. Installation Verification

```bash
cd apps/boreal-docs
pnpm list plop
# Expected: plop@4.0.1
```

### 2. Generator Execution

```bash
pnpm generate:story
# Should show interactive prompts
```

### 3. File Generation

```bash
ls -la src/stories/Components/TestButton/
# Expected: TestButton.stories.ts, TestButton.mdx
```

### 4. TypeScript Compilation

```bash
pnpm lint
# Should pass without errors
```

### 5. Storybook Rendering

```bash
pnpm dev
# Navigate to localhost:6006
# Check: Components > TestButton appears in sidebar
# Verify: Story renders without errors
# Check: Both Canvas and Docs tabs work
```

### 6. Template Variables

**Open generated files and verify**:

- [ ] Component name in PascalCase in imports
- [ ] Component name in kebab-case in CSS classes
- [ ] Title path: `{Category}/{ComponentName}`
- [ ] All TODO comments present
- [ ] Multiple stories created (if requested)
- [ ] MDX imports correct story file
- [ ] Lit template syntax correct (`${}` not `{{}}`)

### 7. Edge Cases

```bash
# Test category with spaces
pnpm generate:story
# Input: TestModal, "Images & Icons"
# Verify: Directory at "src/stories/Images & Icons/TestModal/"

# Test conflict handling
pnpm generate:story
# Re-run with same name
# Verify: Shows skipIfExists message
```

---

## Post-Implementation

### Team Onboarding

- Run live demo in team meeting
- Show examples: simple story, complex story with variants
- Walk through post-generation TODOs
- Answer questions

### Monitor Usage

- Track generator usage (first month)
- Collect team feedback (Slack, retros)
- Identify pain points or edge cases
- Iterate on templates based on feedback

### Future Enhancements (Optional)

**Phase 2** (2-3 weeks after):

- Conflict resolution prompt (Skip/Overwrite/Rename)
- Pre-filled argTypes suggestions
- More comprehensive documentation (GENERATING_STORIES.md)
- Test automation script

**Phase 3** (1-2 months after):

- Complex story template (Icons pattern with helpers/, constants/, types/)
- Component generator for packages/boreal-web-components (see extension strategy)
- Unified generator (both packages from single command)

---

## Success Criteria

- ✅ Generator runs with single command (`pnpm generate:story`)
- ✅ Generates valid TypeScript .stories.ts files
- ✅ Generates valid MDX documentation files
- ✅ All imports resolve correctly (@ path alias)
- ✅ Generated stories compile without TypeScript errors
- ✅ Stories render in Storybook UI without errors
- ✅ Follows Button reference pattern exactly
- ✅ Includes all Section 5.3 required elements (types, formatHtmlSource, argTypes, etc.)
- ✅ Interactive prompts are clear and helpful
- ✅ Completion time under 60 seconds for simple story
- ✅ Documentation is clear for team onboarding
- ✅ 70% faster than manual story creation
- ✅ Zero compilation errors in generated files
- ✅ Team adoption rate >50% in first month

---

## Timeline

| Step                        | Duration       | Cumulative    |
| --------------------------- | -------------- | ------------- |
| Install dependencies        | 5 min          | 5 min         |
| Create plopfile.js          | 30 min         | 35 min        |
| Create .stories.ts template | 45 min         | 1h 20min      |
| Create .mdx template        | 20 min         | 1h 40min      |
| Test generator              | 30 min         | 2h 10min      |
| Document usage              | 15 min         | 2h 25min      |
| **Total**                   | **~2.5 hours** | **2.5 hours** |

---

## Risk Mitigation

### Risk: Template drift from patterns

**Mitigation**: Reference Button files in template comments, quarterly review

### Risk: TypeScript compilation errors

**Mitigation**: Test with strict mode, validate imports resolve

### Risk: Team adoption resistance

**Mitigation**: Live demo, excellent docs, optional initially

### Risk: Handlebars escaping issues with Lit

**Mitigation**: Test Lit syntax carefully, document escaping rules

---

## Dependencies

**Installed**:

- ✅ `plop@4.0.5` (already in package.json, line 35)

**Sub-dependencies** (automatic):

- inquirer@9.x (prompts - Plop's built-in dependency)
- handlebars@4.x (templates - Plop's built-in dependency)
- globby (file patterns)
- chalk (colors)
- 18 other utility packages

**Total size**: ~613 KB
**Runtime impact**: None (devDependency only)
**Security**: All widely-used, maintained packages

---

## Next Steps After Approval

1. Navigate to `apps/boreal-docs`
2. ✅ ~~Install plop~~ (already installed: v4.0.5)
3. Create `plopfile.js` with ES module syntax
4. Create `.plop-templates/story-simple/` directory
5. Create two template files (.stories.ts.hbs, .mdx.hbs)
6. Update `package.json` scripts (add generate:story, generate)
7. Test with TestButton component
8. Verify in Storybook (`pnpm dev`)
9. Update README with usage instructions
10. Team demo and rollout

**Note**: Plop 4.0.5 includes all features needed. Package.json has `"type": "module"` so plopfile uses ES module syntax.
