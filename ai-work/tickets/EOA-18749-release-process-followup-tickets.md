# Follow-up tickets from EOA-18749 (drafts, not yet in Jira)

These are local drafts kept alongside the release process work. Create a Jira ticket from one only when someone picks it up, then record its ID in the EOA-18749 plan row named in each heading (T23, T24, T26, T27, T17, T34); item 7 comes from EOA-19635 Task 11. Suggested project: EOA, type: Task. Items 2 and 3 are planned (not executed) in plan EOA-19635, Task 4 ("Runtimes").

## 1. Make `validate:pack` restore files safely (was T23)

**Summary:** Pack validation scripts discard uncommitted edits and leave files dirty when the terminal closes

**Description:** `pnpm validate:pack:*` (`scripts-boreal/bin/publish.js`) rewrites the wrapper `package.json`, the test app `package.json` and `pnpm-lock.yaml` to use local tarballs, and on exit runs `git checkout HEAD --` on them.
- Any uncommitted edit to those files is silently discarded.
- Cleanup runs on exit, error, SIGINT and SIGTERM, but not on SIGHUP (closing the terminal window) or `kill -9`. After the 0.14.0 release the three files were found modified with `file:` tarball references.
- Done 2026-10-30 (EOA-19635 Task 12, `6495b48e`): SIGINT and SIGTERM now exit with 130 and 143 instead of 0, so an interrupted `prerelease` hook no longer reports success; the `kill -9` recovery step was added to the publishing guideline. The remaining criteria below are optional.

**Acceptance criteria:**
- The script restores only what it changed (backup and restore), or refuses to run when those files have uncommitted changes.
- A SIGHUP handler runs the same cleanup.
- README troubleshooting describes the dirty-file case and how to recover.
- Verified by closing the terminal mid-run and by running with a dirty file.

## 2. Upgrade pnpm 11 to 12 (was T24)

**Summary:** Upgrade pnpm from 11 to 12

**Description:** Pin via `corepack use pnpm@12.x` and commit the one-time lockfile rewrite separately. Confirm the Jenkins agents' Node and Corepack support with DevOps. Grep CI scripts for `--resolution-only` and `--frozen-lockfile false` (none today). Re-run the pack scenarios and the Windows checklist. Update README and `cicd-dependency-installation.md`. Link to EOA-19635, which lists it as out of scope.

**Acceptance criteria:** build, test, `validate:all` and a release `--dry-run` pass on pnpm 12 on macOS and Windows; docs updated.

Included in plan EOA-20193 as T20 (2026-11-11). It also replaces the `peerDependencyRules` entry added for ESLint 10 with the `"eslint-plugin-react>eslint:peer"` override, which pnpm 11.28.2 and 11.28.11 reject and pnpm 12.19.0 accepts.

## 3. Evaluate moving Node 22 to Node 24 LTS (was T26)

**Summary:** Move the repository from Node 22 to Node 24 LTS

**Description:** Node 22.23.3 is pinned; Node 22 is in maintenance (end of life believed around April 2027, to verify at nodejs.org/en/about/previous-releases). `release-it` 21 supports `^24.15.0`; pnpm 11.28.2 and commitlint 21 run on 24. Check Stencil, Storybook, Chromatic, puppeteer, Playwright and the example apps on 24, and the Jenkins agents' Node version. Then update `.node-version`, `.nvmrc`, `engines.node` and the README. Link to EOA-19635.

**Acceptance criteria:** build, test, validate and release dry run pass on 24 (macOS and Windows); agents confirmed; decision recorded before April 2027.

## 4. Browser build output (UMD/IIFE) for the Library CDN (was T27, after Q4)

**Summary:** Add a UMD/IIFE browser build to boreal-web-components for the Library CDN

**Description:** Required for enterprise clients with npm registry restrictions. Add the output target, build and archive it in the CI build job (ITOPS-63110), publish it through the CD deployment (ITOPS-63138). Prerequisite for the Library CDN content. Depends on the S3 and CloudFront work (ITOPS-63094), which is not in Q4. Label: backlog, later than Q4.

**Acceptance criteria:** the build produces a single browser bundle that works from a `<script>` tag; archived by CI; the CDN path convention (version-pinned and `/latest/`) agreed with DevOps.

## 5. Graduate the packages from 0.x alpha to 1.0.0 (was T17, after alpha feedback)

**Summary:** Graduate boreal-web-components, boreal-style-guidelines and the React and Vue wrappers from 0.x to 1.0.0

**Description:** Not scheduled. Start once the real-world feedback from the alpha is addressed; the packages stay on `0.x` with `preMajor` until then. The procedure is documented in `ai-docs/guidelines/release-process.md` and `RELEASING.md`.
- Optionally release `1.0.0-rc.N` first.
- Release `1.0.0` deliberately with `--increment=1.0.0`.
- Remove `preMajor` from the four `.release-it.json` files.
- Decide whether web-components and the wrappers share one fixed version, which would make the single product changelog fully consistent.
- Decide whether to add per-component maturity labels (experimental, preview, stable).
- Record the outcome in ADR 0013 and `CONTRIBUTING.md`.

**Acceptance criteria:**
- The graduation decision, including fixed versus independent versioning and maturity labels, is recorded in ADR 0013 and `CONTRIBUTING.md`.
- `1.0.0` is released with `--increment=1.0.0` after a dry run (and `1.0.0-rc.N` first if chosen).
- `preMajor` is removed from all four `.release-it.json` files and a following dry run shows normal major, minor and patch bumps.
- The release docs (`release-process.md`, `RELEASING.md`) no longer describe the `0.x` policy as current.
- Label: backlog, later than the alpha phase.

## 6. Review how `bds-flag` resolves flag assets, and keep its manifest in sync (was T34)

**Summary:** Review approaches for resolving `bds-flag` assets in the React and Vue wrappers, and guard the generated flag manifest against drift

**Description:**

*Background — why the current workaround exists.*
- Before `32292f5f` (EOA-19436), `bds-flag` built the URL as `window.location.origin + getAssetPath('./constants/flags/4x3/<iso2>.svg')`. Stencil's `getAssetPath` resolves against the asset base path of the loaded bundle, and the SVGs only exist in `dist/boreal-web-components/constants/` (copied by `assetsDirs`). In vanilla JS, loading the library from a script tag, that folder is served next to the script, so it worked.
- In the React and Vue wrappers the library is bundled by the consumer's tool (Vite, webpack). The app does not serve `node_modules/@pxglobal/boreal-web-components/dist/...`, so the relative path resolves against the host page and returns 404, and prefixing `window.location.origin` makes it worse when the base path is already absolute. Making it work needs consumer-side configuration (`setAssetPath` plus copying the assets), which the wrappers do not do.
- The workaround replaces runtime path resolution with `helpers/generatedFlags.ts`, a map of ISO2 code to `() => import('../constants/flags/4x3/<code>.svg')`. Stencil inlines each SVG as a base64 data URI in its own chunk (271 chunks, about 4.0 MB of chunks from 2.7 MB of SVGs in the current build), so no path is resolved at runtime. An absolute `FLAG_BASE_URL` (CDN) still bypasses it, and `customFlags[].flag_4x3` overrides per flag.
- The manifest was regenerated by a `prebuild` script. That rewrote the committed file on every build (formatting differs from the prettier-formatted committed file), dirtied the working tree and blocked the wrapper release; the script was removed in `89d1919b` (T33). Nothing keeps the manifest in sync with `constants/flags/4x3/*.svg` now: a new SVG without regeneration renders a blank flag, and a deleted SVG leaves a dangling import that fails the build.

*Part A — guard the manifest (small, independent of Part B).*
- Make the generator output byte-identical to the committed format (run prettier on the output or emit the same key style), and resolve its paths from the script location, not the cwd.
- Add `generate:flags` (manual) and a drift check, either `check:flags` (regenerate in memory, fail on difference) in lint or CI, or a spec asserting `Object.keys(FLAGS)` equals the SVG filenames. No build or release hook.

*Part B — review other approaches to the wrapper path problem and decide.* Compare against the current data-URI chunks, with a short write-up in `ai-work/research/`:
1. **Current:** lazy data-URI chunks via the manifest. Check: bundle and tarball size (the SVGs are also still copied to `dist/…/constants/` by `assetsDirs`, so they ship twice), 271 chunks in consumer builds, the manifest maintenance cost, and whether consumers with a strict Content-Security-Policy need `img-src data:` (to verify).
2. **Stencil's documented asset model:** `getAssetPath` with `setAssetPath` and consumer-side copying of the assets (for example `vite-plugin-static-copy`, webpack copy plugin). Check what each wrapper could do automatically and what must be documented.
3. **Absolute base URL on the Library CDN** (S3 and CloudFront, `/icons/` static assets in the CI/CD plan, ITOPS-63094, item 4 above): make the base URL configurable (global setter, prop or environment) instead of the hardcoded `FLAG_BASE_URL` constant. Check offline and air-gapped enterprise clients, and the dependency on infrastructure that is not in Q4.
4. **Module-relative URLs** (`new URL('./x.svg', import.meta.url)`): works in bundlers that understand it; check whether Stencil's `dist`, `dist-custom-elements` and lazy-loader outputs preserve it and how Vite pre-bundling treats it.
5. **CSS-based flags** (sprite or one stylesheet with the flags as masks or backgrounds, as in the `flag-icons` library): check delivery (global CSS import) and tree-shaking.
6. **Reduce the cost of the current approach:** SVGO optimisation, URL-encoded instead of base64 data URIs, dropping the redundant `assetsDirs` copy, splitting flags into a separate package.

Evaluation criteria: works in vanilla JS, React and Vue with Vite and webpack without consumer configuration; SSR safety; CSP; consumer bundle and tarball size; offline use; maintenance burden. Prove each candidate in the `validate:pack` test apps (React and Vue) and a plain HTML page, not only in Storybook (see the memory note on stale wrapper bundles: verify through `dev:pack:*` or `validate:pack:*`).

*Part C — implement the decision.* If Part B replaces the manifest, remove `flagsManifest.ts`, `generatedFlags.ts` and the Part A guard, and update the bds-flag docs and the `customFlags` examples. If the manifest stays, Part A is the final state.

**Acceptance criteria:**
- Part A: running the generator on a clean tree produces no diff; adding or removing an SVG without regenerating fails the check; `pnpm build` leaves the working tree clean.
- Part B: a research note compares at least the six options against the criteria above, with measured sizes and a verified result for each tested wrapper, and a recommendation agreed with the team.
- Part C: flags render in vanilla JS, React and Vue (checked with `validate:pack:react` and `validate:pack:vue` test apps) without consumer-side asset configuration, or the required configuration is documented per wrapper; unit tests and the docs updated; no regression in the `customFlags` override.
- Existing release flow unchanged: `release:wc-stack --dry-run` leaves a clean tree.

## 7. Automate dependency checks in Jenkins and evaluate Renovate (from EOA-19635 Task 11)

**Summary:** Add a scheduled dependency report to Jenkins (policy Phase 2) and decide whether to run Renovate on Bitbucket Server (policy Phase 3)

**Description:** The dependency maintenance policy runs a monthly manual ticket (Phase 1). Phase 2 is a scheduled job inside the single multi-stage Jenkins job that reports `pnpm outdated -r` and `pnpm audit --prod`. Phase 3 is a self-hosted Renovate run in Jenkins, which depends on DevOps. The research is in `ai-work/research/2026-10-27-EOA-19635-renovate-bitbucket-evaluation.md`: Renovate on Bitbucket Server cannot assign, label or open issues, has no Dependency Dashboard, and ignores `automergeStrategy`.
- Phase 2 does not need the DevOps answers below, only Jenkins access.
- Ask DevOps: can a dedicated bot account be created and with which write scope; who owns and rotates the HTTP access token; which Jenkins agent, Node and Docker versions and network access apply and whether a monthly schedule is acceptable; is a Mend licence already available.

**Acceptance criteria:**
- A scheduled Jenkins job publishes the outdated and audit results monthly.
- The four DevOps answers are recorded in the evaluation document.
- A recommendation is recorded: proceed, defer or reject.
- Effort: small for the report; the Renovate decision depends on DevOps.
