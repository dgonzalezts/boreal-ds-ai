---
name: feedback-jsx-fragment-shorthand
description: Stencil JSX shorthand fragment <>...</> throws ReferenceError at spec-test runtime in this codebase — must import and use Fragment explicitly
metadata:
  type: feedback
---

Never use the JSX shorthand fragment `<>...</>` in this codebase's `.tsx` components. It compiles fine but throws `ReferenceError: Fragment is not defined` the moment the branch actually renders in a Jest spec test (caught late — only on the code path that renders it, so existing tests that don't hit that branch stay green and mask the bug until a new test exercises it).

**Why:** this repo's Stencil/TSX toolchain does not have an automatic JSX-fragment-to-`Fragment`-import transform wired up. `bds-banner.tsx` and `bds-tag.tsx` are the two existing precedents — both explicitly `import { Fragment } from '@stencil/core'` and use `<Fragment>...</Fragment>` instead of the shorthand.

**How to apply:** whenever a `render()`/render-helper needs to return multiple sibling elements without a wrapper, add `Fragment` to the `@stencil/core` import list and write `<Fragment>...</Fragment>`, never `<>...</>`. Verify by actually running the component's spec suite (`pnpm --filter @telesign/boreal-web-components test -- <component>`) after adding a fragment — a clean `tsc`/build/lint pass does NOT catch this, only executing the render path does. Found and fixed in `bds-table.tsx`'s `renderToolbarLeft()` during the EOA-15507 Task 5 (skeleton loading) implementation.
