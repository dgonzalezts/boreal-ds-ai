# PR Examples — Boreal DS

Concrete examples of well-formed PR titles and descriptions for this repository.

---

## Feature PR — new infrastructure

**Title:**
```
feat(web-components): EOA-10099 add form foundation architecture
```

**Body:**
```
Establishes the shared JS/TS form foundation that all form-associated components
(bds-text-field, bds-select, bds-checkbox, bds-radio, etc.) will build on.

Without a shared mixin, each component would repeat ~12 lines of identical
FACE boilerplate — reflected props, formDisabledCallback, and lifecycle stubs —
across 8+ components with no single point of correction. The mixin eliminates
this while keeping @AttachInternals() on each component class directly, which
Stencil's static analysis requires.

Shared SCSS partial and additional behavioral mixins (textInputMixin,
selectableMixin) are deferred to Phase 2 pending boreal-styleguidelines
token integration. See .ai/plans/EOA-10099-form-foundation.md for the full
three-phase roadmap.

Refs EOA-10099
```

---

## Bug Fix PR — runtime error

**Title:**
```
fix(web-components): EOA-10099 restrict @AttachInternals to component class
```

**Body:**
```
Moves @AttachInternals() out of formAssociatedMixin and onto each component
class directly, fixing a runtime TypeError where this.internals was undefined
in formAssociatedCallback.

Stencil's compiler performs static analysis on the component class body and
does not pick up @AttachInternals() when it is declared inside a mixin
factory function. @Prop(), @State(), @Watch(), and @Method() are unaffected
and continue to work inside mixin factories as documented.

Refs EOA-10099
```

---

## Docs PR — JSDoc / plan updates

**Title:**
```
docs(web-components): EOA-10099 update JSDocs in mixin and internals
```

**Body:**
```
Updates JSDoc on formAssociatedMixin and form internals utilities to reflect
the @AttachInternals() placement constraint discovered during implementation.

The @example blocks now show the correct pattern (decorator on the component
class, not inside the factory) and the "Provides:" list no longer claims the
mixin manages internals. No behaviour change.

Refs EOA-10099
```

---

## Refactor PR — structural change, no behaviour change

**Title:**
```
refactor(web-components): EOA-10099 reorganise src folder structure
```

**Body:**
```
Moves utilities and types into their final directory layout before new
infrastructure files are added, to avoid retroactive renames mid-feature.
No logic changes.

Refs EOA-10099
```

---

## Chore PR — tooling / config

**Title:**
```
chore: EOA-10099 exclude local tooling directories from git
```

**Body:**
```
Adds .ai/, .claude/, and .github/ to .gitignore. These directories contain
local AI plan files, Claude Code session memory, and GitHub-specific local
config that should not be tracked in the repository.

Refs EOA-10099
```

---

## Multi-scope PR

When a PR touches more than one package, list the primary scope in the title and
call out the secondary changes in the body:

**Title:**
```
feat(web-components): EOA-10099 add bds-text-field component
```

**Body:**
```
Implements the Phase 1 bds-text-field component using formAssociatedMixin
and ElementInternals for native form participation.

Includes:
- Full FACE lifecycle (formAssociatedCallback, formResetCallback,
  formStateRestoreCallback, formDisabledCallback via mixin)
- Built-in valueMissing validator + customValidators prop for consumer-defined rules
- @Method() wrappers for checkValidity() and reportValidity() (required
  because Stencil's element proxy blocks native FACE prototype members)
- Focus delegation on <Host> so the browser can focus the element on
  invalid form submission

Also updates index.html dev harness with verification steps for all eight
Phase 1 FACE contract checks.

Refs EOA-10099
```

---

## Title format quick reference

```
feat(web-components): EOA-XXXXX <what was added>
fix(web-components): EOA-XXXXX <what was broken and fixed>
docs(web-components): EOA-XXXXX <what docs were updated>
refactor(web-components): EOA-XXXXX <what changed structurally>
test(web-components): EOA-XXXXX <what tests were added or fixed>
chore: EOA-XXXXX <tooling/config change>
feat(boreal-docs): EOA-XXXXX <Storybook or docs-app change>
```
