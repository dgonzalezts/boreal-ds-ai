# PR Title

docs(release): EOA-18749 remove process-only entries from the changelogs

---

# PR Body

## Description

Last editorial step of the changelog cleanup (EOA-18749, EOA-18868, plan item T13, "option 2"). Tier 1 (broken links) and tier 2 (trim to own entries, wrapper pointers) were merged earlier; this PR removes the entries that carry no information for a reader of the public "What's new" page.

**19 entries removed, nothing added, nothing reworded:**

| Group | Entries | Examples |
|---|---|---|
| Pull-request review chatter | 11 | "Fixed PR comments", "Solved all PRs comments", "resolve comments" (web-components, alpha.5 to alpha.10) |
| Experiments and reverts | 4 | "test commitlint" and `Revert "rebase release current"`, each in web-components and style-guidelines (alpha.0) |
| Playground-only changes | 4 | "add playground examples for manual qa", "remove playground code from index.html" and two similar `index.html` playground edits |

Three section headings that became empty were removed with them (`### Reverts` twice, `### Performance Improvements` once).

## Implementation Details

- `packages/boreal-web-components/CHANGELOG.md`: 594 → 577 entries.
- `packages/boreal-style-guidelines/CHANGELOG.md`: 26 → 24 entries.
- Done with a script that required every target to match exactly one line in its version section, so no similar entry could be removed by accident. The diff has 0 added lines.
- Deliberately kept: entries that mix real changes with review wording (for example "Solved pr comments, added validations and deleted unused scss classes"), lint and JSDoc fixes, and the code-comment documentation entries.

## Impact

- Documentation only. Nothing changes in the published packages (npm tarballs do not contain the changelogs).
- The Storybook "What's new" page shows the shorter lists after the next deploy.
- Git history keeps every removed entry, and the commit hashes stay valid in Bitbucket.
- Commit type `docs`: this PR does not release any package, although it touches package folders.

## Testing

- [x] Diff reviewed: only deletions (19 entries and 3 empty headings), 0 added lines
- [x] Version headings unchanged (14 in web-components, 5 in style-guidelines) and both "Published as `@telesign/…`; continues as `@pxglobal/…`" notices intact
- [x] Files still end with a newline
- [x] Pre-push hook: 357 suites, 4,199 tests

## Additional Remarks

- Merge with Squash and merge and keep the title above (no `!`, no bare `@` handle).
- Reviewers: the list of removed entries is in the diff; say if any should stay.
- After merging, redeploy Storybook to refresh the "What's new" page.

## References

Refs EOA-18749

## Checklist

- [x] Follows conventional commit format: `type(scope): TICKET description`
- [x] Ticket reference included
- [x] Documentation only; no code changes
- [x] History preserved in git
