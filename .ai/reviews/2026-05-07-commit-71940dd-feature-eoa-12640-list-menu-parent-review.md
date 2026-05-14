# Boreal DS — Code Review Report

**Generated:** 2026-05-07T14:09:33  
**Base ref:** `main`  
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-react (React wrapper)** — checklist section(s): B
- **boreal-vue (Vue wrapper)** — checklist section(s): B
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `apps/boreal-docs/src/utils/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `apps/boreal-docs/src/utils/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `apps/boreal-docs/src/utils/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `apps/boreal-docs/src/utils/index.ts:4`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/generate.ts:50`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/generate.ts:51`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/scss-generator.ts:15`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/scss-generator.ts:36`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/scss-generator.ts:38`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/scss-generator.ts:45`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/scss-generator.ts:69`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/scss-generator.ts:72`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/scss-generator.ts:74`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/scss-generator.ts:111`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/scss-generator.ts:123`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/scss-generator.ts:124`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/scss-generator.ts:144`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/token-processor.ts:12`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/token-processor.ts:24`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/token-processor.ts:38`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/token-processor.ts:43`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/token-processor.ts:143`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/token-processor.ts:173`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-styleguidelines/src/generators/token-processor.ts:203`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/actions/bds-button/bds-button.tsx:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/actions/bds-button/bds-button.tsx:5`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/actions/bds-button/bds-button.tsx:6`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/actions/bds-button/bds-button.tsx:193`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:64`
- 🔴 **[event-name-format]** @Event() name 'readonly' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:97`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:3`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:9`
- 🔴 **[event-name-format]** @Event() name 'readonly' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu/bds-list-menu.tsx:43`
- 🔴 **[event-name-format]** @Event() name 'readonly' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu/bds-list-menu.tsx:46`
- 🟡 **[class-jsdoc-invalid-tags]** Component class JSDoc uses `@element` or `@method` tags — ignored by the CEM analyzer. Use method-level JSDoc instead. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu/bds-list-menu.tsx`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu/bds-list-menu.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu/bds-list-menu.tsx:5`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/actions/bds-toggle/bds-toggle.tsx:103`
- 🔴 **[face-native-constraint-on-input]** Inner <input> carries native constraint attribute `required`. Ownership of validity must stay with `ElementInternals.setValidity()`. `packages/boreal-web-components/src/components/actions/bds-toggle/bds-toggle.tsx`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/actions/bds-toggle/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/actions/bds-toggle/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/actions/bds-toggle/types/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/actions/bds-toggle/types/index.ts:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-badge/bds-badge.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-badge/bds-badge.tsx:5`
- 🟡 **[class-jsdoc-invalid-tags]** Component class JSDoc uses `@element` or `@method` tags — ignored by the CEM analyzer. Use method-level JSDoc instead. `packages/boreal-web-components/src/components/feedback/bds-banner/bds-banner.tsx`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-banner/bds-banner.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-banner/bds-banner.tsx:5`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-spinner/bds-spinner.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-spinner/bds-spinner.tsx:5`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/feedback/bds-spinner/bds-spinner.tsx:53`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-status/bds-status.tsx:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-status/bds-status.tsx:5`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-tag/bds-tag.tsx:4`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/feedback/bds-tag/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/feedback/bds-tag/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/feedback/bds-tag/types/index.ts:3`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox.tsx:70`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox.tsx:89`
- 🟡 **[face-reset-no-validity]** `formResetCallback` is defined but `updateValidity()` or `setValidity()` is not called — validity state may be stale after reset. `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox.tsx`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/forms/bds-flag/bds-flag.tsx:63`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/forms/bds-flag/bds-flag.tsx:71`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/forms/bds-flag/bds-flag.tsx:78`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-flag/constants/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-flag/constants/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-flag/constants/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-flag/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-flag/types/index.ts:2`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx:98`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx:188`
- 🔴 **[face-native-constraint-on-input]** Inner <input> carries native constraint attribute `required`. Ownership of validity must stay with `ElementInternals.setValidity()`. `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/helpers/bds-divider.tsx:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/helpers/bds-divider.tsx:6`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/images-icons/bds-avatar/bds-avatar.tsx:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/images-icons/bds-avatar/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/images-icons/bds-avatar/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/images-icons/bds-avatar/types/index.ts:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/layouts/bds-grid/grid-item/bds-grid-item.tsx:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/layouts/bds-grid/grid-item/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/layouts/bds-grid/grid-item/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/layouts/bds-grid/grid-item/types/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/layouts/bds-grid/grid/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/layouts/bds-grid/grid/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/layouts/bds-grid/grid/types/index.ts:3`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/overlays/bds-dialog/bds-dialog.tsx:4`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/overlays/bds-dialog/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/overlays/bds-dialog/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/overlays/bds-dialog/types/index.ts:3`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:57`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:3`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:6`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:7`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:9`
- 🔴 **[aria-camel-set-attr]** `setAttribute` called with a camelCase ARIA attribute name. Use kebab-case: `setAttribute('aria-describedby', ...)` not `setAttribute('ariaDescribedBy', ...)`. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:261`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:312`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:5`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:7`
- 🔴 **[aria-camel-set-attr]** `setAttribute` called with a camelCase ARIA attribute name. Use kebab-case: `setAttribute('aria-describedby', ...)` not `setAttribute('ariaDescribedBy', ...)`. `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:175`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:102`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/titles-text/bds-typography/bds-typography.tsx:7`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/titles-text/bds-typography/bds-typography.tsx:140`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/mixins/anchored.mixin.ts:2`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/mixins/anchored.mixin.ts:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/mixins/anchored.mixin.ts:5`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/mixins/anchored.mixin.ts:6`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/mixins/anchored.mixin.ts:7`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/mixins/anchored.mixin.ts:8`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/mixins/backdrop.mixin.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/mixins/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/mixins/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/mixins/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/mixins/index.ts:4`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/mixins/index.ts:5`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/mixins/index.ts:6`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/mixins/links.mixin.ts:2`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/mixins/links.mixin.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/services/floating/interfaces/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/services/floating/interfaces/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/services/floating/interfaces/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/services/floating/interfaces/index.ts:4`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/services/floating/interfaces/index.ts:5`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:4`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:5`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:6`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:7`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:8`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/index.ts:4`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/index.ts:5`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/index.ts:6`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/index.ts:7`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/menu/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/index.ts:4`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-web-components/src/utils/testing/mocks/backdrop-mock.ts:17`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-web-components/src/utils/testing/mocks/backdrop-mock.ts:18`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-web-components/src/utils/testing/mocks/backdrop.ts:17`
- 🟡 **[unsafe-any]** Broad `any` usage detected. Use a specific type or narrow cast with justification. `packages/boreal-web-components/src/utils/testing/mocks/backdrop.ts:18`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/mocks/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/mocks/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/mocks/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/mocks/index.ts:4`

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ❌ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ✅ Storybook/MDX/README updated when behavior or APIs change
- ✅ Public APIs, events, and props follow naming conventions

### A — Stencil (boreal-web-components)

- ❌ Every @Prop() has `readonly` and an adjacent JSDoc block
  - **Standard:** Every `@Prop()` must be `readonly` and have a JSDoc block directly above it.
  - **Antipattern:** `bds-list-menu-item.tsx` uses `mutable: true` on `selected` (no `readonly`); script also flagged a possible missing JSDoc on `checkable` at line 64 — verify whether the JSDoc is adjacent enough for the parser.
- ❌ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
  - **Standard:** Use `@Prop({ reflect: true }) readonly selected` + `@State() private isSelected` mirror. Write to state in `@Watch` and event handlers, never to the prop directly.
  - **Antipattern:** `mutable: true` creates two writers on the same reflected attribute — the parent (via binding) and the child (via `this.selected = ...`) — causing race conditions when the parent re-renders.
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
  - **Standard:** Use bare `@Event()` with no explicit `bubbles`/`composed`/`cancelable` options (see ADR `.ai/decisions/0003-event-options-convention.md`). The `[event-name-format]` failures on `bds-list-menu` files are false positives — the script parsed `readonly` as the event name instead of the actual name (`bdsChange`, `bdsSelect`, `bdsSelectItem`).
  - **Antipattern:** `@Event({ bubbles: true, composed: true })` — explicit options deviate from the project convention without benefit.
- ✅ Event names do not reuse native DOM events
- ✅ @AttachInternals() is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via @Method()
- ❌ Only ElementInternals.setValidity() manages validity
- ❌ `formResetCallback` and `formStateRestoreCallback` call updateValidity()
- ❌ JSDoc changes preserve custom-elements.json generation accuracy
  - **Standard:** Do not use `@element` or `@method` in the component class JSDoc — these are ignored by the CEM analyzer. Use method-level JSDoc on each `@Method()` instead (which is already done; the class-level `@method` tags are redundant noise).
  - **Antipattern:** Class-level `@method` tags give a false sense of documentation without contributing to the generated `custom-elements.json`.
- ✅ Boolean @Prop() names use no `is`/`has`/`show` prefix
- ✅ Props declared on component class, not inside mixin factory
- ✅ No no-op constructor in mixin factory (use ESLint override instead)
- ❌ ARIA attribute names passed to `setAttribute` are kebab-case
- ✅ No dead `declare global` Popover API blocks (redundant since TS 5.2)
- ✅ Interface files named `IComponent.ts`, not `IBdsComponent.ts`
- ❌ Getter accessors carry no redundant `get` prefix

### B — React/Vue Wrappers

- ✅ Generated outputs/types rebuilt when web components change
- ✅ @telesign/boreal-web-components stays in `dependencies`
- ✅ Uses `publishPackageManager: pnpm` with `publishArgs`

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

## Memory-Guided Review

### Event naming — `feedback_custom_events_naming.md`

`bdsChange`, `bdsSelect`, and `bdsSelectItem` all follow the `bds{Action}` pattern with no component noun embedded in the middle (e.g. not `bdsListMenuChange`). ✅ No issues.

### Boolean prop naming — `feedback_boolean_prop_naming.md`

All boolean props use clean adjective form: `disabled`, `selected`, `checkable`, `selectControls`. None use the `is`/`has`/`show` prefix. ✅ No issues.

### Getter accessor naming — `component-accessor-naming-conventions.md`

`childItems`, `firstEnabledItem`, `isMultiple`, `menuItemRoleExtended`, `isLabelVariant`, `classMap` — none carry a redundant `get` prefix. ✅ No issues.

### Prop validation pattern — `coding_standards.md`

Both components correctly implement the three-part pattern: `validatePropValue` + stacked `@Watch()` + `componentWillLoad()` call. ✅ No issues.

### Form control interfaces — `stencil-form-control-interfaces.md`

`bds-list-menu` and `bds-list-menu-item` are not form-associated elements. `IFormControl<T>` and `componentModels` registration do not apply. ✅ Not applicable.

### `mutable: true` antipattern — `common_antipatterns.md`

⚠️ **`bds-list-menu-item.tsx`** uses `mutable: true` on `selected`. This is the highest-risk finding: the parent calls `updateChildrenState()` which sets `item.selected = isSelected` on each child. If `selected` is also mutated internally (in `handleClick` for the non-listbox checkable path), the two writers race on the same reflected attribute. Resolving this with a `@State()` mirror also fixes the stale-value emit bug in `handleClick` (finding #7 in this report).

### SCSS `mouseleave` / `relatedTarget` — `mouseleave-relatedtarget-vs-target.md`

No `mouseleave` handlers in the list-menu components. ✅ Not applicable.

---

**Memory topic files consulted:**
- `feedback_custom_events_naming.md`
- `feedback_boolean_prop_naming.md`
- `component-accessor-naming-conventions.md`
- `stencil-form-control-interfaces.md`
- `common_antipatterns.md` (mutable prop section)
- `mouseleave-relatedtarget-vs-target.md`

---

## Additional Manual Findings (Beyond Automated Scan)

The following issues were found by reading the code directly and are not reported by the static analyzer:

| # | Severity | Location | Finding |
|---|----------|----------|---------|
| M1 | ⚠️ Bug | `bds-list-menu-item.tsx` `handleClick` | Emits `selected: !this.selected` AFTER mutating the prop — the detail carries the pre-toggle state when `checkable && parentRole !== LISTBOX` |
| M2 | ⚠️ Type | `bds-list-menu.tsx` `getSelectedValues` | Return type is `Promise<string \| string[]>` but `selectedValues[0]` on an empty array yields `undefined`; should be `Promise<string \| string[] \| undefined>` |
| M3 | ⚠️ Style | `bds-list-menu.tsx` line ~137 + render | `==` used instead of `===` for string comparisons |
| M4 | ⚠️ Style | `bds-list-menu.tsx` `updateChildrenState` | `forEach` callback param `item` shadows the method param `item`; rename loop var to `child` |
| M5 | ⚠️ Test | `bds-list-menu-methods.spec.tsx` | `setSelectedValues` called without `await`; no `waitForChanges()` before assertions |
| M6 | ⚠️ Test | `bds-list-menu-methods.spec.tsx` | `root as any` — use `root as HTMLBdsListMenuElement` for typed method calls |
| M7 | ⚠️ Test | `bds-list-menu/__test__/` | File named `bds-list-menu-ay11.spec.tsx` — typo, should be `bds-list-menu-a11y.spec.tsx` |
| M8 | ⚠️ Coverage | `bds-list-menu-item` | No tests for `checkable` prop: `renderCheckbox()`, `aria-checked`, checkbox visibility |
| M9 | ⚠️ Coverage | `bds-list-menu` | No tests for `selectControls` (Select All / Deselect All) feature |
| M10 | ⚠️ Style | `bds-list-menu.scss` | Two `// TODO:` comments — track as tasks, do not commit TODO comments |

---

**Result: 21 passed · 9 failed**

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_