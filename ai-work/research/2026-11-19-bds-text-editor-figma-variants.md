---
ticket: EOA-18739
component: bds-text-editor
status: exploring
---

# T7 Figma research: bds-text-editor (file rtiE5zGA4aoOuxIQMgfD6h, set 14:34765)

Method: `get_metadata` for the 48 variants, `get_design_context` on 14:34946, then read-only `use_figma` dumps of every variant (bound variable names, fills, strokes, effects, text styles) diffed against a baseline, and `get_variable_defs` for values. Plain nodes were diffed against their Outline counterparts. Screenshots checked: Outline Default and Error Focus content frame at 4x, Plain Hover and Plain Focus.

## 0. Findings that change the plan (read first)

1. **Disabled+Error and Readonly+Error are not designs.** All 8 nodes at 192 tall (14:35036, 14:35041, 14:35046, 14:35051 and Plain 3332:85432, 85437, 85442, 85447) contain a single `_skeleton/TextEditor` layer: Label 48x16, Field 448x152, Footer 448x16, each filled `ui (components)/base-light` radius 2. The extra 40 = 192 - 152 is the skeleton's own stack (16 + 4 + 152 + 4 + 16). There is no error styling for disabled or readonly. Suggested rule: disabled and readonly ignore `error`.
2. **Plain is only really specified for 3 of 24 states.** Plain Default empty (3332:85162), Plain Default populated (3332:85177) and Plain Disabled populated (3332:85467) differ from Outline (container border hidden, toolbar bottom border only). Every other Plain node (Hover, Focus, Active, all Error, Readonly, Disabled empty) is a line-for-line copy of its Outline node: full 1px container border and the toolbar's four-side border. Confirmed on screenshots of Plain Hover (3332:85192) and Plain Focus (3332:85222): both show the full outline. Plain Disabled empty (3332:85452) is also an Outline copy, while Plain Disabled populated is not, so the set is internally inconsistent.
3. **Container border vs toolbar border.** The toolbar frame has its own 1px stroke on four sides (Outline) inside the container's 1px stroke, but at 4x only one border shows around the box: the container's stroke is drawn over the toolbar's, so in Error the whole perimeter is `stroke/danger-base` including the toolbar zone, and only the toolbar's bottom line (`stroke/default-light`) is visible as a divider. In CSS the toolbar needs only `border-bottom` in both variants. `bds-toolbar border="all"` (current render code) would draw a second 1px on top, sides and corners inside the container border.
4. **Toolbar height 41 = 32 button + 2 x 4 + 1 bottom border.** The frame is fixed at 41 with padding 12 on four sides, so Figma clips and centres the 32 high items; the effective vertical padding is 4 (`spatial/padding/2xs`), horizontal is 12 (`spatial/padding/s`). `bds-toolbar density="comfortable"` (padding 12 all sides) would give 57. Use padding-block `$boreal-spatial-padding-2xs` and padding-inline `$boreal-spatial-padding-s`, or a fixed height 41 with the same centring.
5. **Hover shadow is `Box shadow/s`, not the shared `bds-hover-shadow` mixin.** `bds-hover-shadow` is `$boreal-depth-box-shadow-xs` (0 1px 2px). Figma is 0 2px 4px = `$boreal-depth-box-shadow-s`. The form field shell has no `:hover` rule at all.
6. **Focus keeps the grey border.** In every Focus frame the container stroke stays `stroke/default-light` (or `stroke/danger-base`) under the ring. The shared shell `--focused` sets `border-color: $boreal-stroke-focus`, and `--plain.--focused` does the same. Error stays danger because `--error` comes later in source. Decide whether the editor follows the shell (matches bds-text-field) or the editor frames.

## 1. Dimensions and structure (all variants)

| Item | Value | Source |
| --- | --- | --- |
| Component | 448 x 152 (Default, Hover, Focus, Active, Disabled, populated or not) | all 152 nodes |
| Stack | Label 16 + gap 4 + Content frame 112 + gap 4 + Footer 16 = 152 | `Container` frame, `spatial/gap/2xs` |
| Container (Content frame) | 448 x 112, vertical, no padding, clips content, radius `radius/xs` all corners | 14:34766 |
| Toolbar | 448 x 41, horizontal, padding 12 (`spatial/padding/s`) bound on all sides, gap 12 (`spatial/gap/s`), items centred, top radii `radius/xs`, bottom radii 0, clips content | see finding 4 |
| Editable area (Content) | 448 x 71 = 112 - 41, vertical, padding x 12 (`spatial/padding/s`), y 6 (`spatial/padding/1xs`), fill `ui (components)/inverse`, no radius | 14:34956 |
| Readonly empty | Container 448 x 122; Content 82 (padding 6 / 0 / 6 / 0), Toolbar layer present but HIDDEN | 14:34886 |
| Readonly populated | 448 x 72; Content 32 = 6 + 20 + 6 | 14:34901 |
| Label row | 448 x 16, `supporting/label/xs` (12/16 semibold), `text/default-darker` | owned by `bds-typography variant=label` |
| Footer | 448 x 16, gap 12 (`spatial/gap/s`), items start, justify end, helper (flex 1, 416 wide) + counter right ("0/0"), `body/xs` 12/16 regular | verify only |
| Minimum height | Not stated. 71 (editable with toolbar), 112 (box) and 152 are the frame heights of a fixed demo; 82 and 32 are the readonly heights. Hug versus min-height is not designed | open question |
| Overflow / max-height / scroll | Not designed. The container clips (`overflow: clip`) only to keep the radius | open question |

Toolbar contents: `Buttons` (ButtonGroups instance: Orientation Horizontal, Button Variant Plain, Steps x2, Button Color Default) containing Button1 (Medium, Plain, Default, emoji icon + disclosure, 50 x 32) and Button2 (link icon, 32 x 32); each button padding 4 / 6 (`spatial/padding/2xs`, `spatial/padding/1xs`; Button2 binds the older variable `spacing/1xs` = 6), content padding 2 (`spatial/padding/3xs`), icon 16, radii joined (`radius/xs` outer, `radius/none` inner). Then Divider 1 x 18 (`ui (components)/default-lighter`, width `stroke/xs`), then Slot (Guide zone 51 x 32, dashed `stroke/default-light`, fill `ui (components)/default-lighter`, "Slot" heading/sm `text/default`). The buttons are the library `Button Variant=Plain` at `Button State=Default` in every state except Disabled. **No hover, focus or active state for toolbar buttons is designed** (not even in Focus/Active frames); `bds-button` owns them.

## 2. Token map (Figma variable -> value in the frames -> repo)

| Figma variable | Value | SCSS (injected, no `@use`) |
| --- | --- | --- |
| `ui (components)/default-base` | #f7f7f8 | `$boreal-ui-default-base` |
| `ui (components)/inverse` | #fff | `$boreal-ui-inverse` |
| `ui (components)/default-lighter` | #f7f7f8 | `$boreal-ui-default-lighter` |
| `ui (components)/default-light` | #d3d4d9 | `$boreal-ui-default-light` |
| `ui (components)/base-light` | skeleton only | not needed |
| `stroke/default-light` | #e3e3e6 | `$boreal-stroke-default-light` |
| `stroke/danger-base` | #c7242b | `$boreal-stroke-danger-base` |
| `stroke/xs` (1) / `stroke/none` (0) | 1 / 0 | no token exists; shell and `bds-toolbar` use literal `1px` |
| `radius/xs` / `radius/none` | 4 / 0 | `$boreal-radius-xs` / `$boreal-radius-none` |
| `text/default-darker` | #131316 | `$boreal-text-default-darker` |
| `text/default-light` | #8a8e96 | `$boreal-text-default-light` (placeholder, helper, counter) |
| `text/disabled` | #b6b8be | `$boreal-text-disabled` |
| `text/danger-base` | #c7242b | `$boreal-text-danger-base` (bds-typography does this) |
| `text/default` | #272a2f | `$boreal-text-default` |
| `icon/default-dark` / `icon/disabled` | #8a8e96 / #b6b8be | `$boreal-icon-default-dark` / `$boreal-icon-disabled` (bds-button owns) |
| `spatial/padding/s`, `1xs`, `2xs`, `3xs` | 12, 6, 4, 2 | `$boreal-spatial-padding-s`, `-1xs`, `-2xs`, `-3xs` |
| `spatial/gap/s`, `2xs`, `3xs` | 12, 4, 2 | `$boreal-spatial-gap-s`, `-2xs`, `-3xs` |
| `body/sm` | Inter 14 / 20 regular | `$boreal-typography-font-size-sm`, `-line-height-sm`, `-font-weight-regular`, family `$boreal-typography-font-family-primary` |
| `Box shadow/s` (hover) | 0 2px 4px 0 #13131626 (`depth/y/s`, `depth/blur/s`, `depth/spread/none`, `depth/color/base`) | `$boreal-depth-box-shadow-s` |
| `Box shadow/focus` | spread 1 `depth/state/focus/inner-color` #fff, then spread 3 `depth/state/focus/outer-color` #9ec5ff (`depth/spread/xs`, `depth/spread/m`) | `$boreal-depth-box-shadow-focus` (`0 0 0 1px white, 0 0 0 3px var(--boreal-focus)`), mixin `bds-focus-ring` |
| `Box shadow/active` | focus layers plus INNER 0 1px 2px `depth/state/active/Color` #13131626 (`depth/y/xs`, `depth/blur/xs`) | `$boreal-depth-box-shadow-active`, mixin `bds-focus-ring-active` |

Hex values are the engage theme as Figma resolves them; the repo variables are theme-driven.

## 3. Shared rules that already exist (`forms/_shared/_form-field-shell.scss`, `bds-transition-surface`, `bds-focus-ring`)

Included via `@include form-field-shell('bds-text-editor')`. Selectors are class based (`.bds-text-editor`, host carries the class from `classMap`). The editor's SCSS currently does not include the shell.

| Need | Shell provides | Verdict for T7 |
| --- | --- | --- |
| Host layout | `.p` flex column, gap `spatial-gap-2xs` (= Figma 4), width `var(--p-width, 100%)` (customWidth mechanism, `hostStyle` sets `--bds-text-editor-width`), font family, colour | covered |
| Container border + radius + transition | 1px `stroke-default-light`, radius `var(--p-radius, radius-xs)`, `bds-transition-surface`, overflow hidden | covered, but container background is `ui-inverse` (Figma container is default-base; toolbar and editable cover it, so invisible) |
| Container padding / min-height / alignment | padding 6 / left 8, `min-height: spatial-layout-l`, `align-items: center`, row flex | **must override**: `padding: 0; min-height: <decided>; align-items: stretch; flex-direction: column` |
| Focus | `--focused` container: border `stroke-focus`, z-index 1, `bds-focus-ring` | ring matches `Box shadow/focus`; border colour differs (finding 6). Selector is the host `--focused` class, not `:focus-within` (plan wants `:focus-within`; the host class stays on while the link popover is open, popover sits outside the container) |
| Error | `--error` container border `stroke-danger-base` | covered, matches all Error frames (border, and helper/counter via `bds-typography error`) |
| Disabled | `--disabled`: cursor not-allowed, container bg `ui-default-lighter`, border default-light, `pointer-events: none` | covered for the container; **add** toolbar bg `ui-default-lighter`, editable bg `ui-default-lighter`, editable text `text-disabled`, divider colour, `-` placeholder |
| Readonly | `--readonly`: bg transparent, `border: none` | covered for the container; **add** no toolbar (render code already hides it), editable padding `padding-block 1xs; padding-inline 0` |
| Plain | `--plain`: container border transparent; focused plain border `stroke-focus` | covers Plain Default container; **add** toolbar `border-bottom` only (and see finding 2 on Plain Hover/Focus/Error) |
| Footer | `__footer` flex, space-between, align center | counter right aligned OK; **no gap** (Figma 12 = `spatial-gap-s`); no change in height |
| Hover | none | **add** (`Box shadow/s`) |
| Active | none (only `bds-focus-ring-active` mixin exists) | **add** (`Box shadow/active`) |

Editor-local rules T7 must write: container column flex reset and overrides above, toolbar row (bottom border, bg `ui-inverse`, height 41 / padding, top radii `radius-xs`), editable box (padding 6 / 12, bg `ui-inverse`, font from `body/sm`, caret colour, placeholder colour, `outline: none`, pre-wrap reset already present), state rules for hover/active/disabled/readonly parts, field chip, link form.

## 4. State matrix

Notation: C = container (Content frame, fill `default-base`, radius xs). T = toolbar. E = editable (Content, padding 6/12, fill `inverse`). Shadow names are Figma effect styles. "base border" = `stroke/xs` `stroke/default-light` on all sides. Populated rows differ from the empty row only in the E text; see section 5.

### Outline

| Node | State / Error / Populated | Container | Toolbar | Editable and text | Other | CSS mapping |
| --- | --- | --- | --- | --- | --- | --- |
| 14:34766 | Default / no / empty | base border, no shadow | 41, fill `inverse`, border all (hidden under C), bottom line `default-light` | placeholder "Your placeholder goes here" `text/default-light` body/sm | label `text/default-darker`; helper, counter `text/default-light` | shell default; T bottom border; `::placeholder`-like colour `$boreal-text-default-light` |
| 14:34781 | Default / no / populated | as above | as above | "Your text goes here" `text/default-darker` | no caret | text `$boreal-text-default-darker` |
| 14:34796 | Hover / no / empty | + `Box shadow/s` | same | **caret "I" 4x20 `text/default-darker` instead of placeholder** | | `.container:hover` -> `$boreal-depth-box-shadow-s` |
| 14:34811 | Hover / no / populated | + `Box shadow/s` | same | text + caret after it (130 + gap 4 + 4 = 138) | | as above |
| 14:34826 | Focus / no / empty | + `Box shadow/focus` (border unchanged `default-light`) | same | caret only, no placeholder | | shell `--focused` ring; border colour: finding 6 |
| 14:34841 | Focus / no / populated | as Focus | same | text + caret | | as above |
| 14:34856 | Active / no / empty | + `Box shadow/active` | same | caret only | | `$boreal-depth-box-shadow-active` (mixin `bds-focus-ring-active`) on `:active` while focused |
| 14:34871 | Active / no / populated | as Active | same | text + caret | | as above |
| 14:35056 | Disabled / no / empty | base border, no shadow, fill unchanged | fill `default-lighter`, border `default-light`; buttons State=Disabled, each radius xs (not joined); icons `icon/disabled`; divider line `ui (components)/default-light` (darker than the enabled `default-lighter`) | fill `default-lighter`; text `-` 7x20 `text/disabled` | label `text/disabled`; helper, counter unchanged `default-light` | shell `--disabled`; add T/E bg `$boreal-ui-default-lighter`, text `$boreal-text-disabled` |
| 14:35071 | Disabled / no / populated | as above | as above | text `text/disabled` | | as above |
| 14:34886 | Readonly / no / empty | no border, no fill, radius xs; 448 x 122 | layer HIDDEN | padding 6 / 0 / 6 / 0; text "Your text goes here" `text/default-darker` (E 82 tall) | | shell `--readonly`; E `padding-block $boreal-spatial-padding-1xs; padding-inline 0` |
| 14:34901 | Readonly / no / populated | as above; 448 x 72 | HIDDEN | same, E 32 tall (hugs one line) | | as above |
| 14:34916 | Default / yes / empty | border `stroke/danger-base` | unchanged (stroke `default-light` hidden under C) | placeholder `default-light` | helper, counter `text/danger-base` | shell `--error` |
| 14:34931 | Default / yes / populated | danger border | unchanged | text `default-darker` | helper `text/danger-base`; **counter stays `text/default-light`** | shell `--error`; counter colour is a Figma inconsistency (finding list below) |
| 14:34946 | Hover / yes / empty | danger border + `Box shadow/s` | unchanged | caret only | helper, counter danger | hover shadow + error border |
| 14:34961 | Hover / yes / populated | danger border + `Box shadow/s` | unchanged | text + caret | helper danger; counter default-light | as above |
| 14:34976 | Focus / yes / empty | danger border + `Box shadow/focus` | unchanged | caret only | helper, counter danger | `--error` after `--focused` keeps the border danger |
| 14:34991 | Focus / yes / populated | danger border + focus | unchanged | text + caret | helper danger; counter default-light | as above |
| 14:35006 | Active / yes / empty | danger border + `Box shadow/active` | unchanged | caret only | helper, counter danger | active shadow + error border |
| 14:35021 | Active / yes / populated | danger border + active | unchanged | text + caret | helper danger; counter default-light | as above |
| 14:35041 | Disabled / yes / empty | **skeleton only, 448 x 192** | n/a | n/a | `_skeleton/TextEditor` | no design: disabled ignores error |
| 14:35036 | Disabled / yes / populated | skeleton, 192 | n/a | n/a | | as above |
| 14:35051 | Readonly / yes / empty | skeleton, 192 | n/a | n/a | | no design: readonly ignores error |
| 14:35046 | Readonly / yes / populated | skeleton, 192 | n/a | n/a | | as above |

### Plain

Differences from the Outline counterpart (diff of every layer, depth 9):

| Node | State / Error / Populated | Differs from Outline | CSS mapping |
| --- | --- | --- | --- |
| 3332:85162 | Default / no / empty | C stroke hidden (invisible, weight 1 kept); T stroke `default-light` bottom only (weights 0 / 0 / 1 / 0) | shell `--plain` transparent border; T `border-bottom: 1px solid $boreal-stroke-default-light` |
| 3332:85177 | Default / no / populated | same as above | same |
| 3332:85467 | Disabled / no / populated | C stroke hidden; T bottom only; T fill `default-lighter` | same plus disabled T/E bg |
| 3332:85452 | Disabled / no / empty | **none, identical to Outline 14:35056** | follow the Outline rule or ask design |
| 3332:85192, 85207 | Hover / no / empty, populated | none (full border, shadow `Box shadow/s`, toolbar border four sides) | design copy; see open question |
| 3332:85222, 85237 | Focus / no / empty, populated | none (full border + `Box shadow/focus`) | shell `--plain.--focused` gives a blue border; Figma keeps grey |
| 3332:85252, 85267 | Active / no / empty, populated | none | as above |
| 3332:85282, 85297 | Readonly / no / empty (122), populated (72) | none (readonly has no border either way) | `--readonly` covers |
| 3332:85312, 85327 | Default / yes / empty, populated | none (danger border full, toolbar four sides) | shell `--error` after `--plain` keeps danger border visible? Check: `--plain` is later and sets `border-color: transparent`, so a plain error container would lose the danger border. Must verify and fix |
| 3332:85342, 85357 | Hover / yes | none | as above |
| 3332:85372, 85387 | Focus / yes | none | as above |
| 3332:85402, 85417 | Active / yes | none | as above |
| 3332:85432, 85437, 85442, 85447 | Disabled / Readonly with Error | skeleton, 192 | no design |

Source-order check done on the shell: `--focused`, `--error`, `--disabled`, `--plain` (then `--plain.--focused`), `--readonly`. Same specificity (one class plus one descendant), so `--plain` beats `--error` and `--focused` on `border-color`, except `--plain.--focused` (higher specificity) which wins. A plain error container therefore renders a transparent border today.

## 5. Content, caret and text details

| Item | Value |
| --- | --- |
| Typography | `body/sm`: font-size `$boreal-typography-font-size-sm` (14), line-height `-line-height-sm` (20), weight regular (400), family primary, left aligned |
| Padding | x `spatial/padding/s` (12), y `spatial/padding/1xs` (6); readonly x 0, y 6 (binds the older `spacing/1xs`, value 6) |
| Text colour | `text/default-darker` (populated, readonly, caret); `text/disabled` (disabled); `text/default-light` (placeholder) |
| Placeholder | `text/default-light`, "Your placeholder goes here". In Hover, Focus and Active (empty) the placeholder is replaced by a caret "I"; Figma shows no placeholder while focused. Disabled empty shows "-" in `text/disabled` |
| Caret | a text node "I" (4 x 20, `text/default-darker`, body/sm), inline after the text with gap 4 (`spatial/gap/2xs`). Not a pixel width in the design. Maps to `caret-color: $boreal-text-default-darker` |
| Line box | one line = 20, so one-line editor = 12 + 20 = 32 (readonly populated 32) |
| Min height | undetermined (see section 1) |
| Overflow | undetermined |

## 6. Focus ring scope (answer)

The `Box shadow/focus` (and `Box shadow/active`, `Box shadow/s` on hover) effect is on the **Content frame (the bordered container, toolbar included)** in every state, never on the whole component (label and footer sit outside) and never on the toolbar or editable separately. The 4x screenshot of Error Focus shows white 1px ring then blue 3px ring wrapping the red container border. The toolbar buttons stay `State=Default` in every state frame, so there is no designed focus or active styling for the toolbar buttons or for a focused toolbar tool; `bds-button`'s own `:focus-visible` ring applies and the container ring staying while a tool has focus is the open question already recorded in T7. The box shadow is not clipped by the container `overflow` because it is on the same element.

## 7. Not in the design (decided by us)

Field chip, link popover, Fields text-only trigger (`bds-dropdown` trigger with a label), hover/focus/disabled looks for toolbar buttons beyond the library Plain button, readonly or disabled error. The chip is styled from the gray `bds-tag` tokens (design validated 2026-11-17).

## 8. Open questions for design

1. Plain Hover, Focus, Active, Error, Readonly, Disabled empty are Outline copies (full border). Should Plain show a border in those states (as the frames do), or keep the Default look (no border, toolbar bottom line only) with only the ring added? The shell treats plain as transparent border plus blue focus border.
2. Disabled and Readonly with Error are skeleton frames: confirm that error is ignored for both.
3. Populated + Error: helper is danger but the counter stays `text/default-light` (empty + Error: both danger). Intentional?
4. Focus border: keep `stroke/default-light` under the ring (the frames) or switch to the focus colour like `bds-text-field` (shell)?
5. Should the placeholder hide on focus (frames replace it with the caret)?
6. Editable minimum height (71 with toolbar? 59 content?), and behaviour for long content (grow forever, max-height with scroll)? Readonly empty is 82 tall, populated 32.
7. Disabled divider is `ui (components)/default-light` while the enabled one is `default-lighter`; intentional?
8. Disabled empty shows "-" instead of the placeholder; implement or keep the placeholder?
9. Where does the Active (pressed) shadow apply: while the pointer is down on the editable only, or on any press inside the container (toolbar buttons included)?
10. `Button2` and readonly editable bind `spacing/1xs` instead of `spatial/padding/1xs` (same value 6); likely a stale variable, no action unless the values diverge per theme.

## 9. Checklist status after this pass

- Plain variant (container, toolbar, every state): pulled and diffed (24 nodes), section 4. Done.
- Container Default, Hover, Focus, Active: done. Disabled: done. Readonly: done (empty 122, populated 72).
- Error = true Default, Hover, Focus, Active, empty and populated: done. Disabled+Error and Readonly+Error: pulled, they are skeletons.
- Populated Default, Focus (and Hover, Active, Disabled, Readonly): done.
- Toolbar height, padding, bottom border, top radii, gaps: done (finding 4).
- Content padding, typography, placeholder colour, caret: done. Min height and overflow: not designed (questions 6).
- Footer spacing: verified (gap 12 missing from the shell; owned by `renderFieldFooter`).
- Field chip: not in Figma (decided by us).
- Dimensions 448 x 152 and toolbar 41: confirmed.
