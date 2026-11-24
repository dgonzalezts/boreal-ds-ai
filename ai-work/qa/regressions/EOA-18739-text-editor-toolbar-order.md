# EOA-18739 — bds-text-editor toolbar order / slot divider regression QA

- Date: 2026-11-20
- Branch: `feature/EOA-18739_text-editor-v1_DG`. Fix commits under test: `4654410d` (toolbar order) and `a9194ada` (slot divider).
- Executor: qa-subagent. Driver: Playwright 1.64.1 (repo copy) running Chromium (rev 1248), Firefox (rev 1555) and WebKit 27.2 (rev 2370). Firefox and WebKit were installed with `playwright install`.
- **Result: 153/153 PASS, 0 FAIL, 0 BLOCKED.** A negative control on a pre-fix build reproduced the reported bugs, which shows the harness can detect them (see below).

## Builds under test

| Surface | Build | Fix marker check |
| --- | --- | --- |
| Raw WC | Isolated `stencil build --dev` of the working tree at `a9194ada` (19:02). The `www` output went to a scratch dir and was served with `python3 -m http.server`. | `toolsWrapper` present in `bds-text-editor.entry.js` |
| React | `pnpm run dev:pack:react` (turbo build 19:13; vite deps 19:14) | `toolsWrapper` present in `node_modules/.vite/deps/@pxglobal_boreal-react.js` |
| Vue | `pnpm run dev:pack:vue` (vite deps 19:18) | `toolsWrapper` present in `node_modules/.vite/deps/@pxglobal_boreal-vue.js` |
| Negative control | Pre-fix `dist/boreal-web-components` restored from the Turbo cache artifact `6db751c2a772a7d3` (2026-11-19 build) | no `__tools` in the entry chunk |

**Caveat (Vue only):** during this run, another session made uncommitted edits to `bds-text-editor.tsx`/`.scss`. The edits add a new `--editing` focus-state class and do not touch the toolbar render. They landed at 19:16, after the React pack and the raw-WC build but before the Vue pack. The Vue bundle therefore contains those edits (`isInsideEditable` is present), and the React and raw-WC bundles do not. Toolbar-order behaviour is the same in all three builds.

## Method

- One page per surface, with seven editors (`ed-a`, `ed-b`, `ed-b5`, `ed-c`, `ed-d1..3`). Each editor gets `fields = [{token:'{{1}}',label:'Name'},{token:'DF-Email',label:'Email'}]` as a JS property/prop. A `window.__qa.set(id, {toolbar, slots, readOnly})` hook drives the runtime changes. React uses `useState` and Vue uses `reactive`. In both, slotted tools are rendered conditionally from a `slots` array as `<BdsButton slot="toolbar">`, so slot add/remove is done the framework way. Raw WC sets the props directly and uses DOM append/remove.
- Each step waits 400 ms. Editors are never re-mounted between steps.
- **Order measurement:** the harness collects every `bds-button-group`, `bds-divider` and `[data-qa-slot]` element in the editor that is not inside a `bds-button-group` and has a visible (non-zero) bounding rect. It sorts them by `getBoundingClientRect().x`. Inside each group it labels `bds-dropdown` as `fields` and a non-dropdown `bds-button` as `link`, also sorted by x. `.children` is never used. A check also fails if an item renders outside `bds-toolbar` or on more than one row.
- C1 uses real `ArrowRight` key presses after a programmatic focus on the Fields trigger. C2 reads the toolbar's `role` and the pixel gaps between adjacent items (right edge to next left edge).
- Scratch harness files: `qa.html`, `driver.cjs` and the JSON results were kept in the session temp dir and deleted afterwards. The testapp `App.tsx`/`App.vue` scratch scenarios were reverted.

## Matrix

WC = raw web components, R = React, V = Vue; Cr/FF/WK = Chromium/Firefox/WebKit. "—" = not in scope for that cell. The PRE column is the pre-fix negative control (WC, Chromium) and is for information only.

| Check | Expected | WC-Cr | WC-FF | WC-WK | R-Cr | R-FF | R-WK | V-Cr | V-FF | V-WK | PRE (pre-fix) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | `group(fields,link)` | PASS | PASS | PASS | PASS | PASS¹ | PASS¹ | PASS | PASS¹ | PASS¹ | pass |
| A2 | `group(fields) \| group(link)` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **fail** `\| group(link) group(fields)` |
| A3 | `group(fields,link)` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **fail** `group(link,fields)` |
| A4 | `group(fields) \| group(link)` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | **fail** `\| group(link) group(fields)` |
| A5 | `group(fields,link)` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | **fail** `group(link,fields)` |
| A6 | `group(link) \| group(fields)` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | **fail** `\| group(fields) group(link)` |
| A7 | `group(fields) \| group(link)` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | **fail** `\| group(link) group(fields)` |
| A8 | `group(link,fields)` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | pass |
| A9 | `group(link)` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | pass |
| A10 | no `bds-toolbar` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | pass |
| A11 | `group(link) \| group(fields)` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | pass |
| B1 | `group(fields,link) \| A` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **fail** `A group(fields,link) \|` |
| B2 | `group(link) \| group(fields) \| A` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **fail** `A group(link) \| group(fields) \|` |
| B3 | `group(link) \| group(fields)` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **fail** `group(link) \| group(fields) \|` (trailing divider) |
| B4 add C, D | `… \| C D` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | **fail** `C D group(link) \| group(fields) \|` |
| B4 remove C | `… \| D` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | **fail** `D group(link) \| group(fields) \|` |
| B4 readOnly true | no toolbar | PASS | PASS | PASS | PASS | — | — | PASS | — | — | pass |
| B4 readOnly false | `… \| D` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | pass |
| B4 remove D | `group(link) \| group(fields)` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | **fail** trailing `\|` |
| B5 add X | `X` only | PASS | PASS | PASS | PASS | — | — | PASS | — | — | pass |
| B5 remove X | no `bds-toolbar` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | **fail** empty toolbar rendered |
| C1 | Insert field → Insert link → slotted → Insert field | PASS | PASS | PASS | — | — | — | — | — | — | n/a |
| C2 | `role="toolbar"`, uniform gaps | PASS (12/12 px) | PASS (12/12) | PASS (12/12) | — | — | — | — | — | — | n/a |
| D1 | `link,\|,fields` → `group(link) \| group(fields)` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | pass |
| D2 | `fields,\|,link` → `group(fields) \| group(link)` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | pass |
| D3 | `\|,fields,link` → `group(fields,link)` | PASS | PASS | PASS | PASS | — | — | PASS | — | — | pass |

¹ A1 was run in the Firefox/WebKit wrapper subsets as the starting state for A2/A3. It passed but is not counted as an extra scoped check in the totals.

Totals: WC 27 × 3 = 81, React 24 + 6 + 6 = 36, Vue 24 + 6 + 6 = 36, for **153 PASS**.

### C1 / C2 evidence (all three browsers, identical)

- C1 focus sequence: `Insert field` (fields trigger) → `Insert link` → `S` (slotted) → `Insert field` → `Insert link`. Roving focus wraps correctly.
- C2: `bds-toolbar` has `role="toolbar"`. Gaps for `group(fields,link) | S` are `[12, 12]` px. Every multi-item state in A/B/D measured 12 px between every adjacent pair, e.g. B4 add C, D: `12/12/12/12/12`.
- Every passing state rendered on a single row, with no items outside `bds-toolbar`.

## Screenshots (B1)

`ai-work/qa/regressions/screenshots/`:

- `B1-wc-chromium.png`, `B1-wc-firefox.png`, `B1-wc-webkit.png`
- `B1-react-chromium.png`, `B1-react-firefox.png`, `B1-react-webkit.png`
- `B1-vue-chromium.png`, `B1-vue-firefox.png`, `B1-vue-webkit.png`
- `B1-wcPRE-chromium.png`: the pre-fix control, showing `A` rendered before the Fields/Link group with a stray trailing divider

## Console

- No errors, page errors or warnings mention `bds-text-editor`, `bds-toolbar` or `bds-button-group` on any surface or in any browser.
- `[BorealDS Button] No accessible name found…` appears 5 times on page load in every surface and browser. The pre-fix build logs it the same 5 times, so it predates this fix. Every `bds-button` rendered after settle has an accessible name (a DOM audit found zero unnamed buttons). This looks like the dev-mode name check firing before the icon-only toolbar buttons get their `aria-label`. It is unrelated to this ticket but worth a separate look.
- Firefox also logs about 95 `downloadable font: glyf: Glyph bbox was incorrect` warnings (for `boreal-icons`) and a "localhost classified as a bounce tracker" notice. Both are environmental noise.

## Teardown

- Stopped: both `dev:pack:*` pipelines (SIGINT to `publish.js`, whose cleanup restored `package.json`/`pnpm-lock.yaml`), the leftover vite servers on 5173, and my `http.server` instances on 8765/8766.
- Left running (not started by me): the orphaned Stencil dev-server worker on 3333 (PID 55798, parent `launchd`, started 10:27), Storybook on 6006, and a `python3 -m http.server 7121` from another session.
- Pre-existing `examples/vue-testapp/*.tgz` and `packages/boreal-vue/*.tgz` (dated Oct 29) were left untouched.
- `git status`: my testapp edits were reverted and the temporary Stencil config/tsconfig/`.qa-src` were removed. The other working-tree changes visible now (`bds-text-editor.tsx/.scss`, `events.spec.ts`, docs mdx/stories, `src/index.html`, plus a new commit `2963084e`) came from a concurrent session, not from this QA run.
