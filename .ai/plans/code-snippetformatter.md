---
status: done
---

# Plan: Create `formatHtmlSource` Formatter

## Objective

Replace `prettierFormatter` with `formatHtmlSource` in `src/utils/formatters.ts`:

1. Add comprehensive Prettier options for better HTML formatting
2. Clean empty attribute values with regex (no manual list)
3. Remove style tags
4. (Phase 2, if needed) Handle Lit binding syntax

## Files to Modify

1. `src/utils/formatters.ts` - Replace `prettierFormatter` with `formatHtmlSource`
2. `src/stories/Button.stories.ts` - Update import to use `formatHtmlSource`

## Prettier Options to Add

```typescript
prettier.format(code, {
  parser: "html",
  plugins: [prettierPluginHtml],
  // Layout
  printWidth: 80, // Line length before wrapping
  tabWidth: 2, // Spaces per indentation
  useTabs: false, // Use spaces, not tabs
  // HTML-specific
  htmlWhitespaceSensitivity: "ignore", // 'css' | 'strict' | 'ignore'
  bracketSameLine: false, // Put > on new line
  singleAttributePerLine: true, // One attribute per line when wrapped
});
```

### Option Explanations

| Option                      | Value      | Why                                                             |
| --------------------------- | ---------- | --------------------------------------------------------------- |
| `printWidth`                | `80`       | Standard readable line length                                   |
| `tabWidth`                  | `2`        | Consistent with project style                                   |
| `htmlWhitespaceSensitivity` | `'ignore'` | Allows reformatting without preserving insignificant whitespace |
| `bracketSameLine`           | `false`    | Cleaner multi-attribute formatting                              |
| `singleAttributePerLine`    | `true`     | Better readability for components with many attrs               |

## Implementation (Two Phases)

### Phase 1: Simple Approach (Start Here)

No Lit binding handling - test if Prettier preserves them naturally.

```typescript
/**
 * Formats code for Storybook source display using Prettier.
 * Removes style blocks and cleans empty attribute values.
 */
export const formatHtmlSource = async (source: string): Promise<string> => {
  // 1. Remove <style> tags
  let code = removeStyleTags(source);

  // 2. Format with Prettier
  const prettier = await import("prettier/standalone");
  const prettierPluginHtml = await import("prettier/plugins/html");

  let formatted = await prettier.format(code, {
    parser: "html",
    plugins: [prettierPluginHtml],
    printWidth: 80,
    tabWidth: 2,
    useTabs: false,
    htmlWhitespaceSensitivity: "ignore",
    bracketSameLine: false,
    singleAttributePerLine: true,
  });

  // 3. Clean empty attribute values: attr="" → attr
  return formatted.replace(/(\s[?.@]?\w+)=""/g, "$1");
};
```

### Phase 2: Add Lit Binding Handling (If Phase 1 Fails)

Only implement if Prettier breaks on `?disabled`, `@click`, or `.value`:

```typescript
function preserveLitBindings(code: string): string {
  return code
    .replace(/\?(\w+)=/g, "data-lit-bool-$1=")
    .replace(/@(\w+)=/g, "data-lit-event-$1=")
    .replace(/\.(\w+)=/g, "data-lit-prop-$1=");
}

function restoreLitBindings(code: string): string {
  return code
    .replace(/data-lit-bool-(\w+)=/g, "?$1=")
    .replace(/data-lit-event-(\w+)=/g, "@$1=")
    .replace(/data-lit-prop-(\w+)=/g, ".$1=");
}
```

## Verification

1. Run Storybook and navigate to Components/Button
2. Check the source code in the Docs tab shows:
   - Proper indentation with wrapped attributes
   - Lit bindings (`?disabled`, `@click`) preserved correctly
   - No `<style>` blocks
   - Boolean attributes without `=""`
3. Test with complex nested HTML to verify formatting
