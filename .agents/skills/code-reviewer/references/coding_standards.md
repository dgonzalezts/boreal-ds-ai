# Coding Standards

## Overview

This reference summarizes Boreal DS standards reviewers should enforce across the monorepo, with Stencil web components as the primary constraint set.

---

## Stencil Component Standards

### Import Order

Imports in Stencil component files must follow this order:

1. **Framework** — `@stencil/core` and any third-party `node_modules`
2. **Internal aliases** (`@/...`) — ordered by abstraction layer, most abstract first:
   - `@/services` — pure logic, no DOM dependency
   - `@/mixins` — compose services into Stencil behaviour
   - `@/utils` — constants and helpers
3. **Local/relative** (`./` or `../`) — component-specific types, interfaces, assets

Dependencies flow downward — each group only imports from groups above it.

### Barrel Exports and Tree-Shaking

Internal barrels (`@/services`, `@/mixins`, `@/utils`) are resolved at compile time and are safe for internal use. To protect the published package's tree-shakability:

- Only barrel-export what belongs to the contract of that layer. Do not re-export every internal utility for convenience.
- Prefer named re-exports (`export { X } from './X'`) over wildcard re-exports (`export * from './X'`).
- Never use `export *` from a module that has side effects — Rollup may retain the entire module.
- Components never barrel-export each other. Stencil's lazy-loading splits each component into its own chunk; cross-component barrel imports defeat this.

### Props and JSDoc

- Every `@Prop()` must be `readonly` and have a JSDoc block directly above it.
- Use `@file` for module-level JSDoc. Do not use `@fileoverview`.
- Do not place `@internal`, `@element`, or `@method` in a component class JSDoc.
- Use method-level JSDoc for `@Method()` declarations.

### Events

- Use prefixed camelCase event names: `bds{Action}`.
- Use bare `@Event()` — no explicit `bubbles`, `composed`, or `cancelable` options required (see ADR `ai-docs/decisions/0003-event-options-convention.md`).
- Avoid native DOM event names (`click`, `change`, `input`).

### FACE (Form-Associated Custom Elements)

- `@AttachInternals()` must be on the component class body, never inside a mixin.
- Wrap `checkValidity()` and `reportValidity()` with `@Method()` so tests and consumers can call them.
- The custom element owns validity via `ElementInternals.setValidity()`; inner inputs do not carry native constraint attrs.
- `formResetCallback` and `formStateRestoreCallback` must call `updateValidity()` after restoring state.

### Rendering and Testing

- Stencil renders asynchronously. Tests must `waitForChanges()` before reading reflected DOM state.
- `formDisabledCallback` is triggered by `<fieldset disabled>`, not `form.disabled`.
- Components use light DOM only. Avoid Shadow DOM assumptions in styles or events.

### Prop Validation

- Use the shared `validatePropValue` + `componentWillLoad()` + stacked `@Watch()` pattern for enum-like props.

```tsx
import { validatePropValue } from "@/utils/helpers/validateProps";

// Section 6 — Property Watchers
@Watch("variant")
@Watch("size")
checkPropValues(): void {
  validatePropValue(Object.values(BUTTON_VARIANTS) as ButtonVariant[], "default", this.el as HTMLElement, "variant");
  validatePropValue(Object.values(BUTTON_SIZES) as ButtonSizes[], "medium", this.el as HTMLElement, "size");
}

// Section 9 — Lifecycle methods
componentWillLoad(): void {
  this.checkPropValues();
}
```

`validatePropValue` resets the prop to `fallbackValue` and issues a `console.warn` when the value is not in `acceptedValues`. After `checkPropValues()` returns, all validated props are guaranteed to hold a valid value. Always pass `Object.values(ENUM)` — never an inline literal array.

---

## Monorepo Build and Release Standards

### Build and Packaging

- Web-components `dist` copy outputs land in `dist/<namespace>/`; `postbuild` must promote to `dist/css` and `dist/scss`.
- Always validate export maps against clean `dist/` builds.
- Packaging scripts in `scripts-boreal` must rely on Turbo `dependsOn` for build guarantees.
- Per-framework scripts must use explicit suffixes (`:react`, `:vue`, `:angular`).

### Publishing

- release-it must use `publishPackageManager: "pnpm"` plus `publishArgs`, not `publishCommand`.
- Internal packages stay in `dependencies`, not `peerDependencies`, during alpha.

### Docs and Storybook

- Chromatic deploys use `dotenv --` and `--storybook-build-dir=storybook-static`.
- `storybook-static/**` must be declared in `turbo.json` outputs.
- Storybook Vite aliasing must keep `@telesign/boreal-web-components/css/*` working.

---

## TypeScript and General Code Quality

- Avoid `any` unless explicitly justified.
- Do not use `mutable: true` on native form attributes (`disabled`, `checked`, `value`). Use a `@State()` mirror instead — `@Prop() readonly disabled` + `@State() private isDisabled` — and write to the state in `formDisabledCallback` and `@Watch`.
- Prefer `instanceof Element` over `nodeType` checks for type narrowing.
- Keep side effects explicit and avoid hidden async work inside render paths.
- Do not add `declare global { interface HTMLElement { showPopover(): void; ... } }` blocks. The Popover API is built into TypeScript's `lib.dom.d.ts` since TS 5.2; any such declaration is dead code and must be deleted.

---

## Naming Conventions

### Interface file naming

Component interface files must be named `IComponent.ts` — e.g. `ITooltip.ts`, `IPopover.ts`. The `Bds` prefix is reserved for tag names and class names only. Never use `IBdsTooltip.ts` or similar.

### Getter accessor naming

Getter accessors must not carry a `get` prefix. Use `placement`, not `getPlacement`; `canShowArrow`, not `getCanShowArrow`. The `get` keyword already communicates accessor semantics.

### Boolean simplification

`!x || false` is always equivalent to `!x` — the `|| false` branch is unreachable. Remove it.

---

## DOM and Accessibility

### ARIA attributes via `setAttribute`

`setAttribute` requires kebab-case ARIA attribute names. Always write:

```ts
trigger.setAttribute('aria-describedby', 'tooltip-content');
trigger.setAttribute('aria-haspopup', 'true');
```

Passing camelCase (`ariaDescribedBy`) creates a non-standard attribute that is ignored by assistive technology.

### `mouseleave` and stayOnHover logic

When implementing "keep the floating element open if the pointer moves into it" (`stayOnHover`), test `e.relatedTarget` (where the pointer is going), not `e.target` (the element being left). `e.target` is always the element that fired the event and does not indicate the destination.

---

## Reviewer Checklist Shortcuts

- JSDoc present on every `@Prop()`, and no class-level `@internal`.
- Event names prefixed; bare `@Event()` is the convention.
- FACE behavior uses `@AttachInternals()` and `@Method()` wrappers.
- Tests wait for render ticks.
- Build artifacts align with export maps after a clean build.
