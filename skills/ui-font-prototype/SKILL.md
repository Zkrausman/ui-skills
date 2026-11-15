---
name: ui-font-prototype
description: Create original geometric font prototypes and comparison specimens when the user wants new glyph designs, rather than selecting, renaming, or fitting an existing font. Use for experimental ASCII display type; production text families need further design and qualification.
---

# Original font prototypes

Distinguish font selection, licensed adaptation, and original type design. Do not fulfill “brand new fonts” with renamed existing fonts. Author geometry independently and retain the editable generation source. Record any shared skeleton across faces: construction variants are not unrelated mature type families.

Establish use, a new family name, character coverage and the desired construction from the user's brief. The bundled starter has original uppercase and lowercase, digits and punctuation: U+0020–U+007E, 95 printable ASCII codepoints. It is Regular only. It retains overlapping contours and has no kerning, ligatures, accents or complex-script shaping. Extend the geometry for a brief; do not describe the starter as a production body-font system.

## Generate and inspect

The scripts use Python 3. Standard-library geometry and SVG preview work without packages. TTF generation and binary checks require FontTools already installed in the selected runtime. Check availability with `python3 -c "import fontTools"`. If absent, report that font generation is blocked; do not install software, download a runtime or claim that fonts were built. Existing dependency permissions still apply.

Run scripts relative to this skill directory, substituting fresh output paths:

```sh
python3 scripts/preview.py /absolute/new-outline-sheet.svg --construction rounded
python3 scripts/build_font.py --family "Original Geometry" --construction rounded --out /absolute/new-font-directory
python3 scripts/check_fonts.py /absolute/new-font-directory
```

`preview.py` writes a new SVG contact sheet, refusing an existing output. It displays geometry only, not shaping or rasterization of a font. `build_font.py` refuses any existing output directory, loads no base font, and produces a TTF, a manifest and an offline HTML specimen embedding that font. `--construction angular`, `--stroke 40..100` and `--width 0.7..1.3` vary the shared skeleton; lowercase is independently drawn, not substituted small capitals. Widths are proportional to actual outline bounds. These parameters are starting points; optical spacing still needs design work.

The checker exits nonzero for empty input, unreadable fonts, missing promised glyphs, empty non-space outlines or bounds outside advances/vertical metrics. Its scope is static TrueType ASCII structure, not comprehensive font QA. Do not call FontBakery, kerning, shaping, app compatibility, checksum conformance or readability passed unless separately tested. A reopened binary or contact sheet is insufficient evidence of good typography.

Render the actual embedded TTF specimen at display and body sizes using an already available, authorized renderer. Inspect uppercase, lowercase, digits, punctuation, ambiguous glyphs and short text with the same copy and size across candidates. Explanatory labels use a separate system font. If PDF is wanted, embed the actual fonts using an available renderer and inspect every page. Do not install renderers, use an existing browser profile, or silently substitute SVG geometry for a rendered-font specimen. Report missing render capability and unrun checks explicitly.

## Handoff and refinement

Package the original generation source, fonts, exact coverage, limitations, font-license decision and hashes. The source-code MIT license does not automatically license the generated fonts; obtain the owner's distribution terms before publishing them. The builder intentionally assigns no font license. Do not publish font binaries, personal specimens or manifests merely because a toolkit skill is being added. Do not install fonts, change document defaults or publish generated material as a side effect of specimen creation.

Keep selections pending until the owner chooses. Then refine optical spacing, contours, overlaps, punctuation, languages and weights and test in the intended document applications. Keep structural, visual and production qualification outcomes separate. See [SOURCE.md](SOURCE.md) for this starter's provenance and scope.
