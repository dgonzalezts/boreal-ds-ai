# Boreal Component Library - Licensing Brief for Legal

**Prepared:** 2026-10-16
**Prepared by:** Boreal core team
**Decision needed:** license terms for an internal-only component library, and how to handle versions already published on public npm.

## 1. What Boreal is

Boreal is Proximus Global's component library (design system): web components built with Stencil, design tokens with several brand themes, and wrappers for React and Vue. It is in alpha (`0.x`). Source lives on the company's Bitbucket Server.

## 2. Intended use

The library is meant to be used **only across the company** (and, to be confirmed, its affiliates and contractors working for it). It is not intended for external use or redistribution.

## 3. Current state

| Package | Declared `license` | LICENSE file | Published |
| --- | --- | --- | --- |
| `@pxglobal/boreal-web-components` | MIT | Yes (MIT) | Public npm, `access: public` |
| `@pxglobal/boreal-style-guidelines` | ISC | No | Public npm, `access: public` |
| `@pxglobal/boreal-react` | ISC | No | Public npm, `access: public` |
| `@pxglobal/boreal-vue` | none | No | Public npm, `access: public` |

- The web-components README shows an MIT badge.
- Older packages under the `@telesign` scope are deprecated, with a message pointing to `@pxglobal`. Their license state was not checked.
- There is no root `LICENSE` file.
- A CodeArtifact registry is confirmed as the internal sharing registry. Whether public npm stays in use is to be confirmed.

## 4. The problem

1. The four packages declare different licenses (MIT, ISC, none).
2. The declared open-source licenses contradict the "internal only" intent.
3. The packages are downloadable by anyone on public npm today.
4. The copyright holder is not stated anywhere in the packages.

## 5. Options we see

| Option | `package.json` value | Notes |
| --- | --- | --- |
| A. No license | omitted | Exclusive copyright by default, but ambiguous, and it states no permitted users. |
| B. `UNLICENSED` | `"UNLICENSED"` | Explicitly grants no rights to others. Does not describe use by affiliates or contractors. |
| C. Custom proprietary license (our recommendation) | `"SEE LICENSE IN LICENSE"` | One `LICENSE` file, identical in all four packages and at the repo root. Needs text written by Legal. |
| D. Open source (MIT or Apache-2.0) | SPDX identifier | Contradicts the internal-only intent. Listed for completeness. |

Until Legal decides, we propose option B as a stopgap for new releases.

## 6. Questions for Legal

1. Which legal entity is the copyright holder, and what name should appear in the license?
2. Who is permitted to use the library: employees only, or also affiliates and contractors? Which entities?
3. Can you provide or approve the text for a proprietary license (option C)?
4. **Versions already published under MIT or ISC:**
   - Can those grants be withdrawn, or do they stay valid for the versions already downloaded?
   - Should the old versions be deprecated, unpublished (where npm policy allows), or left as they are?
5. Should the packages keep being published on public npm? Our preferred direction is to publish only to the internal registry.
6. Do the Proximus brand assets (theme tokens, logos, fonts, icons) need separate terms or a trademark notice?
7. Do third-party license notices need to be shipped with the packages (see section 7)?
8. Do external people ever contribute? If so, do we need a contributor agreement?
9. Is the old `@telesign` MIT state a concern, and who should be informed?

## 7. Third-party dependency licenses (runtime)

Scan run with `pnpm licenses list --prod` on 2026-10-16. It covers production dependencies only.

| Package | Licenses found |
| --- | --- |
| `@pxglobal/boreal-web-components` | MIT: `@braintree/sanitize-url`, `@colordx/core`, `@date-fns/tz`, `@floating-ui/core`, `@floating-ui/dom`, `@floating-ui/utils`, `@tanstack/virtual-core`, `@types/trusted-types`, `date-fns`. `(MPL-2.0 OR Apache-2.0)`: `dompurify` |
| `@pxglobal/boreal-style-guidelines` | No production dependencies found |
| `@pxglobal/boreal-react` | MIT (41), ISC (3), BSD-2-Clause (4), BSD-3-Clause (1). This list includes build tooling that pnpm resolves for the package, such as Stencil and rollup. |
| `@pxglobal/boreal-vue` | MIT (23), ISC (1), BSD-2-Clause (1), BSD-3-Clause (1) |

- No copyleft licenses (GPL or AGPL) were found in this scan.
- `dompurify` is dual-licensed. The choice of MPL-2.0 or Apache-2.0 should be confirmed with Legal.
- Most dependencies are permissive but require their copyright notices to be kept.
- The react and vue counts include transitive tooling and are not necessarily shipped inside the tarballs. A scan of what actually ships (`dist`) has not been done. It is a follow-up.
- Dev dependencies, fonts and icon assets were not scanned.

## 8. Proposed plan once Legal answers

1. Add the approved `LICENSE` file to the repo root and to each of the four packages.
2. Set `"license"` consistently in all four `package.json` files.
3. Update the package READMEs (remove the MIT badge, add the proprietary notice).
4. Release the change as a `chore` or `docs` commit. The license field is part of published metadata, so it takes effect only with a new release.
5. Agree what happens to the existing public versions (question 4).
6. Record the decision as an ADR.

## 9. Timeline

No deadline set. The next release will carry whatever `license` values are in the repo at that time, so we recommend a decision before it.
