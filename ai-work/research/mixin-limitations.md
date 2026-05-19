User: Confirm me the limitation of the attached mixin. Previously, we added the "name", "disabled" and "required" props to the mixin but we were having some problems with unit testing. Carefully look at the mixin comments and find web references to support this decision. Be thorough

GitHub Copilot: Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/packages/boreal-web-components/src/mixins)

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/.ai/reviews/2026-03-13-commit-b8a6eb2-feature-eoa-10056-bds-checkbox-review.md)

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/packages/boreal-web-components/src/mixins/form-associated.mixin.ts#1-1), lines 1 to 120

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/packages/boreal-web-components/src/mixins/form-associated.mixin.ts#120-120), lines 120 to 140

Now let me read the referenced memory files and look for additional context:

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/.claude/memory/stencil-face-attach-internals.md)

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/.claude/memory/stencil-face-element-proxy-limits.md)

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/.claude/memory/stencil-async-rendering-gotchas.md)

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/.ai/decisions)

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/.claude/memory/stencil-face-constraint-validation-pattern.md)

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/.ai/decisions/0001-attach-internals-must-be-on-component-class-not-in-mixin.md)

Now let me check the bds-checkbox component to see how it implements these props, and look for any test files that reveal the unit testing problem:

Searched for files matching `**/packages/boreal-web-components/src/components/forms/bds-checkbox/**`, 4 matches

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/.claude/memory/MEMORY.md)

Let me read the remaining memory files relevant to this topic:

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/.claude/memory/stencil-face-test-mocks.md)

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/.claude/memory/stencil-prop-patterns.md)

Now let me read the checkbox component itself and search for any evidence of the `@Prop` declarations being in or attempted in the mixin:

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox.tsx#1-1), lines 1 to 120

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/packages/boreal-web-components/src/components/forms/bds-checkbox/__test__/bds-checkbox.spec.tsx#1-1), lines 1 to 100

Now let me look at the full checkbox spec and check git history for evidence of the props-in-mixin revert:

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/packages/boreal-web-components/src/components/forms/bds-checkbox/__test__/bds-checkbox.spec.tsx#100-100), lines 100 to 190

Ran `resolve-library-id`
Completed with input: {
"libraryName": "stencil"
}

Ran `get-library-docs`
Completed with input: {
"context7CompatibleLibraryID": "/stenciljs/core",
"topic": "mixin props state decorators static analysis compiler"
}

Read [](file:///Users/dgonzalez/Library/Application%20Support/Code/User/workspaceStorage/2a409964a3a3abf8fce9ae564ecf1fb1/GitHub.copilot-chat/chat-session-resources/d5701837-a3e1-4681-89a5-4b9e3703a55a/toolu_vrtx_01VW2tNSXdeLiaM6GVkMbYye__vscode-1773770547513/content.txt#1-1), lines 1 to 100

Read [](file:///Users/dgonzalez/Library/Application%20Support/Code/User/workspaceStorage/2a409964a3a3abf8fce9ae564ecf1fb1/GitHub.copilot-chat/chat-session-resources/d5701837-a3e1-4681-89a5-4b9e3703a55a/toolu_vrtx_01VW2tNSXdeLiaM6GVkMbYye__vscode-1773770547513/content.txt#100-100), lines 100 to 250

Read [](file:///Users/dgonzalez/Library/Application%20Support/Code/User/workspaceStorage/2a409964a3a3abf8fce9ae564ecf1fb1/GitHub.copilot-chat/chat-session-resources/d5701837-a3e1-4681-89a5-4b9e3703a55a/toolu_vrtx_01VW2tNSXdeLiaM6GVkMbYye__vscode-1773770547513/content.txt#250-250), lines 250 to 450

Let me look at the Stencil testing config and understand how the test transform works for mixins:

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/packages/boreal-web-components/stencil.config.ts)

Read [](file:///Users/dgonzalez/projects/src/worktrees/boreal-ds/feature/EOA-10056-bds-checkbox/packages/boreal-web-components/testing.config.ts)

Ran `get-library-docs`
Completed with input: {
"context7CompatibleLibraryID": "/stenciljs/core",
"topic": "newSpecPage testing props mixin inheritance unit test transformer jest"
}

Read [](file:///Users/dgonzalez/Library/Application%20Support/Code/User/workspaceStorage/2a409964a3a3abf8fce9ae564ecf1fb1/GitHub.copilot-chat/chat-session-resources/d5701837-a3e1-4681-89a5-4b9e3703a55a/toolu_vrtx_01Kgep3ywPejPpfGaHCGzN39__vscode-1773770547519/content.txt#1-1), lines 1 to 200

Now I have a thorough picture. Let me run one more targeted search to fully verify the static-metadata shadowing mechanism in Stencil's transformer:

Ran `get-library-docs`
Completed with input: {
"context7CompatibleLibraryID": "/stenciljs/core",
"topic": "convertDecoratorsToStatic static properties members cmpMeta inheritance class extends"
}

Searched for regex `static get properties|cmpMeta|convertDecoratorsToStatic|members|$members$` (`**//Users/dgonzalez/Library/Application Support/Code/User/workspaceStorage/2a409964a3a3abf8fce9ae564ecf1fb1/GitHub.copilot-chat/chat-session-resources/d5701837-a3e1-4681-89a5-4b9e3703a55a/toolu_vrtx_01DdoxJsSSTqkizvicBjhGZ2__vscode-1773770547521/content.txt`), no results

Read [](file:///Users/dgonzalez/Library/Application%20Support/Code/User/workspaceStorage/2a409964a3a3abf8fce9ae564ecf1fb1/GitHub.copilot-chat/chat-session-resources/d5701837-a3e1-4681-89a5-4b9e3703a55a/toolu_vrtx_01DdoxJsSSTqkizvicBjhGZ2__vscode-1773770547521/content.txt#1-1), lines 1 to 200

I now have a complete, evidence-backed picture. Here is the thorough confirmation you requested.

---

## Confirmed Limitation of `formAssociatedMixin`

The mixin can be found at form-associated.mixin.ts. Its JSDoc correctly describes two distinct but related constraints.

---

### Constraint 1 — `@AttachInternals()` cannot be in the mixin (runtime failure)

#### What happens

If `@AttachInternals() internals!: ElementInternals` is placed inside the mixin factory's inner class, `this.internals` is `undefined` at runtime whenever any FACE lifecycle callback (e.g. `formAssociatedCallback`) calls `this.internals.setFormValue(...)`. The error thrown is:

```
TypeError: Cannot read properties of undefined (reading 'setFormValue')
```

#### Why

Stencil's decorator transformation compiles `@AttachInternals()` differently from `@Prop()` or `@State()`. It requires the decorator to be statically visible on a class that carries `@Component()`. Inside a factory function, the inner class is an anonymous class expression without `@Component()` — Stencil's compiler does not wire up `ElementInternals` for it. This is a compile-time analysis failure, not a runtime one.

#### References

- ADR-0001 — full trade-off analysis confirming the rejected Option A
- stencil-face-attach-internals.md — confirms `@AttachInternals()` must be on the class body; lists which decorators DO work inside mixins
- Stencil docs: every official FACE example places `@AttachInternals()` on the component class body — never inside a mixin ([`stenciljs.com → Form-Associated Elements`](https://stenciljs.com/docs/form-associated))
- WHATWG FACE spec: `attachInternals()` is a method on the element instance; the call must be wired up at component registration time, which requires the decorator to be seen by Stencil's component analyzer ([WHATWG FACE section](https://html.spec.whatwg.org/multipage/custom-elements.html#custom-elements-face-example))

---

### Constraint 2 — `@Prop()` / `@State()` / `@Watch()` from a mixin break `newSpecPage` unit tests (static metadata shadowing)

This is the specific problem encountered with `name`, `disabled`, and `required`.

#### What happens in spec tests

When a `@Prop()` is declared inside the mixin's inner class AND the consuming component also declares its own `@Prop()`s, the unit tests fail in three ways:

1. Setting the prop via an HTML attribute (e.g. `<bds-checkbox disabled>`) has no effect — the prop is not registered with the Stencil runtime
2. `@Watch()` callbacks for those props never fire
3. DOM assertions on prop-derived rendering (disabled class, aria attributes) fail

#### Root cause — static getter shadowing

Stencil's `convertDecoratorsToStatic` transformer converts every `@Prop()` into an entry in `static get properties()` on the class where the decorator appears. This is visible in the official compiler docs (`docs/compiler.md`):

```typescript
// Output of the transformer
export class MyComponent {
  static get properties() {
    return { "name": { "type": "string", ... } };
  }
}
```

When `@Prop() name`, `@Prop() disabled`, and `@Prop() required` are inside the mixin factory's inner class `FormAssociated`, the transformer generates `static get properties()` on `FormAssociated`. When `@Prop() checked`, `@Prop() indeterminate`, etc. are on `BdsCheckbox`, the transformer generates a separate `static get properties()` on `BdsCheckbox`.

JavaScript static getter inheritance follows the prototype chain — **but the child class's static getter silently shadows the parent's**:

```
BdsCheckbox.properties  → returns only {checked, indeterminate, ...}  ← shadows ↓
FormAssociated.properties → returns {name, disabled, required, ...}   ← never reached
```

Stencil's runtime proxy (`proxyComponent`, from `docs/runtime.md`) reads `cmpMeta.$members$`, which is populated from `Cstr.properties` (the single resolved static getter on the component class). With shadowing in place, `$members$` contains only `BdsCheckbox`'s own props. The mixin props are invisible to the proxy — they are not registered, not reflected, not watched.

`newSpecPage` works directly with the component class object in a mock-doc environment. It relies entirely on these compiled static getters. It has no mechanism to merge parent-class static metadata.

#### Why it "worked" in WDIO (E2E) tests

Stencil's **full compiler pipeline** runs during E2E builds. During compilation, it can traverse the full class hierarchy and merge static metadata from parent classes into the final component bundle. This is confirmed by Stencil's own WDIO mixin test suite (`test/wdio/ts-target/extends-mixin/mixin-a.tsx`), which only exists as an E2E test — there is no equivalent spec-test fixture in the Stencil repository for mixin props, which is itself a signal that Stencil does not guarantee `newSpecPage` compatibility for props inherited from mixins.

#### References

- Stencil compiler docs — `static get properties()` pattern: [github.com/stenciljs/core/blob/main/docs/compiler.md](https://github.com/stenciljs/core/blob/main/docs/compiler.md)
- Stencil runtime docs — `proxyComponent` reads `cmpMeta.$members$`: [github.com/stenciljs/core/blob/main/docs/runtime.md](https://github.com/stenciljs/core/blob/main/docs/runtime.md)
- Stencil WDIO mixin test (E2E only, no spec equivalent): [github.com/stenciljs/core/blob/main/test/wdio/ts-target/extends-mixin/](https://github.com/stenciljs/core/blob/main/test/wdio/ts-target/extends-mixin/)
- MDN Web Docs — JavaScript static method inheritance and shadowing: [developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/static](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/static)

---

### What the mixin does and does not own

| Declaration                           | Where                    | Why                                                                                       |
| ------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------- |
| `@AttachInternals()`                  | **Component class body** | Compiler static analysis requires it on the `@Component()` class                          |
| `@Prop() name / disabled / required`  | **Component class body** | Static getter shadowing makes mixin props invisible to `newSpecPage`                      |
| `@State() isDisabled`                 | **Component class body** | Same shadowing reason; also guards against double-writer race with `formDisabledCallback` |
| `@Watch('disabled') onDisabledChange` | **Component class body** | Watchers on unregistered props are never called                                           |
| `formDisabledCallback`                | **Mixin**                | A plain method with no decorator — safely inherited, no static metadata involved          |

`formDisabledCallback` is the only FACE lifecycle callback that is identical across all components with no value semantics, so it is the only safe candidate to live in the mixin. All decorator-bearing declarations must remain on the component class body.
