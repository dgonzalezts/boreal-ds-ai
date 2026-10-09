# Bitbucket Squash Messages: Breaking Changes and @mentions

Source: tests with `release-it --dry-run` in a rehearsal clone, 2026-10-09.

---

## The squash message shape

Subject = the PR title, then `Merge in <project>/<repo> from <branch> to <target>`, then `Squashed commit of the following:` followed by every squashed commit **indented** (`commit <hash>`, `Author:`, `Date:`, then the message).

## A `BREAKING CHANGE:` footer inside that list is ignored

| Message | Result |
|---|---|
| `type(scope)!: …` in the title, with or without the Bitbucket body | breaking: minor bump below 1.0, BREAKING CHANGES entry |
| no `!`, footer only inside the indented list | **not breaking**: patch bump, no entry |
| plain unindented footer | breaking |
| `!` + footer right after the title | breaking, but Bitbucket's text is swallowed into the entry |
| `!` + footer as the **last** lines of the message | breaking, clean entry |

Rule: a breaking PR needs the `!` in the title; an optional footer goes at the very end of the merge message.

## A bare `@name` becomes a link

The generator turns `@name` in a commit subject into `<host>/name` (a page that does not exist). Code spans (backticks) and names containing `/` (`@pxglobal/boreal-react`) are left alone. Write handles such as `@pxglobal` in backticks in titles.
