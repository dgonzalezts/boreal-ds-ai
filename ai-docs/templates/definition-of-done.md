# Definition of Done Checklist for Boreal Components

## 📋 **Pre-Development**

- [ ] Figma design received and reviewed with UX/UI team
  - [ ] Ensure Figma covers all scenarios described in the Jira ticket (EOA)
  - [ ] Ensure Figma provides designs for all scenarios of a component (if Slots, that we can see each slot in each state; eg: if component includes checkbox, see checkbox all its states)
- [ ] Component classified (Atom/Molecule/Organism) and API defined
- [ ] WBS (EOA tickets) are created for the component and ready for grooming
  - [ ] Good component specific Acceptance Criteria is added
  - [ ] When possible, also provide Dev Notes to help the developer that will be taking the ticket
  - [ ] File structure planned following naming conventions (`bds-[name]`)

## 🔧 **Development**

- [ ] All `@Prop()` declarations are `readonly` and have a JSDoc block
- [ ] Boolean prop names use descriptive adjectives — no `is`/`has`/`show` prefix (e.g. `disabled`, `closable`, `error`)
- [ ] All properties defined with explicit TypeScript types — no `any`
- [ ] Design tokens used exclusively via `var(--boreal-*)` in SCSS — no hard-coded colours, spacing, or radii
- [ ] Basic accessibility implemented (ARIA attributes, keyboard support)
- [ ] Custom events named with `bds{Action}` camelCase pattern (e.g. `bdsChange`, `bdsClick`)
- [ ] Events use bare `@Event()` — no explicit `bubbles`/`composed`/`cancelable`
- [ ] FACE components: `@AttachInternals()` on the class body; `checkValidity()` and `reportValidity()` exposed via `@Method()`; `formResetCallback` and `formStateRestoreCallback` implemented
- [ ] No inline comments (`//` or `/* */`) explaining what code does — JSDoc on exported public API only
- [ ] No ESLint or TypeScript errors

## 🧪 **Testing**

- [ ] ≥ 90% statement coverage achieved using `@stencil/core/testing` (`newSpecPage` + Vitest)
  - [ ] Spec files split by concern: `basics`, `a11y`, `events`, `variants`, `slots` (create only those that apply)
  - [ ] All async assertions use `waitForChanges()` before reading DOM state
- [ ] ≥ 90% mutation score confirmed after coverage gate passes
- [ ] Component tested in React and Vue examples (`examples/react-testapp`, `examples/vue-testapp`)
- [ ] Manual visual testing completed:
  - [ ] Tested in Chrome and Firefox/Safari
  - [ ] All component states tested (default, hover, focus, error, disabled)
  - [ ] Component matches Figma design within 2px tolerance
  - [ ] Keyboard navigation verified
  - [ ] Responsive breakpoints tested
  - [ ] Works with all existing themes
  - [ ] Cross-browser compatibility verified
- [ ] Code reviewed and approved by peer developers
- [ ] No Action Items/Tasks in PR left open

## 📚 **Documentation**

- [ ] Storybook MDX file created with required sections:
  - [ ] How to use it / When to use it / Component preview / Properties / Actions
- [ ] Stories created: Default, variants, states, interactive examples
- [ ] Code examples include installation and usage instructions
- [ ] Common usage patterns documented
  - [ ] Specially when working with components that “nest” other components, since we are avoiding it when we create the components these are meant to be handled on implementation, so please provide good scenario coverage to give developers a quick code snippet they can easily copy&paste
- [ ] Breaking changes documented with migration path (if applicable)

## 🔍 **Review & Release**

- [ ] Code reviewed by peer developer
- [ ] UX/UI team validation completed
- [ ] Commit message follows `type(scope): TICKET-ID description` convention via `pnpm commit`
- [ ] CEM (`custom-elements.json`) integrity verified — JSDoc changes do not break generation
- [ ] Bundle size impact documented and acceptable
- [ ] Performance verified (component renders in <100ms on average hardware)
- [ ] CHANGELOG.md updated with appropriate semantic version
- [ ] Breaking changes communicated to team (if applicable)
- [ ] Backwards compatibility verified with consuming applications (`validate:pack` passes)
- [ ] Published following existing process
