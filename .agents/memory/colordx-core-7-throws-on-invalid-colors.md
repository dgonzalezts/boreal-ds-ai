# `@colordx/core` 7 throws `RangeError` on invalid colors where 5.6.0 returned a value

Verified on `@colordx/core` 7.3.0 against 5.6.0 (EOA-20193, 2026-11-12 to 2026-11-13).

## The Problem

`contrast()` (and other methods) throw `RangeError` on an invalid color in version 7; 5.6.0 returned a value (21 and 1 in the cases tested). `presetColors` in `bds-color-picker` is consumer-supplied, so one invalid entry would crash the render.

## The Fix

`getContrastVariant` in the `bds-color-picker` helpers resolves invalid input to `#000000` before calling the library. Do the same for any new call that takes consumer input.

Other verified differences from 5 to 7 on the picker's surface:

- uppercase or padded `transparent` is accepted;
- HSL hue is 0 for colors with saturation about 0.01;
- contrast values move by up to 0.02.

## How to verify

Technique worth reusing for any major upgrade of a pure library: a differential script that loads both published tarballs side by side in Node and compares tens of thousands of inputs, run before writing characterization tests. Then run the `bds-color-picker` specs.
