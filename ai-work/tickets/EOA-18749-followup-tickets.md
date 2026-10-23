# Follow-up tickets from EOA-18749 (drafts, not yet in Jira)

Atlassian access from the agent is blocked by company policy, so these are drafts to paste into Jira. Record each new ID in the EOA-18749 plan (rows T23, T24, T26, T27) after creation. Suggested project: EOA, type: Task.

## 1. Make `validate:pack` restore files safely (was T23)

**Summary:** Pack validation scripts discard uncommitted edits and leave files dirty when the terminal closes

**Description:** `pnpm validate:pack:*` (`scripts-boreal/bin/publish.js`) rewrites the wrapper `package.json`, the test app `package.json` and `pnpm-lock.yaml` to use local tarballs, and on exit runs `git checkout HEAD --` on them.
- Any uncommitted edit to those files is silently discarded.
- Cleanup runs on exit, error, SIGINT and SIGTERM, but not on SIGHUP (closing the terminal window) or `kill -9`. After the 0.14.0 release the three files were found modified with `file:` tarball references.

**Acceptance criteria:**
- The script restores only what it changed (backup and restore), or refuses to run when those files have uncommitted changes.
- A SIGHUP handler runs the same cleanup.
- README troubleshooting describes the dirty-file case and how to recover.
- Verified by closing the terminal mid-run and by running with a dirty file.

## 2. Upgrade pnpm 11 to 12 (was T24)

**Summary:** Upgrade pnpm from 11 to 12

**Description:** Pin via `corepack use pnpm@12.x` and commit the one-time lockfile rewrite separately. Confirm the Jenkins agents' Node and Corepack support with DevOps. Grep CI scripts for `--resolution-only` and `--frozen-lockfile false` (none today). Re-run the pack scenarios and the Windows checklist. Update README and `cicd-dependency-installation.md`. Link to EOA-19635, which lists it as out of scope.

**Acceptance criteria:** build, test, `validate:all` and a release `--dry-run` pass on pnpm 12 on macOS and Windows; docs updated.

## 3. Evaluate moving Node 22 to Node 24 LTS (was T26)

**Summary:** Move the repository from Node 22 to Node 24 LTS

**Description:** Node 22.23.3 is pinned; Node 22 is in maintenance (end of life believed around April 2027, to verify at nodejs.org/en/about/previous-releases). `release-it` 21 supports `^24.15.0`; pnpm 11.28.2 and commitlint 21 run on 24. Check Stencil, Storybook, Chromatic, puppeteer, Playwright and the example apps on 24, and the Jenkins agents' Node version. Then update `.node-version`, `.nvmrc`, `engines.node` and the README. Link to EOA-19635.

**Acceptance criteria:** build, test, validate and release dry run pass on 24 (macOS and Windows); agents confirmed; decision recorded before April 2027.

## 4. Browser build output (UMD/IIFE) for the Library CDN (was T27, after Q4)

**Summary:** Add a UMD/IIFE browser build to boreal-web-components for the Library CDN

**Description:** Required for enterprise clients with npm registry restrictions. Add the output target, build and archive it in the CI build job (ITOPS-63110), publish it through the CD deployment (ITOPS-63138). Prerequisite for the Library CDN content. Depends on the S3 and CloudFront work (ITOPS-63094), which is not in Q4. Label: backlog, later than Q4.

**Acceptance criteria:** the build produces a single browser bundle that works from a `<script>` tag; archived by CI; the CDN path convention (version-pinned and `/latest/`) agreed with DevOps.
