---
name: race-condition-single-trial-misdiagnosis
description: A single-trial read of post-interaction UI state can land on either side of a race condition, producing a misleading pass or fail. Also covers two follow-up findings — (2) playwright-cli's default type() speed (~0ms/keystroke) can trigger races invisible to real human typing, causing automation vs. manual-test disagreements that are not a mistake on either side; (3) how to correctly verify a raw-DOM-event race through a framework wrapper (real paste event, not the synthetic setter proxy) without over-claiming it as a framework-specific bug. Worked example from bds-color-picker's opacity field.
metadata:
  type: project
---

## Part 1 — repeat trials before reporting a timing-sensitive result

During EOA-17362 (`bds-color-picker`) QA, TC-EDGE-004 (invalid opacity values) was first reported
as a deterministic display bug: typing an out-of-range opacity (`150`) and blurring left the field
permanently showing the raw, unclamped `"150"` text instead of reformatting to `"100%"`. That
first-pass conclusion was based on a single trial per input value, read once after a fixed
`waitForTimeout(150)`.

Repeating the *exact same* scripted interaction back-to-back (11 trials, sampling at
0ms/550ms/1550ms post-blur) showed the field actually reformats correctly in roughly half of runs
— a non-deterministic race, not a fixed defect.

**Takeaway:** whenever a test step reads UI/DOM state shortly after a state-changing interaction
(blur, async validation, debounced reformat, popover open/close animation, etc.), do not trust a
single trial for the pass/fail verdict — repeat the identical interaction several times (5–10 is
usually enough to reveal a split) before writing up either a "Pass" or a "Fail" result.

## Part 2 — the "50/50 race" was actually input-speed-dependent, and this explains real automation-vs-manual disagreements

After reporting Part 1's ~50/50 finding, the user manually tested the same scenario in their own
browser and reported it "always restores back to 100" for them — a direct contradiction. Rather
than assuming either side was wrong, a targeted A/B re-test isolated the real variable: **how fast
the new value arrives at the field, not the value itself.**

- Typing `150` at human-realistic speed (`page.keyboard.type(val, { delay: 120 })`, ~120ms between
  keystrokes) reproduced the bug **0/14** times across two batches — matching the user's manual
  test exactly.
- Typing `150` at `playwright-cli`'s/Playwright's **default** speed (`page.keyboard.type(val)`,
  effectively ~0ms between keystrokes — far faster than any human) reproduced it intermittently,
  roughly 1/3–1/2 of trials, confirmed via an interleaved fast/slow A/B run in the same session to
  rule out environmental drift.
- A single fast `value` setter + one `input` event dispatch (the closest synthetic proxy for a
  real paste) reproduced it **6/6, deterministically**.
- A genuine OS-level `Cmd+V` clipboard paste (`navigator.clipboard.writeText` + `page.keyboard.press('Meta+v')`)
  reproduced it intermittently (2/4 in one trial) — real paste event timing sits between the two
  extremes above.

**Root cause implication:** the bug is a debounce/timer race in the field's reformat-on-blur logic
that a fast value-then-blur sequence can outrun; slow, human-paced keystrokes always give it enough
time to resolve correctly first.

**Takeaway for future QA passes — this generalizes beyond this one bug:**

1. **`page.keyboard.type()`'s default speed does not resemble human typing** — it is much closer to
   a paste or a very fast typist, and can trigger timing-sensitive bugs invisible to real users who
   type at normal speed. When a manual tester (the user, or a future retest) disagrees with an
   automated finding for a typing-triggered bug, **don't assume the automation is right and the
   manual test missed it, or vice versa** — check whether input *speed* is the actual variable, not
   just repeat count. Compare `{ delay: 0 }` (or unset) against `{ delay: ~100-150 }` explicitly.
2. When a bug is genuinely speed/method-dependent, the bug report's reproduction steps must say so
   explicitly and give the **most reliable** repro path (here: a DevTools console snippet doing a
   single fast `value` + `input` dispatch, which reproduced 6/6) rather than only the originally
   fastest-to-write path (character-by-character typing), since a reader trying to verify the report
   by hand-typing will otherwise conclude — correctly, for their input method — that it doesn't
   reproduce, and lose trust in the report.
3. Screenshot evidence for a flaky bug should capture *both* the good and bad outcomes from
   consecutive identical trials, not just one, so the non-determinism itself is part of the record
   — see `ai-work/qa/bug-reports/EOA-17362-bds-color-picker-bug-003.md` and its
   `bug-003-opacity-150-stuck-after-blur.png` / `bug-003-opacity-150-recovered-after-blur.png` pair.

## Part 3 — cross-framework verification of a raw-DOM-event race: reproduce it through the wrapper via a *real* browser event, never the synthetic-setter proxy

The user separately asked whether this bug is reachable through Vue's `v-model`. Two traps to avoid
when answering "does bug X reproduce through framework Y" for a bug whose trigger is a raw DOM event
(here: paste speed into a native `<input>`):

1. **Don't reuse the deterministic synthetic-setter repro** (`Object.getOwnPropertyDescriptor(...).set`
   + `dispatchEvent(new Event('input'))`) as "proof" it reproduces through a framework wrapper — that
   trick bypasses real browser paste/input event dispatch entirely, so it proves nothing about the
   wrapper. Use a genuine `navigator.clipboard.writeText()` + `Cmd+V`/`Ctrl+V` keypress instead, exactly
   as done for the plain-web-components confirmation.
2. **A bug reproducing identically inside a framework wrapper is not automatically "a framework bug."**
   For `bds-color-picker`'s opacity field specifically: it has no public prop, so `v-model` cannot reach
   it at all (see BUG-004's addendum) — the wrapper is provably uninvolved in the code path. More
   generally, a native DOM event (paste, focus, blur) delivered to a native form element nested inside a
   Stencil component is delivered identically regardless of what mounted the custom element (vanilla,
   Vue, React, Angular) — always check whether the framework's *own* reactivity system can even reach the
   affected state before concluding cross-framework testing was necessary to "prove" the bug is real
   there; it may only be necessary to give the user a live, clickable demo, not to test a genuinely
   different code path. State this distinction explicitly in the bug report rather than letting a
   successful cross-framework repro imply a broader root cause than what was actually found.

A live, kept-in-place Vue demo for this: `examples/vue-testapp/src/App.vue`, "EOA-17362 BUG-003 scratch
repro (Vue)" section — run `pnpm run dev:pack:vue` → `http://localhost:5173`. Screenshot evidence:
`ai-work/qa/bug-reports/assets/bug-003-vue-wrapper-paste-repro-stuck.png`.
