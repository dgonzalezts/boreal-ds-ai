# PR Title

build(release): EOA-18749 link version headings to Bitbucket compare pages

---

# PR Body

## Description

Follow-up to the first `@pxglobal` release (EOA-18749). The new `0.14.0` headings of the two maintained changelogs are plain text, while the historical ones link to a Bitbucket compare page. This PR links them and keeps them linked on every future release.

**Why the generator cannot do it:** with `linkCompare: true` the changelog generator builds `…/compare/<old>...<new>` with encoded tag names, and Bitbucket Server rejects it (`400 Bad Request – The encoded slash character is not allowed`). The format Bitbucket accepts is `…/compare/commits?sourceBranch=refs%2Ftags%2F<new>&targetBranch=refs%2Ftags%2F<old>`. The historical links only look right because a one-time script rewrote them earlier; nothing produced them for new releases.

## Implementation Details

- **Script** `scripts-boreal/lib/changelog-link.js` (+ CLI `bin/link-changelog-heading.js`): builds the Bitbucket compare URL from the `context` block of the package's `.release-it.json` (host, owner, repository), encodes both tag names, and links the first plain heading `## <version> (<date>)`. A heading that is already linked, or missing, is left untouched.
- **Never fails a release:** any problem (missing file, bad config, no heading) prints a warning and exits 0.
- **Hook** `after:@release-it/conventional-changelog:beforeRelease` in the configs of `boreal-web-components` and `boreal-style-guidelines`, the only two packages that write a changelog. It runs right after the changelog is written and before git stages the file, so the linked heading is part of the release commit. React and Vue are unchanged.
- **Existing headings:** both `0.14.0` headings are linked against the last `@telesign` tag, generated with the same script.
- **Docs:** new "Release helpers" section in `scripts-boreal/README.md` (goal, why, when it runs, manual use, behaviour), a pointer in step 3 of `RELEASING.md`, and the stale "pnpm 10.x" requirement in the `scripts-boreal` README updated to 11.x.

## Impact Analysis

- **Releases:** the commit types are `build` and `docs`, so this PR does not release any package by itself, although it touches package folders. The next release of web-components and style-guidelines will have a linked heading.
- **Consumers:** none. Nothing changes in the published packages.
- **Storybook:** the "What's new" page shows the linked headings after the next Storybook deploy.
- **Risk:** a wrong script path in the hook would fail the release before the publish (loudly, by design). A runtime problem inside the script cannot fail the release.

## Testing Conducted

**Automated:**

- [x] 9 new unit tests for the URL builder and the heading linker (plain heading, already linked, missing heading, tag encoding, cross-scope tags, URL parts from the context, versions with dots and prerelease suffixes, no dot wildcard, first match only); the `scripts-boreal` suite passes (5 files)
- [x] Pre-push hook: 357 suites, 4,199 tests

**Release rehearsal** (throwaway clone, local git remote, `--no-npm.publish`; nothing reached Bitbucket or npm):

- [x] Two real releases through the hook: both new headings linked with the verified pattern, the linked heading inside the release commit, tree clean
- [x] The hook key was corrected during the rehearsal: `after:bump` runs before the changelog is written, and the plugin namespace is its full package name (`@release-it/conventional-changelog`)
- [x] A run where the heading did not exist yet completed normally (warning only)

**Manual (signed-in browser):**

- [x] The compare links of both `0.14.0` headings open the Bitbucket compare page with the right source and destination tags and the commits between them, also across the `@telesign` → `@pxglobal` scopes

## Additional Remarks

- **Bitbucket Server specific, by design.** If the repository moves to another host, set `linkCompare: true` (the generator's links work natively on GitHub and GitLab) and remove the hook lines, the script, its tests and the README section. The historical links in the changelogs are plain text and would need a rewrite pass, as they did when they were first corrected.
- **Merging:** use Squash and merge with the title above. It has no `!` and no bare `@` handle, so it does not trigger a release.
- **After the merge:** redeploy Storybook to show the links on the "What's new" page. The first real proof of the hook is the next release; the person releasing should check that the new heading is linked.

## References

Refs EOA-18749

## Checklist

### General

- [x] Follows conventional commit format: `type(scope): TICKET description`
- [x] Ticket reference included
- [x] All tests pass
- [x] Self-reviewed for correctness

### Testing

- [x] Unit tests added for the new logic
- [x] Behaviour verified with real releases in a rehearsal environment
- [x] Failure behaviour verified (warning and exit 0)

### Documentation

- [x] `scripts-boreal/README.md` documents the script
- [x] `RELEASING.md` points to it
- [x] No inline comments; JSDoc on the exported functions

### Compatibility

- [x] No change to published packages
- [x] Commit types do not trigger a release
