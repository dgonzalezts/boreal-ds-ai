---
name: bds-date-picker-task15g-react-vue-parity
description: EOA-17138 Task 15g — calendarType="default" confirmed identical across web components/React/Vue; found (not fixed) a same-shape playground-retrofit gap in the React/Vue testapps
metadata:
  type: project
---

**Result: all 4 of Task 15c's scenarios pass identically in React and Vue.** No regression in the core behavior under test (immediate-commit-and-close, no chrome, `with-time` no-op + warning, `required` validation). Confirmed via `playwright-cli` against real `dev:pack:react`/`dev:pack:vue` builds, not assumption:

- `bds-popover`'s `footer`/`header`/`closable` all `false` under `calendarType="default"` in both wrappers.
- Day click commits `value` immediately and closes the popover (`aria-hidden` flips `"true"`) in the same handler — no separate Apply click, in both wrappers.
- Click-outside dismissal leaves the committed value unchanged, in both wrappers.
- `with-time` produces the exact console warning (`` `with-time` has no effect when `calendar-type` is 'default' ``), no time-selector UI renders, day click yields correct naive `YYYY-MM-DD` value with the real `<input>` showing the formatted date and no spurious "not a valid UTC ISO datetime" follow-up warning — in both wrappers.
- `required` + a real form-submit validation attempt flips the slotted field `[invalid]` with the correct `errorMessage`, blocks submission (no app-level "form submitted" log) — in both wrappers.

**Separate finding, logged as Task 15h (not fixed inline, out of this task's scope):** `examples/react-testapp/src/App.tsx` and `examples/vue-testapp/src/App.vue` both hold pre-existing `bds-date-picker` scenarios (Task 7's `withTime` scenarios, Task 15's min/max scenarios) that never pinned `calendar-type` explicitly. Since `calendarType` now defaults to `'default'` (Task 15b's second follow-up correction), every one of those pickers is silently rendering in `default` mode — no footer, no Apply button, no time selector — contradicting their own documented test steps. This is the exact same regression class Task 15c already found and fixed for `packages/boreal-web-components/src/index.html`'s 11 scenarios, but that fix never covered the two testapp playgrounds. Confirmed live via `dp.calendarType` reading `'default'` for every pre-existing picker in both apps. See Task 15h in the plan file for the retrofit scope.

**Method note:** `console warning`/`console` output via `playwright-cli` needs care with backtick-heavy grep patterns in a Bash `-c` string — a first grep for the `with-time has no effect` warning came back empty in Vue and looked like a real parity gap, but was a shell-escaping false alarm (the raw `console 2>&1 | grep -n "bds-date-picker"` dump showed it fired fine). Always re-check with a broader, simpler grep before concluding an absence is real.
