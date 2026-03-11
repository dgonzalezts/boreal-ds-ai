# Plop.js Story Generator: Implementation Learnings & Troubleshooting Guide

**Date Created**: 2026-02-04
**Purpose**: Document critical issues, solutions, and best practices discovered during Plop.js story generator implementation
**Audience**: Developers maintaining or extending the Boreal DS story generator

---

## Table of Contents
1. [Critical Issues and Solutions](#critical-issues-and-solutions)
2. [Handlebars Template Best Practices](#handlebars-template-best-practices)
3. [ESLint Configuration Patterns](#eslint-configuration-patterns)
4. [Testing Methodology](#testing-methodology)
5. [Common Pitfalls](#common-pitfalls)

---

## Critical Issues and Solutions

### Issue 1: Helper Functions Returning Objects Instead of Strings

**Symptom**:
```typescript
// Generated output
title: '[object Object]/',
```

**Root Cause**:
Calling `plop.getHelper('helperName')()` programmatically in JavaScript returns helper objects rather than executing the helper functions as expected. This occurs when trying to use Handlebars helpers like `pascalCase` or custom helpers outside of template context.

**Failed Approach**:
```javascript
// ❌ This doesn't work
plop.setHelper('stripPrefix', str => {
  const parts = str.split('-');
  const withoutPrefix = parts.slice(1).join('-');
  return plop.getHelper('pascalCase')(withoutPrefix); // Returns object!
});

// ❌ This also fails
data.titlePath = plop.getHelper('titlePath')(category, data.componentName);
```

**Solution**:
Replace Handlebars helper calls with plain JavaScript utility functions:

```javascript
// ✅ Use pure JavaScript functions
const toPascalCase = str => {
  return str
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join('');
};

const stripPrefix = componentName => {
  if (!componentName) return '';
  const parts = componentName.split('-');
  const withoutPrefix = parts.slice(1).join('-');
  return toPascalCase(withoutPrefix);
};

// In actions function
const componentNameWithoutPrefix = stripPrefix(data.componentName);
data.componentNameWithoutPrefix = componentNameWithoutPrefix;
```

**Lesson Learned**:
- **Don't call Handlebars helpers programmatically in JavaScript**
- Use pure JavaScript utility functions for data transformations in `actions` functions
- Reserve `plop.setHelper()` only for helpers used directly in templates (e.g., `eq`, `dateFormat`)

**Impact**: Critical - Breaks title path, component names, and render function references

---

### Issue 2: Lit Template String Escaping in Handlebars

**Symptom**:
```typescript
// Generated output
<style>
  \${styles}  // ❌ Backslash rendered literally, won't interpolate
</style>
```

**Root Cause**:
Misunderstanding of Handlebars escaping rules. Developers mistakenly tried to escape `${...}` (Lit template syntax) thinking Handlebars would process it, but **Handlebars only processes `{{...}}`**, not `${...}`.

**Failed Approach**:
```handlebars
<!-- ❌ Incorrect escaping -->
<style>
  \${styles}
</style>
```

**Solution**:
```handlebars
<!-- ✅ No escaping needed for ${} -->
<style>
  ${styles}
</style>
```

**Lesson Learned**:
- Handlebars delimiters: `{{...}}` (double curly braces)
- Lit template delimiters: `${...}` (dollar + single curly)
- **No conflict exists** - write Lit syntax directly in Handlebars templates
- Only escape Handlebars syntax: Use `\{{` if you need literal `{{` in output

**Impact**: Critical - Breaks component rendering and style application

---

### Issue 3: Handlebars Context Scope in Loops

**Symptom**:
```typescript
// Generated output
render: render,  // ❌ Empty string, undefined reference
```

**Root Cause**:
Inside a Handlebars `{{#each}}` loop, the context changes to the current iteration item. Variables from the parent scope are not directly accessible.

**Failed Approach**:
```handlebars
{{#each stories}}
export const {{this}}: Story = {
  render: render{{componentNameWithoutPrefix}},  // ❌ Empty string
};
{{/each}}
```

**Solution**:
Use `../` to access parent context or `@root.` for top-level context:

```handlebars
{{#each stories}}
export const {{this}}: Story = {
  render: render{{../componentNameWithoutPrefix}},  // ✅ Accesses parent
};
{{/each}}
```

**Alternative** (for root-level access):
```handlebars
render: render{{@root.componentNameWithoutPrefix}},
```

**Lesson Learned**:
- **Context changes inside loops**: `{{this}}` refers to current item
- **Parent scope**: Use `../variableName` to go up one level
- **Root scope**: Use `@root.variableName` for top-level data
- Test loop-generated code carefully for variable scoping issues

**Impact**: Critical - Breaks render function references in all stories

---

### Issue 4: Handlebars Parser Confusion with Nested Braces

**Symptom**:
```
[ERROR] Parse error on line 64:
...scal}}Stories.{{this}}} /><Canvas of={
Expecting 'CLOSE', got 'CLOSE_UNESCAPED'
```

**Root Cause**:
The sequence `}}}` (Handlebars `}}` + JSX `}`) confuses the Handlebars parser. It sees three closing braces and tries to interpret them as a special syntax (like triple-brace unescaped output `{{{...}}}`).

**Failed Approach**:
```handlebars
<!-- ❌ Parser sees "}}}}" and gets confused -->
<StoryName of={ {{~../componentNamePascal}}Stories.{{this}}} />
```

**Solution**:
Add a space before the JSX closing brace to separate tokens:

```handlebars
<!-- ✅ Space prevents parser confusion -->
<StoryName of={ {{~../componentNamePascal}}Stories.{{this}} } />
                                                          ^^ ^
                                             Handlebars close + space + JSX close
```

**Lesson Learned**:
- **Avoid `}}}` sequences** in Handlebars templates
- Use whitespace to disambiguate nested brace structures
- Handlebars triple-brace `{{{...}}}` is for unescaped HTML output
- Test MDX/JSX templates carefully for brace-related parser issues

**Impact**: Critical - Prevents MDX file generation entirely

---

### Issue 5: ESLint Empty Object Type Restrictions

**Symptom**:
```typescript
type StoryArgs = {};  // ❌ ESLint error: @typescript-eslint/no-empty-object-type
```

**Error Message**:
> "The `{}` ("empty object") type allows any non-nullish value, including literals like `0` and `""`. If you want a type meaning "any object", you probably want `object` instead."

**Root Cause**:
The `@typescript-eslint/no-empty-object-type` rule flags `{}` types because they're semantically ambiguous (they mean "any non-nullish value," not "empty object").

**Failed Approaches**:
```typescript
// ❌ Too verbose, clutters template
type StoryArgs = Record<string, never> & {};

// ❌ Wrong semantics
type StoryArgs = object;

// ❌ Requires comment that users might forget to remove
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
type StoryArgs = {};
```

**Solution**:
Configure ESLint rule with `allowWithName` pattern to allow specific type names:

```javascript
// eslint.config.js
'@typescript-eslint/no-empty-object-type': [
  'error',
  {
    allowWithName: 'Args$',  // Allows types ending with "Args"
  },
],
```

Then use clean syntax in template:
```typescript
// ✅ Clean, no linting errors
type StoryArgs = {
  // TODO: Define your component args here
};
```

**Lesson Learned**:
- Use **scoped ESLint configurations** for template-generated patterns
- `allowWithName` accepts regex patterns (e.g., `'Args$'` matches `*Args`)
- Keeps generated code clean without disabling rules project-wide
- Document the pattern in ESLint config comments

**Impact**: Medium - Code works but fails linting, blocks CI/CD

---

## Handlebars Template Best Practices

### 1. Variable Substitution

**Basic substitution**:
```handlebars
{{variableName}}          <!-- Escaped output (safe for HTML) -->
{{{variableName}}}        <!-- Unescaped output (raw HTML) -->
```

**Context access**:
```handlebars
{{this}}                  <!-- Current context (e.g., in loops) -->
{{../parentVariable}}     <!-- Parent scope -->
{{@root.topLevel}}        <!-- Root-level data -->
```

### 2. Conditionals

**If/else**:
```handlebars
{{#if condition}}
  Content when true
{{else}}
  Content when false
{{/if}}
```

**Custom helper comparison**:
```handlebars
{{#if (eq value "target")}}
  Content when equal
{{/if}}
```

### 3. Loops

**Each loop**:
```handlebars
{{#each items}}
  {{this}}                <!-- Current item -->
  {{../parentVar}}        <!-- Access parent scope -->
  {{@index}}              <!-- Current index (0-based) -->
{{/each}}
```

### 4. Whitespace Control

**Tilde `~` removes whitespace**:
```handlebars
{{~variable}}             <!-- Remove preceding whitespace -->
{{variable~}}             <!-- Remove following whitespace -->
{{~variable~}}            <!-- Remove both -->
```

**Use case**: Tight spacing in generated code
```handlebars
<Meta of={ {{~componentNamePascal}}Stories} />
<!-- Generates: <Meta of={ComponentStories} /> -->
```

### 5. Comments

**Handlebars comments** (not in output):
```handlebars
{{!-- This comment is removed during processing --}}
```

**Output comments** (included in generated files):
```handlebars
<!-- This comment appears in the output -->
{/* JSX comment style for MDX files */}
```

---

## ESLint Configuration Patterns

### Pattern 1: Scoped Rule Exceptions

Use `allowWithName` for template-generated patterns:

```javascript
'@typescript-eslint/no-empty-object-type': [
  'error',
  {
    allowWithName: 'Args$',  // Regex: matches types ending with "Args"
  },
],
```

**Benefits**:
- Allows `StoryArgs`, `ComponentArgs`, `ButtonArgs` when empty
- Still flags other empty object types
- No eslint-disable comments needed
- Clean generated code

### Pattern 2: File-Specific Rules

For stories directory only:

```javascript
{
  files: ['src/stories/**/*.{ts,tsx}'],
  rules: {
    '@typescript-eslint/no-empty-object-type': [
      'error',
      { allowObjectTypes: 'always' }
    ],
  },
}
```

### Pattern 3: Development vs Production

```javascript
{
  files: ['**/*.stories.{ts,tsx}'],
  rules: {
    '@typescript-eslint/no-empty-object-type': process.env.NODE_ENV === 'development'
      ? 'warn'   // Allow during development
      : 'error', // Enforce in CI/production
  },
}
```

---

## Testing Methodology

### Test Scenario Structure

**1. Simple Component (Automatic Mode)**
- Tests: Basic generation, prefix stripping, automatic story mode
- Validates: Title path, component field, render functions, MDX auto mode

**2. Multiple Stories (Manual Mode)**
- Tests: Story variant generation, manual MDX mode
- Validates: Story exports, manual story listing, context in loops

**3. Custom Categories**
- Tests: Custom category input, special characters
- Validates: Directory creation with spaces/ampersands

**4. Conflict Handling**
- Tests: `skipIfExists` behavior
- Validates: No file overwrites, appropriate warnings

**5. Edge Cases**
- Tests: Multi-word components, no categories, unusual names
- Validates: PascalCase conversion, optional features

### Verification Checklist

For each generated file, verify:

**`.stories.ts` file**:
- [ ] Imports correct (html, css, formatHtmlSource, types)
- [ ] Title path has prefix stripped
- [ ] Component field uses full kebab-case name
- [ ] Lit templates use `${...}` not `\${...}`
- [ ] Render function names match component
- [ ] Story exports reference correct render function
- [ ] No TypeScript compilation errors
- [ ] No ESLint errors

**`.mdx` file**:
- [ ] Imports match story display mode (Stories vs Canvas)
- [ ] Meta/Title references correct story imports
- [ ] All sections present (How to use, When to use, etc.)
- [ ] Automatic mode uses `<Stories />` component
- [ ] Manual mode lists each story explicitly
- [ ] No Handlebars parse errors
- [ ] No React/MDX errors in Storybook

### Manual Completion Test

To verify the full workflow:

1. Generate a test component
2. Implement the TODO sections:
   - Define `StoryArgs` with real properties
   - Add `argTypes` configuration with controls
   - Implement render function with component markup
   - Add default `args` values
3. Run `pnpm dev` and verify in Storybook:
   - Controls panel works
   - Component renders correctly
   - Code snippets display properly
   - ArgTypes table shows categories
   - All stories appear in sidebar

---

## Common Pitfalls

### ❌ Pitfall 1: Calling Helpers Programmatically
```javascript
// ❌ Don't do this
const result = plop.getHelper('pascalCase')(myString);

// ✅ Do this instead
const toPascalCase = str => { /* pure JS implementation */ };
const result = toPascalCase(myString);
```

### ❌ Pitfall 2: Over-Escaping Template Syntax
```handlebars
<!-- ❌ Don't escape Lit syntax -->
<style>\${styles}</style>

<!-- ✅ Write it directly -->
<style>${styles}</style>
```

### ❌ Pitfall 3: Forgetting Parent Context in Loops
```handlebars
{{#each items}}
  <!-- ❌ Won't work - wrong scope -->
  {{componentName}}

  <!-- ✅ Access parent scope -->
  {{../componentName}}
{{/each}}
```

### ❌ Pitfall 4: Adjacent Closing Braces
```handlebars
<!-- ❌ Parser confused by }}} -->
<Component prop={ {{value}}} />

<!-- ✅ Add space -->
<Component prop={ {{value}} } />
```

### ❌ Pitfall 5: Project-Wide ESLint Disables
```javascript
// ❌ Too permissive
'@typescript-eslint/no-empty-object-type': 'off'

// ✅ Scoped exception
'@typescript-eslint/no-empty-object-type': [
  'error',
  { allowWithName: 'Args$' }
]
```

---

## Quick Reference

### Handlebars Syntax Cheat Sheet

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{{var}}` | Output variable | `{{componentName}}` |
| `{{{var}}}` | Unescaped output | `{{{htmlContent}}}` |
| `{{!-- --}}` | Comment (removed) | `{{!-- TODO: fix --}}` |
| `{{#if}}` | Conditional | `{{#if condition}}...{{/if}}` |
| `{{#each}}` | Loop | `{{#each items}}{{this}}{{/each}}` |
| `{{../var}}` | Parent scope | `{{../parentVariable}}` |
| `{{@root.var}}` | Root scope | `{{@root.topLevelVar}}` |
| `{{~var}}` | Trim whitespace | `{{~componentName~}}` |

### Common Helper Functions Needed

```javascript
// PascalCase conversion
const toPascalCase = str =>
  str.split('-')
     .map(w => w.charAt(0).toUpperCase() + w.slice(1))
     .join('');

// Strip prefix (br-button → Button)
const stripPrefix = name => {
  const parts = name.split('-');
  return toPascalCase(parts.slice(1).join('-'));
};

// kebab-case conversion
const toKebabCase = str =>
  str.replace(/([a-z])([A-Z])/g, '$1-$2')
     .toLowerCase();
```

---

## Debugging Tips

### 1. Enable Verbose Plop Output
```bash
DEBUG=plop:* pnpm generate:story
```

### 2. Test Template Syntax Separately
Create a minimal test template:
```handlebars
<!-- test.hbs -->
Title: {{titlePath}}
Component: {{componentName}}
Stripped: {{componentNameWithoutPrefix}}
```

### 3. Inspect Generated Data
Add logging to plopfile actions:
```javascript
actions: data => {
  console.log('Generated data:', JSON.stringify(data, null, 2));
  return [/* actions */];
}
```

### 4. Validate Handlebars Syntax
Use online Handlebars playground: https://handlebarsjs.com/playground.html

### 5. Check ESLint Configuration
```bash
npx eslint --print-config src/stories/Component/Component.stories.ts
```

---

## Related Documentation

- [Plop.js Official Docs](https://plopjs.com/documentation/)
- [Handlebars Syntax Guide](https://handlebarsjs.com/guide/)
- [TypeScript ESLint Rules](https://typescript-eslint.io/rules/)
- [Storybook Component Story Format](https://storybook.js.org/docs/api/csf)
- [Lit Template Syntax](https://lit.dev/docs/templates/overview/)

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-04 | 1.0 | Initial documentation - All critical issues resolved |

---

## Contributors

- Implementation and documentation based on Test Scenario 1 execution
- Issues discovered and resolved during boreal-docs generator development
