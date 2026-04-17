# Boreal DS — Agent Memory Index

This directory contains non-obvious, durable facts about the codebase, environment, and workflow that future AI sessions must know to operate correctly. Each topic file is self-contained and factual.

---

## Topic Files

### Stencil.js — Form-Associated Custom Elements (FACE)

| File                                            | What it covers                                                                                                                                                                                                                                                                   |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `stencil-face-attach-internals.md`              | `@AttachInternals()` cannot live in a mixin factory — must be declared on the component class body. Runtime failure mode and required pattern.                                                                                                                                   |
| `stencil-face-element-proxy-limits.md`          | Stencil's element proxy blocks native FACE prototype members (`checkValidity`, `reportValidity`, `validity`). All external access must go through `@Method()` wrappers.                                                                                                          |
| `stencil-face-constraint-validation-pattern.md` | How to avoid doubled validation events. The custom element owns validity; the inner `<input>` carries no native constraint attributes. `IFormValidator` / `customValidators` pattern. `formResetCallback` must call `updateValidity()`.                                          |
| `stencil-async-rendering-gotchas.md`            | Stencil batches DOM updates asynchronously — reflected DOM reads in the same tick as a `@Prop()` set return stale values. `formDisabledCallback` trigger conditions. `HTMLButtonElement.prototype.checkValidity` naming collision in `onclick` scope.                            |
| `stencil-face-test-mocks.md`                    | Shared `mocks.ts` location for FACE test doubles. `mockElementInternals()` and `suppressElementInternalsErrors()` pattern. Why `?.` optional chain cannot prevent mock-doc `console.error` on `ElementInternals` property access. Required boilerplate for every FACE spec file. |

### Component API Conventions

| File                                       | What it covers                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `stencil-prop-patterns.md`                 | `stencil/props-must-be-readonly` and `stencil/required-jsdoc` are enforced as errors. `disabled` must use a `@State()` mirror — `mutable: true` on `disabled` causes a Stencil compiler warning and races with the browser's FACE lifecycle. `readonly` + `mutable: true` coexist for non-FACE props only. `instanceof Element` triggers TypeScript narrowing; `nodeType` does not. JSDoc feeds `custom-elements.json`. |
| `feedback_prop_validation_pattern.md`      | Prop validation requires `validatePropValue` + `componentWillLoad()` + stacked `@Watch()` decorators. `@Watch()` alone skips initial attribute values. Pattern adapted from BEEQ reference implementation.                                                                                                                                                                                                              |
| `component-interface-file-naming.md`       | Interface files use `IComponent.ts` (e.g. `ITooltip.ts`), never `IBdsComponent.ts` — the `Bds` prefix is reserved for tag names and class names only.                                                                                                                                                                                                                                                                   |
| `component-accessor-naming-conventions.md` | Getter accessors must not carry a `get` prefix (`placement`, not `getPlacement`); `!x \|\| false` is always redundant — use `!x`.                                                                                                                                                                                                                                                                                       |
| `feedback_event_naming.md`                 | All custom events must use `bds{Action}` camelCase format. Never use native event names (`click`, `change`) — causes type-contract violations, duplicate dispatch, and framework binding collisions.                                                                                                                                                                                                                    |
| `feedback_event_options_explicit.md`       | Bare `@Event()` with no options is the accepted convention. Explicit `bubbles`, `composed`, `cancelable` not required. Aligns with BEEQ and Aqua DS reference implementations. See ADR 0003.                                                                                                                                                                                                                            |

**Boolean prop naming** — `@Prop()` booleans must not carry an `is`, `has`, or `show` prefix. Use single descriptive adjectives that match native HTML attribute style (`disabled`, `closable`, `required`, `counter`). Examples: `hasClear` → `clearable`; `showClose` → `closable`; `hasHeader` → `header`.

**Custom event naming** — `@Event()` names follow `bds{Action}` camelCase. No component noun in the middle (`bdsClose`, not `bdsBannerClose`). Exception: `valueChange` is reserved for Vue `v-model` integration.

---

### Stencil.js — Props, Interfaces, and 2-Way Binding

| File                                 | What it covers                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `stencil-prop-patterns.md`           | `stencil/props-must-be-readonly` and `stencil/required-jsdoc` are enforced as errors. `disabled` must use a `@State()` mirror — `mutable: true` on `disabled` causes a Stencil compiler warning and races with the browser's FACE lifecycle. `readonly` + `mutable: true` coexist for non-FACE props only. `instanceof Element` triggers TypeScript narrowing; `nodeType` does not. JSDoc feeds `custom-elements.json`. |
| `stencil-form-control-interfaces.md` | `IFormControl<T>` composite interface pattern. 2-way binding responsibility split (component vs mixin vs output target). `componentModels` config fields and `eventAttr` gotcha. `IFormAssociatedCallbacks` JSDoc as canonical template.                                                                                                                                                                                |

### Node.js Scripts and Process Management

| File                                | What it covers                                                                                                                                                                                                            |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nodejs-signal-handler-patterns.md` | `spawnSync` is the correct tool for SIGINT/SIGTERM cleanup handlers — async handlers do not complete during teardown. `process.once()` registration. `pnpm install` as the only recovery step after a SIGKILL force-kill. |

### Stencil — Light DOM CSS Patterns

| File                                 | What it covers                                                                                                                                                                                                                                                                                       |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `project_no_shadow_dom.md`           | All components use light DOM only (`shadow: false` or omitted). No shadow boundaries exist. Global CSS applies directly. `composed` event flag is irrelevant. BEEQ shadow-mode patterns must be adapted before adoption. If shadow DOM is introduced, ADR 0003 must be revisited.                    |
| `stencil-light-dom-host-vs-class.md` | When to use `:host` vs a root BEM class in light DOM components. Form controls require `:host` because `[disabled]` and `:focus-visible` must cascade from the host element. Layout/feedback components use a root class. `:host` compilation in light DOM and state-dependent inner style patterns. |

### Stencil — Build Output and Distribution

| File                                      | What it covers                                                                                                                                                                                                                                                              |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `stencil-dist-copy-namespace-behavior.md` | Stencil's `dist` output target places `copy` entries inside `dist/<namespace>/`, not `dist/`. The `postbuild.js` script in `boreal-web-components` promotes files to the paths the export map expects. A stale `dist/` masks the bug — always `rm -rf dist` before testing. |

### scripts-boreal — Packaging Pipeline

| File                              | What it covers                                                                                                                                                                                                                                  |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts-boreal-pack-pipeline.md` | `publish.js` packs artifacts but does not build. Build guarantee comes from Turborepo `dependsOn` in `turbo.json`. Per-framework script suffix convention (`:react`, `:vue`, `:angular`). `validate:all` aggregator and `release:all` sequence. |

### Turborepo — Dev Task Behavior

| File                                       | What it covers                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `turbo-persistent-interactive-pty-hang.md` | `persistent: true` implies `interactive: true` by default — deadlocks silently in headless/CI environments and on Windows with a cold daemon. Fix: add `"interactive": false` explicitly, and bypass Turbo entirely in root `dev:components`/`dev:docs` scripts. Also covers the race condition caused by `dev` scripts that alias `build`. |

### Sass — Path Resolution

| File                                  | What it covers                                                                                                                                                                                                                                                                                      |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sass-paths-windows-forward-slash.md` | Sass treats backslashes as escape characters — all paths in `injectGlobalPaths` and `includePaths` must use forward slashes. Apply `.map(p => p.replace(/\\/g, '/'))` at the array level. Also covers why `require.resolve` is unreliable for locating pnpm workspace packages on Windows/Linux CI. |

### CI Debugging Techniques

| File                                        | What it covers                                                                                                                                                                                                                                        |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `github-actions-windows-debug-technique.md` | Using temporary `workflow_dispatch` workflows on `windows-latest`/`ubuntu-latest` runners to reproduce platform-specific bugs. `timeout-minutes` + `continue-on-error` pattern. Using `.git/info/exclude` to keep debug workflows off local branches. |

### DOM and Accessibility

| File                                    | What it covers                                                                                                                                                                                                 |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dom-setattribute-aria-kebab-case.md`   | `setAttribute` requires kebab-case for ARIA attributes (`aria-describedby`, not `ariaDescribedBy`) — camelCase writes a non-standard attribute that screen readers ignore. Bug confirmed in `bds-tooltip.tsx`. |
| `mouseleave-relatedtarget-vs-target.md` | `mouseleave` "stay on hover" logic must use `e.relatedTarget` (where the pointer is going), not `e.target` (element being left). `bds-tooltip.tsx` has this bug unfixed as of 2026-04-13.                      |

### TypeScript

| File                                                 | What it covers                                                                                                                                         |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `typescript-popover-api-declare-global-redundant.md` | `declare global { interface HTMLElement { showPopover()... } }` is dead code since TypeScript 5.2 — delete any such blocks; the project uses `^5.9.3`. |

### Storybook + Vite

| File                       | What it covers                                                                              |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| `storybook-vite-quirks.md` | Vite glob export limitation workaround and esm-es5 warning suppression in Storybook config. |

### Chromatic Deployment

| File                      | What it covers                                                                                                                                                                                                                                                                                      |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `chromatic-deployment.md` | pnpm does not load `.env` files — use `dotenv-cli`; two-actor model (dotenv-cli vs Chromatic CLI); `--storybook-build-dir` vs `--build-script-name`; Turborepo output caching requirement for `storybook-static/**`; token storage pattern; why Chromatic quickstart bypasses the dependency chain. |

### release-it + pnpm Publish

| File                         | What it covers                                                                                                                                                                                                                                                                                                                            |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `release-it-pnpm-publish.md` | `publishCommand` is silently ignored by release-it — use `publishPackageManager: "pnpm"` and `publishArgs` instead. Full pnpm workspace protocol replacement mechanics. Why `workspace:*` (exact pin) is correct for alpha. Why internal deps belong in `dependencies` not `peerDependencies`. Sequence diagram of the full publish flow. |

---

## Related ADRs

| ADR                                                                              | Decision                                                                                                                                                                           |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.ai/decisions/0001-attach-internals-must-be-on-component-class-not-in-mixin.md` | Full trade-off analysis for `@AttachInternals()` placement. Accepted: declare on component class, never in mixin.                                                                  |
| `.ai/decisions/0002-iform-control-composite-interface-for-form-components.md`    | `IFormControl<T>` composite interface (`IFormAssociatedCallbacks & IFormValueEmitter<T>`) is the single type all form controls implement. Enforces FACE + event contract together. |

---

## Related Plans

| Plan                                     | Status                                                                                                                                                                                                                   |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `.ai/plans/EOA-10099-form-foundation.md` | Form foundation architecture. Phase 1 complete. Phase 2 (SCSS partial, `textInputMixin`, `selectableMixin`) deferred to after `boreal-styleguidelines` token integration.                                                |
| `.ai/plans/EOA-10057-bds-text-field.md`  | `bds-text-field` full implementation. Tasks 1 (types) and 2 (TSX logic) complete. Tasks 3–7 (SCSS partial, token audit, styles, tests, stories) remaining. Component lives under `src/components/forms/bds-text-field/`. |

---

## Changelog

- 2026-02-27 — Initial memory directory created. Four topic files added covering Stencil FACE constraints discovered during `bds-text-field` / `formAssociatedMixin` implementation (EOA-10099).
- 2026-03-03 — Two new topic files added: `stencil-prop-patterns.md` (readonly + JSDoc enforcement, mutable coexistence, instanceof narrowing) and `stencil-form-control-interfaces.md` (IFormControl<T> pattern, 2-way binding architecture, componentModels config). ADR-0002 added covering the IFormControl<T> composite interface decision. Source: PR review on EOA-10230.
- 2026-03-03 — New topic file added: `storybook-vite-quirks.md` (Vite glob export limitation and esm-es5 warning suppression). Captured from inline comments removed from `apps/boreal-docs/.storybook/main.ts`.
- 2026-03-06 — `stencil-prop-patterns.md` extended: `@internal` in a component class JSDoc silently excludes the entire component from `custom-elements.json` and all output target wrappers. Confirmed on `bds-banner`. Never use `@internal` at class level. Ref: https://custom-elements-manifest.open-wc.org/analyzer/getting-started/#supported-jsdoc
- 2026-03-06 — `stencil-prop-patterns.md` extended: `@element` and `@method` class-level JSDoc tags are silently ignored by the CEM analyzer — decorators are the sole source of truth. `@fileoverview` flagged by ESLint; `@file` is the correct tag. Source: EOA-10230 JSDoc cleanup session.
- 2026-03-06 — New topic file added: `nodejs-signal-handler-patterns.md`. Covers `spawnSync` as the correct approach for SIGINT/SIGTERM cleanup (async handlers do not complete during teardown), `process.once()` dual-signal registration, and `pnpm install` as the only recovery step after a SIGKILL force-kill. Source: EOA-10230 `scripts-boreal/bin/publish.js` fix.
- 2026-03-10 — Two new topic files added. `stencil-dist-copy-namespace-behavior.md`: Stencil places `dist` copy entries under `dist/<namespace>/`; `postbuild.js` promotes them to the export-map-expected paths; stale `dist/` masks missing files. `scripts-boreal-pack-pipeline.md`: `publish.js` packs only; builds are guaranteed by Turborepo `dependsOn`; per-framework suffix convention for all pack/validate scripts; `validate:all` and updated `release:all` sequence. Source: EOA-10230 deployment and publishing session.
- 2026-03-10 — New topic file added: `release-it-pnpm-publish.md`. Covers: `publishCommand` being silently ignored by release-it 19.2.4 (the correct fields are `publishPackageManager` and `publishArgs`); pnpm workspace protocol replacement happening at tarball creation time only; `workspace:*` exact-pin rationale for alpha; `dependencies` vs `peerDependencies` for internal packages; full publish flow sequence diagram. Source: first alpha release session.
- 2026-03-11 — New topic file added: `chromatic-deployment.md`. Covers: pnpm does not auto-load `.env` files (use `dotenv-cli`); two-actor model separating dotenv-cli from the Chromatic CLI; `--storybook-build-dir` vs `--build-script-name` and why Turborepo must own the build step; `storybook-static/**` must be declared in Turborepo build outputs to survive cache hits; token storage pattern (`.env` gitignored, `.env.example` committed); why Chromatic's quickstart pattern bypasses the dependency chain. Source: EOA-10749 Chromatic deployment session.
- 2026-03-13 — `stencil-prop-patterns.md` updated: `mutable: true` on `disabled` produces a Stencil compiler warning and can race with the browser's FACE lifecycle. Correct pattern is a `@State()` mirror (`isDisabled`) written by both `@Watch('disabled')` and `formDisabledCallback`. `mutable: true` with narrow cast remains valid for non-FACE props. Source: EOA-10056 bds-checkbox code review.
- 2026-03-13 — New topic file added: `stencil-face-test-mocks.md`. Covers: shared `mocks.ts` location for FACE test doubles; `mockElementInternals()` and `suppressElementInternalsErrors()` exports; why optional-chain guards cannot prevent mock-doc `console.error` on `ElementInternals` property access; required boilerplate for every FACE spec file. Source: EOA-10056 bds-checkbox code review.
- 2026-03-13 — New topic file added: `stencil-light-dom-host-vs-class.md`. Covers: when to use `:host` vs a root BEM class in light DOM Stencil components; form controls require `:host` because `[disabled]` reflects on the host and `:focus-visible` must cascade outward; `:host` compilation in light DOM; state-dependent inner style pattern. Source: EOA-10056 bds-checkbox code review.
- 2026-03-17 — `bds-text-field` component created (EOA-10057). Tasks 1 (types: `ITextField.ts`, `enum.ts`, `types.ts`) and 2 (full TSX logic: all props, events, FACE callbacks, validation wiring) are complete. Component placed under `src/components/forms/bds-text-field/` in the `forms` category, matching the plopfile category convention. Remaining: shared SCSS partial (Task 3), Figma token audit (Task 4), SCSS styles (Task 5), unit tests (Task 6), Storybook stories + MDX (Task 7). Stories will be scaffolded via `pnpm generate:story` under `src/stories/forms/bds-text-field/`.
- 2026-04-13 — Five new topic files added from overlay component review pass (`bds-tooltip`, `bds-popover`). `component-interface-file-naming.md`: `IComponent.ts` not `IBdsComponent.ts`. `component-accessor-naming-conventions.md`: no `get` prefix on getters; `!x || false` is always `!x`. `dom-setattribute-aria-kebab-case.md`: `setAttribute` requires kebab-case ARIA names; camelCase variant is an a11y regression. `mouseleave-relatedtarget-vs-target.md`: `stayOnHover` requires `e.relatedTarget`, not `e.target` — bug confirmed unfixed in `bds-tooltip.tsx`. `typescript-popover-api-declare-global-redundant.md`: `declare global` Popover API augmentation is dead code since TS 5.2.
- 2026-04-08 — Three new topic files added from Windows-specific `pnpm dev:components` hang debugging session. `turbo-persistent-interactive-pty-hang.md`: Turbo `persistent: true` silently deadlocks in headless/CI environments; fix is `"interactive": false` plus bypassing Turbo in `dev:components`/`dev:docs` scripts; also covers the `dev`-as-alias-for-`build` race condition. `sass-paths-windows-forward-slash.md`: Sass cannot parse backslash paths; apply `.map(p => p.replace(/\\/g, '/'))` to all Sass path arrays; `require.resolve` is unreliable for pnpm workspace package resolution on Windows/Linux. `github-actions-windows-debug-technique.md`: using `workflow_dispatch` workflows with `timeout-minutes` + `continue-on-error` for platform-specific bug reproduction; `.git/info/exclude` pattern to keep debug workflows off local branches.
