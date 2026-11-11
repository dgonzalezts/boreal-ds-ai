# Never run a bare `git stash pop` in this repo

The repo carries ~41 long-lived stashes from past branches. A bare `git stash pop` after a
`git stash push <specific paths>` has already been popped silently applies the **oldest-most-recent
unrelated stash** (`stash@{0}` = "tree shaking review & examples") into the working tree. It happened
during EOA-19598 T61 while trying to undo an accidental `git checkout` of one file; the tree came
back with `examples/react-testapp/src/App.tsx` and `examples/vue-testapp/src/App.vue` rewritten by
someone else's stash content. Recovered with `git checkout -- <those paths>`; nothing was lost
because `git stash pop` only drops the entry on a clean apply, so `git stash list` still showed it.

Rules:

- Always pair stash operations by explicit path: `git stash push <paths>` … `git stash pop stash@{0}`
  only after confirming `stash@{0}` is *your* entry (`git stash list` before and after).
- `2>/dev/null` on `git stash pop` hides exactly the "your local changes would be overwritten"
  failure that tells you you're about to pop the wrong entry.
- Prefer a plain file copy to `/tmp` for "temporarily revert my work to measure the before state",
  and `git checkout -- <path>` only for files you have already backed up.
- This repo is frequently worked by several sessions at once: `git status` showed a clean tree at
  task start and unrelated `examples/*` edits minutes later. Never `git checkout -- .`, `git stash`
  without paths, or `git reset --hard` here.
