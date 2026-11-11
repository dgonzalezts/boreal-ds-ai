# playwright-cli `eval` is an expression wrapper — a full-call snippet needs `run-code`

`playwright-cli eval "<code>"` sends `page.evaluate('() => (<code>)')`, i.e. the argument is parsed as a **single expression**. Consequences when replaying documented console snippets (T61/T62/PD-02 style):

- **`SyntaxError: Unexpected token ';'`** for any multi-statement snippet (`b = document.getElementById(...); b.items = [...]`). The snippet is fine — the harness is not. Replay it via `playwright-cli -s=<s> run-code --filename=/tmp/x.js`, with the file body `async page => (await page.evaluate("<snippet verbatim as a JS string>"))`; Playwright's `evaluate(string)` goes through `Runtime.evaluate` and accepts statement lists, returning the last expression's value.
- **`ReferenceError: Cannot access '<name>' before initialization`** for bare-name fragments (`value = 'Item 1'`). The wrapper's own arrow-function scope has a TDZ binding named `value`, so a fragment that would be a harmless implicit-global assignment in DevTools throws here. Confirm the real-console behaviour with `window.eval("<fragment>")` (indirect eval, global scope, non-strict) before reporting it as a page/console error.
- Suppressing a huge return (e.g. a 1000-item array from `el.items = [...]`) is easiest by mapping the resolved value in the `run-code` wrapper — the snippet text itself stays unmodified.

## False "picking is broken" alarms

Two self-inflicted failure modes hit in the same session while verifying `bds-search-bar` items mode:

1. Clicking a row **the current filter had excluded** — with `value` committed, the reopened list is filtered by the field text (`Item 3` ⇒ only `Item 3`, `Item 30…399` mounted), so `[value='item-5']` matches nothing. `playwright-cli click` errors on a missing target; piping through `grep Console` hides that error line. Never grep playwright-cli output in a way that drops `### Error`.
2. Raw `mousemove`/`mousedown`/`mouseup` coordinates while more than one popover is open on the accumulating playground page — the points can belong to another scenario's panel.

Decisive positive control: reload the page, use a locator click on a row you just verified exists (`#t-status bds-list-menu-item[value='item-99']`), then assert `value`, field text and `popover[aria-hidden]` all moved. Three clean picks (fresh t-status, `#pd02`, fresh t-status after typing `99`) confirmed picking works; both "failures" were the artifacts above.
