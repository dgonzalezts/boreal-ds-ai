# `setAttribute` Requires Kebab-Case for ARIA Attributes

`setAttribute` always takes the HTML attribute name in kebab-case. Passing a camelCase property name writes a non-standard, unrecognised attribute to the DOM.

**Wrong — writes a non-standard attribute, breaks accessibility:**
```ts
trigger.setAttribute('ariaDescribedBy', 'tooltip-content');
```

**Correct:**
```ts
trigger.setAttribute('aria-describedby', 'tooltip-content');
```

The confusion arises because the DOM *property* accessor uses camelCase (`element.ariaDescribedBy`), but `setAttribute` operates on the HTML *attribute* name, which is always kebab-case for ARIA attributes. These are two different access paths.

This bug was found in `bds-tooltip.tsx` `subscribe()`. Screen readers do not recognise the camelCase variant, making the bug an accessibility regression with no visible runtime error.
