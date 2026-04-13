# Getter Accessor and Boolean Expression Conventions in Components

## Getter naming — no `get` prefix

A getter property named `getPlacement` is doubly redundant: the `get` keyword is already present and callers read it as `this.getPlacement`. Name getters after the value they return.

**Wrong:** `get getPlacement()`, `get getFloatingContent()`
**Correct:** `get placement()`, `get floatingContent()`

## `|| false` is always redundant

`!x || false` always evaluates to `!x`. The `|| false` tail adds no logical effect and should be deleted.

**Wrong:**
```ts
return !this.floatingOptions.hideArrow || false;
```
**Correct:**
```ts
return !this.floatingOptions.hideArrow;
```

Both patterns were found in overlay component getters during the overlay review pass.
