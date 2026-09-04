# BUG-003: `bds-color-picker` — opacity field display gets stuck showing an unclamped value when a new value arrives quickly (paste, fast typing), but not on normal hand-typed input

**Severity:** Medium
**Priority:** P1
**Type:** UI / Functional (race condition)
**Status:** Open
**Component:** `bds-color-picker`
**Discovered during:** TC-EDGE-004
**Affects:** Opacity percentage field, both trigger and popover instances. Rare edge case — only triggered by a fast/programmatic value arrival (paste, or input speeds well beyond normal typing), not by ordinary hand-typed input.

---

## Environment

- **Component:** `bds-color-picker` (`packages/boreal-web-components/src/components/forms/bds-color-picker/bds-color-picker/bds-color-picker.tsx`, opacity field is a `bds-number-field`)
- **Playground fixture (web components):** "Input Edge Cases" section, `label="Edge Case Input"` (index 12 in `document.querySelectorAll('bds-color-picker')`)
- **Playground fixture (Vue):** `examples/vue-testapp/src/App.vue`, "EOA-17362 BUG-003 scratch repro (Vue)" section — a `bds-color-picker` mounted via `@telesign/boreal-vue`'s `BdsColorPicker` with `v-model`, plus a "Read current DOM state" button that reads both the trigger and popover opacity fields off the live component instance
- **Browser:** Chrome (latest stable), via `playwright-cli`

---

## Description

TC-EDGE-004 requires that opacity stays within the supported 0–100% range and that invalid drafts recover safely. The internal applied opacity (the CSS custom property `--swatch-opacity` driving the preview swatch) **is** always correctly clamped for out-of-range input — but the **visible text left in the opacity field** after blur does not always match what was actually applied.

This was originally reported as a simple, deterministic display bug, then re-classified as a ~50/50 non-deterministic race, then further narrowed: **the actual trigger is how fast the value arrives, not the value itself.** This matters a great deal for anyone trying to reproduce it manually:

- **Typing `150` at normal human speed (one keystroke every ~100ms+) never reproduces it** — 8/8 and a separate 6/6 trial both showed the field correctly settling to `100%` every time. This matches the user's own manual testing exactly, and is why it looked like a non-issue at first.
- **Typing/inserting `150` fast — via CDP's default near-zero-delay synthetic keystrokes, or a single programmatic value+`input`-event dispatch (the closest proxy for a paste) — reproduces it.** A controlled, interleaved A/B (fast vs. slow typing, alternating runs to rule out session drift) showed 2/6 stuck-at-`150` for fast typing vs. 0/6 for slow typing. The single-fast-event proxy (closest to a real paste) reproduced it **6/6, 100% deterministically**.
- **A genuine OS-level clipboard paste (`Cmd+V` after `navigator.clipboard.writeText('150')`) reproduces it intermittently** (2/4 in one trial) — real browser paste event timing sits somewhere between the two extremes above, but it is a completely normal, realistic user action (pasting a copied percentage value) that can trigger the bug.

So: **this is a real, reproducible race condition, but it is specifically sensitive to how quickly the new value lands in the field** — not to "invalid opacity input" in general. A user who types the digits by hand essentially never sees it; a user who pastes a value, or whose input method fires the character events in very quick succession, can hit it.

### Most reliable way to reproduce it (paste-equivalent, deterministic in testing)

1. Baseline: opacity field shows `100%`.
2. Focus the opacity field, select all.
3. Instead of typing character-by-character, set the value in one fast operation and fire a single `input` event — exactly what a real paste does — then blur. In DevTools Console, on `http://localhost:3333` (with the "Edge Case Input" picker's opacity field focused and selected):
   ```javascript
   (() => {
     const el = document.querySelectorAll('bds-color-picker')[12]
       .querySelector('.bds-color-picker__container .bds-number-field__container');
     const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
     setter.call(el, '150');
     el.dispatchEvent(new Event('input', { bubbles: true }));
     el.blur();
   })();
   ```
4. Wait at least 1–2 seconds, then check `el.value` — in every trial (6/6) this left the field permanently stuck on the raw `150` (no `%`), even though `--swatch-opacity` was already correctly clamped to `1` (100%) the whole time.

### A more "hands-on" repro that also works, intermittently

1. Baseline: opacity field shows `100%`.
2. Copy `150` to the clipboard (e.g. select and copy it from anywhere on the page, or from any other app).
3. Focus the opacity field, select all, paste (`Cmd+V` / `Ctrl+V`).
4. Tab away or click elsewhere to blur.
5. Repeat steps 1–4 several times — roughly half the attempts will leave the field stuck on the raw `150`.

**Typing the digits by hand at a normal pace will not reliably reproduce this** — use one of the two methods above.

**Summary of repeated-trial evidence:** hand-typed input at a normal pace (~120ms/keystroke) never reproduces it (0/8 and a separate 0/6 across two trials). A single fast value+`input`-event dispatch (the closest proxy for a paste) reproduces it deterministically (6/6). Fast synthetic character-by-character typing and a genuine `Cmd+V` clipboard paste both reproduce it intermittently (roughly 1/3–1/2 of trials). Once stuck, the field stays stuck (confirmed up to 10s post-blur) — it either resolves quickly or never resolves, it does not "catch up" slowly. Compare with negative input (`-10`), which reformats correctly and consistently every time regardless of typing speed — only the "too high" direction and only fast-arriving input reproduces the race.

This is not reachable via Vue `v-model` or any programmatic API — `bds-color-picker` has no public prop for opacity (see BUG-004), so the only way to trigger this is direct UI interaction with the opacity field.

### Scenario B — decimal input rounds for display but not internally (deterministic, separate issue)

1. Baseline: opacity field shows `100%`.
2. Focus the opacity field, select all, type `42.5`, press Tab.
3. The field reliably redisplays `43%` (rounded) in every trial.
4. But the internal applied value is `--swatch-opacity: 0.425` (the raw, unrounded 42.5%), not `0.43`. The displayed percentage and the actually-rendered transparency are off by 0.5 percentage points and will never exactly agree. This part of the bug **is** deterministic/reproduces every time — only Scenario A is a race.

---

## Steps to Reproduce

See "Most reliable way to reproduce it" and "A more 'hands-on' repro that also works, intermittently" above for the two tested repro paths (DevTools console snippet = deterministic 6/6; real clipboard paste = intermittent ~2/4). For the separate, always-reproducible decimal-rounding issue (Scenario B): open `http://localhost:3333`, scroll to "Input Edge Cases", focus the opacity field, select all (`Meta+A` on macOS), type `42.5` at any speed, Tab — the field always redisplays `43%` while the internally-applied value stays the unrounded `0.425`.

---

## Expected Behaviour

After blur, the opacity field's displayed text should **always, deterministically** match the value actually applied to the swatch/color — entering `150` should always redisplay as `100%` (matching the clamp), never sometimes-not. Entering `42.5` should either redisplay `42.5%` or apply exactly `0.43` — whichever the component intends as its rounding rule, the display and the applied value must agree, consistently.

---

## Actual Behaviour

| Input method | Field display after blur | Applied `--swatch-opacity` | Consistent? |
| --- | --- | --- | --- |
| `150`, typed by hand (~120ms/keystroke) | `100%` (every trial, 14/14 across two batches) | `1` (100%) | ✅ Yes, always |
| `150`, typed fast (synthetic, ~0ms/keystroke) | `100%` **or** raw `150` — mixed, roughly 1/3 to 1/2 of trials stuck | `1` (100%, always correctly clamped) | ❌ No, intermittently |
| `150`, single fast value+`input` event (paste-equivalent) | Raw `150`, stuck (6/6 trials) | `1` (100%) | ❌ No, reliably reproduces |
| `150`, real `Cmd+V` clipboard paste | `100%` **or** raw `150` — mixed (2/4 in one trial) | `1` (100%) | ❌ No, intermittently |
| `-10`, any input method | `0%` (every trial) | `0` (every trial) | ✅ Yes, always |
| `42.5`, any input method | `43%` (rounded, every trial) | `0.425` (unrounded, every trial) | ❌ No, always |

No console errors observed in any trial (0 errors across the full re-verification pass).

---

## Visual Evidence

Screenshots of the trigger row (swatch + HEX + opacity field), captured from two back-to-back trials of the exact same `100% → type 150 → Tab → wait 600ms` interaction:

- `ai-work/qa/bug-reports/assets/bug-003-opacity-150-typed-raw.png` — while still focused/typing (before blur): field shows raw `150`, as expected at this stage.
- `ai-work/qa/bug-reports/assets/bug-003-opacity-150-stuck-after-blur.png` — **trial 1**, 600ms after blur: field is still stuck on `150` (no `%`), even though the swatch's applied opacity is already correctly 100%.
- `ai-work/qa/bug-reports/assets/bug-003-opacity-150-recovered-after-blur.png` — **trial 2** (identical steps, run immediately after trial 1), 600ms after blur: field correctly shows `100%`.
- `ai-work/qa/bug-reports/assets/bug-003-opacity-42_5-decimal-rounds-to-43pct.png` — decimal case, reliably shows `43%` (vs. the unrounded `0.425` applied internally).
- `ai-work/qa/bug-reports/assets/bug-003-opacity-neg10-correctly-clamps-0pct.png` — negative case, for contrast: reliably and correctly shows `0%`, checkerboard visible through the now-fully-transparent swatch.

---

## Impact

Medium, but low-frequency: the committed HEX color itself is never corrupted, and a user who types an out-of-range opacity by hand will essentially never see this. It only surfaces when a value arrives quickly — pasting an out-of-range percentage, or an unusually fast input method — leaving the field's displayed text stuck on the raw, unclamped input while the actually-applied opacity is silently different from what's shown. A real but narrow edge case, not a general opacity-validation failure.

---

## Suggested Fix

- Scenario A: the fact that slow, hand-paced keystrokes never reproduce it while a single fast value+event (paste-equivalent) reproduces it every time strongly suggests a debounce/throttle on the `input` handler (or a `requestAnimationFrame`-deferred reformat, consistent with Stencil's async re-render batching) that gets reset or skipped when the value changes and blurs faster than the debounce window. Investigate the opacity field's `input`/`blur`/reformat handler chain for a timer that can be starved or cancelled by a fast value-then-blur sequence — the fix needs to guarantee the field is re-rendered from the clamped/committed value synchronously on `blur` (or `change`), not rely on a timer that a fast interaction can race past.
- Scenario B: on blur/commit, always re-render the opacity field's displayed text from the same clamped, rounded value that is written to `--swatch-opacity`/the committed alpha channel — never leave the field showing a rounding that doesn't match the internally-stored precision.

---

## Related

- Test plan: `ai-work/qa/test-plans/EOA-17362-bds-color-picker-test-plan.md` → TC-EDGE-004
- Possibly related root cause: `EOA-17362-bds-color-picker-bug-001.md` (internal event-leak / re-render timing issues in the same opacity field)
- **Not reachable via `.value`/Vue `v-model`/programmatic assignment**: this bug only reproduces through direct UI interaction with the opacity field (typing fast, or pasting). There is currently no public API to set opacity programmatically at all — see the addendum in `EOA-17362-bds-color-picker-bug-004.md`.
