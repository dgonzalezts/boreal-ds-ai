# Storybook Action Wiring for Web Component Stories

Wiring Storybook `action()` to custom DOM events in Lit/web component stories requires four consistent levels. Getting any one wrong produces silent failures or unreadable Actions panel output.

## The four-level pattern

### 1. Type declaration

```typescript
type StoryArgs = {
  bdsChange?: (payload: { detail: string; from: string; bubbles: boolean }) => void;
};
```

The payload type must match exactly what the arrow function in the template binding extracts. `() => void` (no parameters) is incorrect — TypeScript will not catch misuse at call sites.

### 2. argTypes

```typescript
argTypes: {
  bdsChange: {
    description: 'Emitted when the selected value changes. `detail` carries the value key.',
    table: {
      category: 'Events',
      type: { summary: 'CustomEvent<string>' },
    },
    // Do NOT add `action: 'bdsChange'` here.
    // That is the legacy shorthand and is silently ignored by Storybook
    // when `args` already provides the function. Having both is dead weight.
  },
}
```

### 3. args (the explicit approach — matches Storybook #action docs)

```typescript
import { action } from 'storybook/actions';

args: {
  bdsChange: action('bdsChange'),
},
```

`action('name')` creates a variadic logger: every argument passed to it appears in the Actions panel. The more modern alternative is `fn().mockName('bdsChange')` from `storybook/test`, which additionally works as a Jest/Vitest spy inside `play()` interaction tests.

### 4. Template event binding

```typescript
@bdsChange=${(e: CustomEvent<string>) => args.bdsChange?.({ detail: e.detail, from: (e.target as Element).localName, bubbles: e.bubbles })}
```

The `?.` optional chain is required — `args.bdsChange` is `undefined` in snapshot tests or when the addon is not loaded.

## Why the arrow function wrapper is mandatory

Direct binding `@bdsChange=${args.bdsChange}` passes the raw `CustomEvent` object to `action()`. Storybook's serialiser cannot read it: `detail`, `target`, `bubbles`, and `type` are all **prototype accessor properties** on `Event.prototype` / `CustomEvent.prototype`, not own enumerable keys. This is identical to `JSON.stringify(event)` returning `"{}"`. The serialiser detects a class instance and produces only:

```
{ __isClassInstance__: true, __className__: "CustomEvent", isTrusted: false }
```

The arrow function wrapper extracts the needed data into a plain serialisable object before passing it to the logger.

## Payload convention

| Field | When to include |
|---|---|
| `detail` | Always — it is the primary payload channel in the DOM custom event spec |
| `from: (e.target as Element).localName` | Composite components only — identifies which child element originated the event |
| `bubbles: e.bubbles` | Composite components with a known event-boundary bug — confirms propagation behaviour |

For standalone components (single event source), just pass `e.detail` directly:
```typescript
@bdsChange=${(e: CustomEvent<string>) => args.bdsChange?.(e.detail)}
```

## Legacy shorthand summary

| Approach | Where | Storybook version | Accessible in play()? |
|---|---|---|---|
| `argTypes: { event: { action: 'label' } }` | argTypes | Oldest | No |
| `args: { event: action('label') }` | args | Current | No |
| `args: { event: fn().mockName('label') }` | args | Recommended | Yes |

Reference story: `apps/boreal-docs/src/stories/forms/bds-select/bds-select.stories.ts`
Discovered during: `bds-select` QA session — Actions panel showed `__isClassInstance__` when direct binding was used.
