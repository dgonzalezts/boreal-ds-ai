# Bitbucket Server Compare Links in Changelogs

Source: first `@pxglobal` release (2026-10-09), checked in a signed-in browser.

---

- The generator's compare link (`linkCompare: true`) is `<repo>/compare/<old>...<new>` with `encodeURIComponent` tag names. Bitbucket Server answers **400 Bad Request – "The encoded slash character is not allowed"**, even between two tags of the same scope.
- The accepted form is `<repo>/compare/commits?sourceBranch=refs%2Ftags%2F<new>&targetBranch=refs%2Ftags%2F<old>` (tag names encoded). It also works between tags of different npm scopes (`@pxglobal/…@0.14.0` against `@telesign/…@0.1.0-alpha.12`).
- Therefore `linkCompare` is `false` and `scripts-boreal/bin/link-changelog-heading.js`, run by the hook `after:@release-it/conventional-changelog:beforeRelease`, links the newest heading (see `release-it-hook-names-and-timing.md`).
- Commit links work through the `context` block: `<host>/projects/DEV/repos/boreal-ds/commits/<hash>`.
- The script is specific to Bitbucket Server: on a move to another host set `linkCompare: true` and remove the hook, script, tests and README section.
