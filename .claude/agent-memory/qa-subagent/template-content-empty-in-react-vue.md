# `<template>` authored via JSX/Vue-template children never populates `.content`

Confirmed live in both frameworks (`EOA-16000`, `bds-table` `slot="row-detail"`): `HTMLTemplateElement.content` (the hidden parser-only `DocumentFragment`) is populated by the browser **only** when its own HTML parser encounters the `<template>` tag in raw markup. React and Vue's virtual-DOM reconcilers create the element and append children via normal DOM operations (`appendChild`/`insertBefore`) — not parser semantics — so `.content` stays an empty `DocumentFragment` even though the framework visibly rendered children into the element's ordinary `childNodes`.

**Symptom:** any Boreal DS feature reading `someTemplateElement.content` (e.g. `bds-table` cloning `rowDetailTemplate.content`) renders its toggle/trigger correctly (presence-only checks pass) but the actual detail content is **silently empty** — no error, no console output, nothing to indicate why.

**Verified repro (do this first before assuming a bug in the component):**
```js
document.querySelector('template[slot="row-detail"]').content.childNodes.length
```
`0` despite visible JSX/Vue-template children = this bug, not a real defect elsewhere.

**The working fix, confirmed end-to-end in both frameworks:** populate `.content` imperatively via a ref/mounted-hook, setting `.innerHTML` — `.innerHTML` assignment DOES go through HTML-parser semantics and correctly populates `.content`, unlike appending JSX/Vue-template children.

- React: `useRef<HTMLTemplateElement>` + `useEffect(() => { ref.current.innerHTML = '...' }, [])`
- Vue: `ref<HTMLTemplateElement | null>(null)` + `onMounted(() => { ref.value.innerHTML = '...' })`

Raw web-component/vanilla-HTML usage (writing `<template>` directly in static markup) is entirely unaffected — this is specific to authoring through a framework's virtual-DOM compiler.

**Also confirmed:** a bare `<template>` with no `v-if`/`v-for`/`v-slot` in a Vue SFC does NOT get "unwrapped" by Vue's compiler (an initial worry that turned out to be unfounded) — Vue does render it as a genuine DOM `<template>` node, `ref` binds correctly, and `hasRowDetail`-style presence checks on `el.children` find it fine. Only the `.content` populate step is broken, not the element's existence.

`bds-table` now has a paired one-time dev-mode console warning (`applyRowDetail` detects `template.content.firstElementChild === null`) — if you don't see it despite empty content, the template may not exist at all yet (check presence separately) or the warning may have already fired once this session (it's a one-time guard, not per-attempt).

This is promoted at team level too: see `.agents/memory/template-element-content-empty-in-react-vue.md`. Any future Boreal DS feature reading `.content` will hit the exact same trap unless designed/documented around it up front.

## Second, distinct bug found on `EOA-16000` Task 3 (`bds-table-column` `slot="cell"`): the ref+`.innerHTML` workaround itself races with React specifically, on immediately-rendered (non-lazy) templates

`slot="row-detail"` (Task 2) and `slot="cell"` (Task 3) both clone `template.content` through the same `_cellContentCache`, but they differ in **when** `bds-table` first reads the template: `row-detail` is read lazily, only after a user expands a row — by which point React's `useEffect` (or Vue's `onMounted`) has long since run and populated `.content`. `slot="cell"` is read unconditionally on the **very first render**, racing directly against the framework's post-mount hook.

**Confirmed via `browser_evaluate` (2026-07-31, fresh page loads, reproduced deterministically every time, not a flake):**
- **Web components:** works — the browser's own HTML parser populates `.content` before any script runs, no race exists.
- **Vue (`onMounted` + `.innerHTML`):** works — `onMounted` apparently runs early enough (same tick, before Stencil's microtask-queued initial render) to win the race every time tested.
- **React (`useEffect` + `.innerHTML`):** **fails on first paint, every time.** `bds-table`'s `applyCellTemplate` finds `template.content.firstElementChild === null` on its first (and only) attempt, returns early without caching anything, and nothing ever retries — the cell renders permanently empty. No console warning is logged for this path (unlike the analogous empty-`row-detail`-template case, which has `warnEmptyRowDetailTemplateOnce`). Forcing an unrelated re-render (e.g. reassigning the `data` array reference) after mount does cause the cell to populate correctly, confirming this is a stale-render/no-retry issue, not a data-shape problem.
- **Root cause pinpointed:** swapping `useEffect` → `useLayoutEffect` (synchronous, pre-paint) in React reliably fixes it — `useLayoutEffect` runs before the microtask queue that Stencil's render pipeline drains, `useEffect` runs after.

**Practical implication:** any future Boreal DS feature that reads a `<template>`'s `.content` **unconditionally at initial render** (not lazily on user interaction) needs either (a) `bds-table` itself to become robust to late content population (e.g. a `MutationObserver` on `template.content` triggering a targeted re-render when children first appear), or (b) explicit React-specific documentation to use `useLayoutEffect`, not `useEffect`, for that specific template. Do not assume the `useEffect`-based workaround that fixed `row-detail` generalizes to every `<template>`-based feature — it depends on whether the read is lazy or immediate. This was reported back to `frontend-subagent` as a real bug requiring a root-cause fix, not waived or patched over in the QA scenario.

## RESOLVED (2026-07-31): `bds-table.tsx` now self-heals via `MutationObserver` + `forceUpdate` — option (a) above, implemented

`frontend-subagent` fixed this at the component level rather than requiring `useLayoutEffect` in every consumer. In `applyCellTemplate` (`bds-table.tsx`), when `template.content.firstElementChild === null` on read, it now calls `private watchForLateTemplateContent(col, template)`, which attaches a one-shot `MutationObserver` on `template.content` (deduped per column via a `_pendingTemplateContentObservers: Map<string, MutationObserver>` field — re-entrant calls for the same `colKey` are no-ops). When the observer fires (i.e. the consumer's framework effect populates `.content` late), it disconnects itself, removes itself from the map, and calls `forceUpdate(this)` to re-render with the now-populated template. `disconnectedCallback` also disconnects and clears any still-pending observers to avoid leaks.

**Re-verified end-to-end (React `useEffect`, unchanged — still NOT `useLayoutEffect`):** 5 fresh reloads of `examples/react-testapp` (4 normal `page.goto` + 1 cache-bypassing `location.reload(true)`), each checked via `browser_evaluate` reading `.tier-badge` presence/`data-row-id` on every row — **0 empty cells across all 5 reloads**, deterministic, no console errors (only an unrelated favicon 404). This is a real fix, not a lucky race win: `examples/react-testapp/src/App.tsx` still uses plain `useEffect` (not `useLayoutEffect`) for `cellTemplateRef`, confirming `bds-table` itself now tolerates the React `useEffect`-loses-the-race timing rather than depending on consumer-side hook choice.

Also reconfirmed unaffected: Vue (`onMounted`) cell-template rendering, the `formatter`-takes-precedence one-time warning (unchanged after a forced re-render), virtual-scroll recycling (scrolled through full range + back, 0 stale-content mismatches), and React's `row-detail` (Task 2) expand/collapse (unrelated code path, `applyRowDetail` was not modified to call `watchForLateTemplateContent` — still only lazy-read, still works).

This closes out `EOA-16000` Task 3 QA. The general lesson in the "Practical implication" paragraph above (any future `.content`-reading feature needs to consider this race) still stands — the fix here is specific to `bds-table`'s own `applyCellTemplate`/`applyRowDetail`, not a framework-level guarantee. A future component doing the same "read `.content` on first render" pattern must add its own equivalent late-content observer, it doesn't get this for free.
