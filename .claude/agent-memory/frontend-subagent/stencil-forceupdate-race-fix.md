---
name: stencil-forceupdate-race-fix
description: How to use forceUpdate(this) from componentDidLoad/MutationObserver to fix a light-DOM-read race that the first synchronous render() missed
metadata:
  type: project
---

`forceUpdate` is exported from `@stencil/core` and called as `forceUpdate(this)` (the class instance, not `this.el`) from inside an instance method. It schedules an async re-render but is a no-op unless the host has already completed its first render and isn't already mid-update (`hostRef.$flags$ & (hasRendered|isQueuedForUpdate) === hasRendered`). That makes it safe to call unconditionally from `componentDidLoad` — it only ever fires the extra render when actually needed.

Pattern for fixing a first-paint race where a getter reads live light-DOM (`Array.from(this.el.children)`) and that read can be stale during the very first `render()` call (before Stencil's non-shadow slot-relocation polyfill has settled), even though the specific node in question (e.g. a `<template slot="x">` consumed via `cloneNode`, never actually relocated into a `<slot>`) has no real reason to be affected by relocation timing:

1. Cache what the render assumed, in a plain (non-`@State`) private field, set as the first line of `render()`: `this._xAtLastRender = this.getterX;`
2. Add a private method that re-reads the getter and compares: `if (this.getterX !== this._xAtLastRender) forceUpdate(this);`
3. Call it once in `componentDidLoad` (catches the first-paint race).
4. Also call it from any existing `MutationObserver` callback already watching `this.el` for `childList` changes (catches the node arriving/leaving after mount) — extend the existing observer, don't add a second one.

Verified via live Playwright reproduction on `bds-table`'s row-detail feature (EOA-16000-adjacent regression pass): reloading a page that assigns `.data` synchronously right after parsing missed the expand-toggle column on ~half of loads before the fix, never after. See [[stencil-slot-relocation-timing]] for the related (but distinct) `componentDidLoad`-vs-`componentWillLoad` light-DOM read-timing issue this complements.
