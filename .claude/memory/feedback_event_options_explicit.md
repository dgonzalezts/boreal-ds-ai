# Stencil — `@Event()` Options Must Always Be Explicit

## Rule

Every `@Event()` decorator in Boreal DS must declare all three flags explicitly:

```ts
@Event({ bubbles: true, composed: true, cancelable: false })
bdsButtonClick!: EventEmitter<{ event: MouseEvent }>;
```

Never omit any of `bubbles`, `composed`, or `cancelable` and rely on Stencil's defaults.

## Why

The `EventOptions` interface in `stencil-public-runtime.d.ts` declares all three flags as `boolean?` (optional). Stencil's source does not publicly document what the fallback value is for each. Relying on undocumented implicit defaults is unsafe: defaults can change between Stencil major versions without a breaking-change notice in a consuming project.

## Flag-by-Flag Rationale

### `bubbles`

Almost always `true` for interaction events. A non-bubbling event cannot be handled at the document or host-application level, which defeats the purpose of the event in most component library consumer patterns.

### `composed`

Set to `true` proactively even though Boreal DS currently uses light DOM (no `shadow: true` on any `@Component` decorator). If Shadow DOM is ever adopted, events that are not `composed: true` silently stop at the Shadow Root boundary and never reach host-application event listeners. Setting this now prevents a silent regression later.

### `cancelable`

`false` is correct for events that represent a completed action (e.g. a click that has already fired). Set to `true` only if consumers need to call `.preventDefault()` to opt out of a side effect — for example, a submit event where the consumer wants to cancel default form submission behavior.

## Relationship to `stopPropagation` Fix

The `cancelable` value for `bdsButtonClick` is currently `false`. An identified open item (see `project_open_items.md`) proposes changing it to `true` so that consumers can cancel click-triggered navigation or other side effects. That change is not yet implemented.
