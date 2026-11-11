# EOA-19635 — Production audit triage (Task 1)

**Run:** 2026-10-28, `pnpm audit --prod` on branch `chore/EOA-19635_dependency-security-and-minor-updates_DG` (base `release/current` at `441d0c91`). Node 22.23.3, pnpm 11.28.2.

## Summary

| | Low | Moderate | High | Critical | Total |
| --- | --- | --- | --- | --- | --- |
| Baseline (ticket snapshot 2026-10-16) | 3 | 7 | 17 | 0 | 27 |
| Today | 4 | 7 | 17 | 1 | 29 |

Advisories listed below: 29 (1 critical, 17 high, 7 moderate, 4 low).

## Configuration check (Open assumption A1)

- `pnpm config get minimumReleaseAge` returns `undefined`: the repository does not set it.
- The pnpm 11.28.5 docs (Context7, `settings/dependency-resolution.md`) give the default as **1440 minutes (1 day) since v11**, applied to all dependencies including transitive ones. The repository therefore runs with the default, as ADR 0019 states.
- Consequence for fixes: a patched version published less than a day ago is not installable yet. Such findings are recorded as "fix not yet installable" and re-checked after a day.

## Findings

Sorted by severity, then package. `Decision` stays `pending` until the table is reviewed; nothing has been fixed or changed yet. Paths are shortest dependency path from a workspace package; `Roots` lists every workspace package that reaches the finding.

| # | Severity | Package | Installed | Vulnerable | Patched | Advisory | Roots (paths) | Shortest path | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | critical | `dompurify` | 3.4.8 | `>=3.4.4 <=3.4.16` | `>=3.4.17` | [GHSA-cg2g-xh64-v4q7](https://github.com/advisories/GHSA-cg2g-xh64-v4q7) | `packages__boreal-web-components` (1) | `packages__boreal-web-components>dompurify` | fixed: range bumped to `^3.4.17`, locked 3.4.17 |
| 2 | high | `@vue/server-renderer` | 3.5.28, 3.5.30 | `<3.5.42` | `>=3.5.42` | [GHSA-g2v6-rqmx-r4w6](https://github.com/advisories/GHSA-g2v6-rqmx-r4w6) | `examples__vue-testapp`, `packages__boreal-vue` (2) | `examples__vue-testapp>vue>@vue/server-renderer` | fixed: `vue` re-resolved to 3.5.44 within existing ranges (no manifest change) |
| 3 | high | `brace-expansion` | 2.0.2 | `>=2.0.0 <2.1.2` | `>=2.1.2` | [GHSA-3jxr-9vmj-r5cp](https://github.com/advisories/GHSA-3jxr-9vmj-r5cp) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>minimatch>brace-expansion` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 4 | high | `brace-expansion` | 2.0.2 | `>=2.0.0 <2.1.3` | `>=2.1.3` | [GHSA-mh99-v99m-4gvg](https://github.com/advisories/GHSA-mh99-v99m-4gvg) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>minimatch>brace-expansion` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 5 | high | `brace-expansion` | 2.0.2 | `>=2.0.0 <2.1.4` | `>=2.1.4` | [GHSA-rgw5-rvv9-x895](https://github.com/advisories/GHSA-rgw5-rvv9-x895) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>minimatch>brace-expansion` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 6 | high | `brace-expansion` | 2.0.2 | `>=2.0.0 <2.1.6` | `>=2.1.6` | [GHSA-qhr7-859c-m2p7](https://github.com/advisories/GHSA-qhr7-859c-m2p7) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>minimatch>brace-expansion` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 7 | high | `brace-expansion` | 2.0.2 | `>=2.0.0 <2.1.5` | `>=2.1.5` | [GHSA-6j4f-fj2g-mc7p](https://github.com/advisories/GHSA-6j4f-fj2g-mc7p) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>minimatch>brace-expansion` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 8 | high | `dompurify` | 3.4.8 | `<=3.4.16` | `>=3.4.17` | [GHSA-mrv2-3pqr-j5jr](https://github.com/advisories/GHSA-mrv2-3pqr-j5jr) | `packages__boreal-web-components` (1) | `packages__boreal-web-components>dompurify` | fixed: range bumped to `^3.4.17`, locked 3.4.17 |
| 9 | high | `minimatch` | 9.0.5 | `>=9.0.0 <9.0.6` | `>=9.0.6` | [GHSA-3ppc-4f35-3m26](https://github.com/advisories/GHSA-3ppc-4f35-3m26) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>minimatch` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 10 | high | `minimatch` | 9.0.5 | `>=9.0.0 <9.0.7` | `>=9.0.7` | [GHSA-7r86-cg39-jmmj](https://github.com/advisories/GHSA-7r86-cg39-jmmj) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>minimatch` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 11 | high | `minimatch` | 9.0.5 | `>=9.0.0 <9.0.7` | `>=9.0.7` | [GHSA-23c5-xmqv-rm74](https://github.com/advisories/GHSA-23c5-xmqv-rm74) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>minimatch` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 12 | high | `nanoid` | 3.3.11 | `<3.3.16` | `>=3.3.16` | [GHSA-28wg-ghj8-5hjv](https://github.com/advisories/GHSA-28wg-ghj8-5hjv) | `examples__vue-testapp`, `packages__boreal-vue` (2) | `examples__vue-testapp>vue>@vue/compiler-sfc>postcss>nanoid` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 13 | high | `nanoid` | 3.3.11 | `<3.3.18` | `>=3.3.18` | [GHSA-2v37-7h3g-55p8](https://github.com/advisories/GHSA-2v37-7h3g-55p8) | `examples__vue-testapp`, `packages__boreal-vue` (2) | `examples__vue-testapp>vue>@vue/compiler-sfc>postcss>nanoid` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 14 | high | `nanoid` | 3.3.11 | `<3.3.12` | `>=3.3.12` | [GHSA-xwg4-73v4-xw9w](https://github.com/advisories/GHSA-xwg4-73v4-xw9w) | `examples__vue-testapp`, `packages__boreal-vue` (2) | `examples__vue-testapp>vue>@vue/compiler-sfc>postcss>nanoid` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 15 | high | `picomatch` | 2.3.1 | `<2.3.2` | `>=2.3.2` | [GHSA-c2c7-rcm5-vvqj](https://github.com/advisories/GHSA-c2c7-rcm5-vvqj) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>fast-glob>micromatch>picomatch` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 16 | high | `postcss` | 8.5.6, 8.5.8 | `<=8.5.11` | `>=8.5.12` | [GHSA-6g55-p6wh-862q](https://github.com/advisories/GHSA-6g55-p6wh-862q) | `examples__vue-testapp`, `packages__boreal-vue` (2) | `examples__vue-testapp>vue>@vue/compiler-sfc>postcss` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 17 | high | `postcss` | 8.5.6, 8.5.8 | `<=8.5.17` | `>=8.5.18` | [GHSA-r28c-9q8g-f849](https://github.com/advisories/GHSA-r28c-9q8g-f849) | `examples__vue-testapp`, `packages__boreal-vue` (2) | `examples__vue-testapp>vue>@vue/compiler-sfc>postcss` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 18 | high | `source-map-js` | 1.2.1 | `>=1.0.0 <1.2.2` | `>=1.2.2` | [GHSA-68fv-2mgg-jv7q](https://github.com/advisories/GHSA-68fv-2mgg-jv7q) | `examples__vue-testapp`, `packages__boreal-vue` (14) | `examples__vue-testapp>vue>@vue/compiler-sfc>source-map-js` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 19 | moderate | `brace-expansion` | 2.0.2 | `>=2.0.0 <2.0.3` | `>=2.0.3` | [GHSA-f886-m6hf-6m8v](https://github.com/advisories/GHSA-f886-m6hf-6m8v) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>minimatch>brace-expansion` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 20 | moderate | `brace-expansion` | 2.0.2 | `>=2.0.0 <2.1.7` | `>=2.1.7` | [GHSA-q2hr-2g5m-vwhr](https://github.com/advisories/GHSA-q2hr-2g5m-vwhr) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>minimatch>brace-expansion` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 21 | moderate | `dompurify` | 3.4.8 | `<=3.4.10` | `>=3.4.11` | [GHSA-cmwh-pvxp-8882](https://github.com/advisories/GHSA-cmwh-pvxp-8882) | `packages__boreal-web-components` (1) | `packages__boreal-web-components>dompurify` | fixed: range bumped to `^3.4.17`, locked 3.4.17 |
| 22 | moderate | `dompurify` | 3.4.8 | `<=3.4.12` | `>=3.4.13` | [GHSA-55q2-fjhq-7xh7](https://github.com/advisories/GHSA-55q2-fjhq-7xh7) | `packages__boreal-web-components` (1) | `packages__boreal-web-components>dompurify` | fixed: range bumped to `^3.4.17`, locked 3.4.17 |
| 23 | moderate | `picomatch` | 2.3.1 | `<2.3.2` | `>=2.3.2` | [GHSA-3v7f-55p6-f55p](https://github.com/advisories/GHSA-3v7f-55p6-f55p) | `packages__boreal-react` (1) | `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>fast-glob>micromatch>picomatch` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 24 | moderate | `postcss` | 8.5.6, 8.5.8 | `<8.5.10` | `>=8.5.10` | [GHSA-qx2v-qp2m-jg93](https://github.com/advisories/GHSA-qx2v-qp2m-jg93) | `examples__vue-testapp`, `packages__boreal-vue` (2) | `examples__vue-testapp>vue>@vue/compiler-sfc>postcss` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 25 | moderate | `postcss` | 8.5.6, 8.5.8 | `<=8.5.22` | `>=8.5.23` | [GHSA-fxqj-rqcc-2cmp](https://github.com/advisories/GHSA-fxqj-rqcc-2cmp) | `examples__vue-testapp`, `packages__boreal-vue` (2) | `examples__vue-testapp>vue>@vue/compiler-sfc>postcss` | fixed: re-resolved in the lockfile within the existing range (no override) |
| 26 | low | `dompurify` | 3.4.8 | `<3.4.9` | `>=3.4.9` | [GHSA-vxr8-fq34-vvx9](https://github.com/advisories/GHSA-vxr8-fq34-vvx9) | `packages__boreal-web-components` (1) | `packages__boreal-web-components>dompurify` | fixed: range bumped to `^3.4.17`, locked 3.4.17 |
| 27 | low | `dompurify` | 3.4.8 | `<=3.4.11` | `>=3.4.12` | [GHSA-c2j3-45gr-mqc4](https://github.com/advisories/GHSA-c2j3-45gr-mqc4) | `packages__boreal-web-components` (1) | `packages__boreal-web-components>dompurify` | fixed: range bumped to `^3.4.17`, locked 3.4.17 |
| 28 | low | `dompurify` | 3.4.8 | `<=3.4.15` | `>=3.4.16` | [GHSA-6688-9rhm-gjv2](https://github.com/advisories/GHSA-6688-9rhm-gjv2) | `packages__boreal-web-components` (1) | `packages__boreal-web-components>dompurify` | fixed: range bumped to `^3.4.17`, locked 3.4.17 |
| 29 | low | `dompurify` | 3.4.8 | `<=3.4.16` | `>=3.4.17` | [GHSA-c6gr-qvv4-5v3f](https://github.com/advisories/GHSA-c6gr-qvv4-5v3f) | `packages__boreal-web-components` (1) | `packages__boreal-web-components>dompurify` | fixed: range bumped to `^3.4.17`, locked 3.4.17 |

## Titles

1. `dompurify` (critical): DOMPurify SAFE_FOR_TEMPLATES bypass: split template expressions survive in attached shadow root content on DOM output modes
2. `@vue/server-renderer` (high): @vue/server-renderer: XSS via missing CR in attribute-name blacklist
3. `brace-expansion` (high): brace-expansion: DoS via exponential-time expansion of consecutive non-expanding {} groups
4. `brace-expansion` (high): brace-expansion: DoS via unbounded expansion length causing an out-of-memory process crash
5. `brace-expansion` (high): brace-expansion: DoS via unbounded intermediate arrays, bypassing the CVE-2026-14257 mitigation
6. `brace-expansion` (high): brace-expansion: DoS via uncontrolled recursion on nested brace groups causing stack exhaustion
7. `brace-expansion` (high): brace-expansion: DoS via uncontrolled recursion in parseCommaParts causing stack exhaustion
8. `dompurify` (high): DOMPurify IN_PLACE: hook that removes a parent or sibling leaves the detached subtree's event handlers armed (incomplete fix for GHSA-p98j-92pf-mc4p)
9. `minimatch` (high): minimatch has a ReDoS via repeated wildcards with non-matching literal in pattern
10. `minimatch` (high): minimatch has ReDoS: matchOne() combinatorial backtracking via multiple non-adjacent GLOBSTAR segments
11. `minimatch` (high): minimatch ReDoS: nested *() extglobs generate catastrophically backtracking regular expressions
12. `nanoid` (high): nanoid: non-secure generators can loop indefinitely with negative size
13. `nanoid` (high): nanoid: custom generators can loop indefinitely when size is zero
14. `nanoid` (high): nanoid: Integer Overflow or Wraparound
15. `picomatch` (high): Picomatch has a ReDoS vulnerability via extglob quantifiers
16. `postcss` (high): PostCSS: Arbitrary file read and information disclosure via attacker-controlled sourceMappingURL in CSS comments
17. `postcss` (high): PostCSS: Path Traversal in Previous Source Map Auto-Loading (sourceMappingURL) leads to Arbitrary .map File Disclosure
18. `source-map-js` (high): source-map-js allows event-loop denial of service through indexed source-map section offsets
19. `brace-expansion` (moderate): brace-expansion: Zero-step sequence causes process hang and memory exhaustion
20. `brace-expansion` (moderate): brace-expansion: Quadratic-time expansion of the `{a},b}` rewrite causes CPU denial of service
21. `dompurify` (moderate): DOMPurify: Permanent `ALLOWED_ATTR` pollution via `setConfig()` bypassing the hook clone-guard (incomplete fix of the 3.4.7 hook-pollution patch)
22. `dompurify` (moderate): DOMPurify: IN_PLACE hook removal leaves a detached subtree executable, causing XSS
23. `picomatch` (moderate): Picomatch: Method Injection in POSIX Character Classes causes incorrect Glob Matching
24. `postcss` (moderate): PostCSS has XSS via Unescaped </style> in its CSS Stringify Output
25. `postcss` (moderate): PostCSS: incomplete fix of GHSA-6g55-p6wh-862q — attacker-controlled sourceMappingURL reads arbitrary .map files when `from` is unset
26. `dompurify` (low): DOMPurify: Trusted Types policy survives `clearConfig()` and can poison later `RETURN_TRUSTED_TYPE` output
27. `dompurify` (low): DOMPurify: `CUSTOM_ELEMENT_HANDLING` bypasses `afterSanitizeElements` for allowed custom elements.
28. `dompurify` (low): DOMPurify: IN_PLACE returns a force-removed rawtext root whose text carries attacker markup — pure HTML reparse executes
29. `dompurify` (low): DOMPurify: SMIL attributeName=href guard is skipped when PARSER_MEDIA_TYPE is application/xhtml+xml

## Resolution (2026-10-29)

| | Low | Moderate | High | Critical | Total |
| --- | --- | --- | --- | --- | --- |
| Before | 4 | 7 | 17 | 1 | 29 |
| After | 0 | 0 | 0 | 0 | 0 |

Final `pnpm audit --prod` output: `No known vulnerabilities found`.

What changed (two files, no overrides, no major bumps, no manifest range changed except `dompurify`):

- `packages/boreal-web-components/package.json`: `dompurify` `^3.4.8` → `^3.4.17`. This single bump clears all 8 `dompurify` advisories, including the critical.
- `pnpm-lock.yaml`: `pnpm update -r --lockfile-only` for `brace-expansion`, `minimatch`, `picomatch`, `nanoid`, `postcss`, `source-map-js`, `@vue/server-renderer` and `vue`, then `pnpm install --frozen-lockfile`. Every new version stays inside the range its parent already declares.

Resolved package versions that moved (peer suffixes ignored): `dompurify` 3.4.8 → 3.4.17; `vue` and all `@vue/*` 3.5.28 / 3.5.30 → 3.5.44; `postcss` 8.5.6 / 8.5.8 → 8.5.32; `nanoid` 3.3.11 → 3.3.20; `minimatch` 3.1.2 → 3.1.5 (already in the lockfile), 9.0.5 → 9.0.9, 10.2.0 → 10.2.6; `brace-expansion` 1.1.12 → 1.1.21, 2.0.2 → 2.1.7, plus 5.0.12 added next to the existing 5.0.2; `picomatch` 2.3.2 added for the production path; `source-map-js` → 1.2.2; `@babel/parser`, `@babel/types` and two `@babel` helpers → 7.29.x as dependencies of the new `@vue/compiler-sfc`.

`picomatch` 2.3.1 is still in the lockfile on dev-only paths; the dev audit is outside this ticket's scope unless it blocks a gate.

Every fix version was checked against the registry and was older than the 1-day `minimumReleaseAge` delay (youngest: `postcss` 8.5.32 at about 67 hours).

Reading the lockfile diff: it is about 1,400 changed lines, but only the package-version moves above are real. The rest is pnpm 11 rewriting peer-dependency suffixes (for example `(supports-color@8.1.1)`) on about 490 entries during the fresh resolution; the committed lockfile did not have them. An install with unchanged manifests changes only 18 lines (key ordering), so the churn comes from the resolution the manifest change triggers and cannot be split into its own commit.

Lockfile formatting: pnpm writes single quotes; the committed file uses double quotes, so the lockfile was formatted with the `boreal-web-components` Prettier (`pnpm --filter @pxglobal/boreal-web-components exec prettier --write ../../pnpm-lock.yaml`) to keep the diff reviewable.

## Follow-up tasks logged during triage

1. **Observation (for plan Task 4, Runtimes):** the committed `pnpm-lock.yaml` has an environment section pinning `packageManagerDependencies.pnpm` to 12.4.2, while the root `package.json` `packageManager` is `pnpm@11.28.2`. It predates this work and my changes leave it untouched. Find out why before planning the pnpm 12 upgrade.
2. **Observation (for plan Task 3):** the lockfile now carries peer suffixes that the previous one lacked, so the next dependency PR should not show this churn again.
