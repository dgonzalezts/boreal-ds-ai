# Definition of Done Checklist for Colibri Design System Components (Medium Detail)

## 📋 **Pre-Development**

- [ ] Figma design received and reviewed with UX/UI team
  - [ ] Ensure Figma covers all scenarios in Notion document
  - [ ] Ensure Figma provides designs for all scenarios of a component (if Slots, that we can see each slot in each state; eg: if component includes checkbox, see checkbox all its states)
- [ ] Component classified (Atom/Molecule/Organism) and API defined
- [ ] WBS (EOA tickets) are created for the component and ready for grooming
  - [ ] Good component specific Acceptance Criteria is added
  - [ ] When possible, also provide Dev Notes to help the developer that will be taking the ticket
  - [ ] File structure planned following naming conventions (`bds-[name]`)

## 🔧 **Development**

- [ ] Component extends form the most appropriate Parent Component
  - [ ] Options found in config/components
    - [ ] ThemedComponent || FormComponent || SelectableFormComponent || etc
- [ ] All properties defined with TypeScript types and decorators
  - [ ] Do not follow Notion documentation to the letter on these, we are trying to make components that are both easier to use and easier to maintain
- [ ] Uses design tokens via getThemeVar() instead of hardcoded values
- [ ] Basic accessibility implemented (ARIA, keyboard support)
- [ ] Events use bare `@Event()` — no explicit `bubbles`/`composed`/`cancelable`
- [ ] No ESLint or TypeScript errors

## 🧪 **Testing**

- [ ] 90% test coverage achieved with Open WebComponents (unit tests)
- [ ] Component tested in React and Vue examples
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
- [ ] Bundle size impact documented and acceptable
- [ ] Performance verified (component renders in <100ms on average hardware)
- [ ] CHANGELOG.md updated with appropriate semantic version
- [ ] Breaking changes communicated to team (if applicable)
- [ ] Backwards compatibility verified with consuming applications
- [ ] Published following existing process
