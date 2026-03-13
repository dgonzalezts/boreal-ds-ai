# Common Antipatterns

## Overview

This reference captures recurring review failures in the Boreal DS monorepo, with emphasis on Stencil web components and the release pipeline.

---

## Stencil and CEM Antipatterns

- **Missing JSDoc on `@Prop()`**: Violates `stencil/required-jsdoc` and degrades `custom-elements.json`.
- **Non-`readonly` props**: Violates `stencil/props-must-be-readonly`.
- **Class-level `@internal`**: Removes the entire component from the CEM and breaks wrapper generation.
- **Using `@element` or `@method` in class JSDoc**: Ignored by the CEM analyzer, gives a false sense of documentation.
- **Using `@fileoverview`**: Fails lint rules; use `@file` instead.

---

## Events and API Antipatterns

- **Native event names (`click`, `change`, `input`)**: Collides with native events and framework bindings.
- **Undocumented `@Event()` fields**: Event payload types should be explicit for CEM consumers.

---

## FACE (Form-Associated) Antipatterns

- **`@AttachInternals()` inside a mixin**: Compiles but yields `undefined` at runtime.
- **Calling `internals` from outside the component**: Stencil proxy blocks it; requires `@Method()` wrappers.
- **Using native constraint attrs on inner `<input>`**: Causes double validation events and focus errors.
- **Skipping `updateValidity()` after reset/restore**: Leaves validity state stale.
- **`mutable: true` on `disabled`**: Stencil warns and creates two writers on the same reflected attribute (the component and the browser via `formDisabledCallback`). Use `@State() private isDisabled` as the internal working copy instead.
- **`@Prop()` declarations in a mixin factory**: Stencil's compiler does not pick up `@Prop()` decorators from mixin base classes. Props must be declared directly on the component class — the mixin ends up with an ignored duplicate copy requiring a comment to explain why.
- **No-op constructor in a mixin factory to silence ESLint**: `constructor(...args: any[]) { super(...args); }` does nothing — it is identical to the implicit call. The `any` originates from Stencil's own `MixedInCtor` type. The correct fix is a scoped override in `eslint.config.ts` for `**/mixins/**/*.ts`, not `eslint-disable` comments on a dead constructor.

---

## Rendering and Testing Antipatterns

- **Reading reflected DOM state immediately after setting props**: Stencil updates asynchronously; tests need `waitForChanges()`.
- **Using `form.disabled` in tests**: No effect; only `<fieldset disabled>` triggers `formDisabledCallback`.
- **Assuming Shadow DOM**: Boreal uses light DOM; parts and composed events are not a substitute.

---

## Build and Release Antipatterns

- **Disabling `postbuild` for web-components**: Breaks `dist/css` and `dist/scss` export paths.
- **Testing dist without cleaning**: Stale `dist/` masks missing files.
- **Using `publishCommand` in release-it**: Silently ignored, falls back to `npm publish`.
- **Moving internal deps to `peerDependencies`**: Forces consumers to install manually and breaks alpha flow.
- **Bypassing Turbo build graph in packaging scripts**: Produces incomplete artifacts.

---

## Docs and Storybook Antipatterns

- **Chromatic CLI builds Storybook directly**: Bypasses Turbo dependency order.
- **Missing `storybook-static/**` outputs in Turbo\*\*: Cache hits omit the directory and uploads fail.
- **No `dotenv --` for Chromatic**: `CHROMATIC_PROJECT_TOKEN` not loaded.

---

## TypeScript and Safety Antipatterns

- **Broad `any` or unsafe casts**: Hides contract issues and breaks editor tooling.
- **`nodeType` element checks**: Do not narrow types; prefer `instanceof Element`.
