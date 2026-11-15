"""Build an original ASCII display prototype using already available FontTools."""
import argparse
import base64
import hashlib
import html
import io
import json
from pathlib import Path
import re
import sys

from outlines import contours


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', required=True, help='New ASCII family name, 1–48 letters/digits/spaces')
    parser.add_argument('--out', required=True, type=Path, help='New output directory; existing paths are refused')
    parser.add_argument('--construction', choices=['rounded', 'angular'], default='rounded')
    parser.add_argument('--stroke', type=float, default=70)
    parser.add_argument('--width', type=float, default=1.0)
    parser.add_argument('--copyright', default='', help='Owner-supplied notice; no font license is inferred')
    args = parser.parse_args(argv)
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9 ]{0,47}', args.family) or args.family != args.family.strip():
        parser.error('Use a new ASCII family name without leading/trailing spaces')
    try:
        contours('A', args.stroke, args.width, args.construction)
    except ValueError as error:
        parser.error(str(error))
    if args.out.exists() or args.out.is_symlink():
        parser.error('Output path already exists; choose a fresh directory')
    try:
        from fontTools.fontBuilder import FontBuilder
        from fontTools.pens.ttGlyphPen import TTGlyphPen
        from fontTools.ttLib import TTFont
    except ImportError:
        parser.exit(2, 'FontTools is unavailable in this Python runtime. No files written. Do not install dependencies without separate authorization.\n')

    cmap = {code: f'uni{code:04X}' for code in range(32, 127)}
    order = ['.notdef', *cmap.values()]
    glyphs, metrics = {}, {}
    for name, character in [('.notdef', '?'), *((name, chr(code)) for code, name in cmap.items())]:
        polygons, advance = contours(character, args.stroke, args.width, args.construction)
        pen = TTGlyphPen(None)
        for polygon in polygons:
            pen.moveTo(polygon[0])
            for point in polygon[1:]:
                pen.lineTo(point)
            pen.closePath()
        glyphs[name] = pen.glyph()
        metrics[name] = (advance, 70 if polygons else 0)
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=900, descent=-300)
    fb.setupOS2(sTypoAscender=900, sTypoDescender=-300, usWinAscent=900,
                usWinDescent=300, fsSelection=64, usWeightClass=400)
    family_id = args.family.replace(' ', '')
    names = {'familyName': args.family, 'styleName': 'Regular',
             'uniqueFontIdentifier': family_id + '-Prototype-1.000',
             'fullName': args.family + ' Regular', 'psName': family_id + '-Regular',
             'version': 'Version 1.000'}
    if args.copyright:
        names['copyright'] = args.copyright
    fb.setupNameTable(names)
    fb.setupPost()
    fb.setupMaxp()
    # Fixed source epoch makes repeat builds comparable, without wall-clock metadata.
    fb.font['head'].created = fb.font['head'].modified = 2082844800
    fb.font.recalcTimestamp = False
    buffer = io.BytesIO()
    fb.font.save(buffer)
    data = buffer.getvalue()
    with TTFont(io.BytesIO(data), checkChecksums=2) as reopened:
        if len(reopened.getBestCmap()) != 95:
            raise ValueError('Generated font failed coverage reopening')
    title = html.escape(args.family)
    # Use only promised ASCII in the actual comparison; labels use system fonts.
    sample = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz\n0123456789 !? @#$% &* () [] {}\nIl1 O0 rn m\nThe quick brown fox jumps over the lazy dog.'
    page = ('<!doctype html><meta charset="utf-8"><title>' + title + '</title>'
            '<style>@font-face{font-family:Prototype;src:url(data:font/ttf;base64,'
            + base64.b64encode(data).decode() + ')}body{margin:2rem;font:16px sans-serif}'
            '.sample{font-family:Prototype;white-space:pre-wrap;overflow-wrap:anywhere}'
            '</style><h1>' + title + '</h1><p>Experimental ASCII display prototype. '
            'Same text at 48px and 16px; neither size is quality-qualified.</p>'
            + ''.join('<div class="sample" style="font-size:' + str(size) + 'px">'
                      + html.escape(sample) + '</div>' for size in (48, 16)))
    manifest = {'family': args.family, 'construction': args.construction,
                'stroke': args.stroke, 'width': args.width, 'weight': 'Regular',
                'coverage': 'U+0020–U+007E: 95 printable ASCII codepoints',
                'sha256': hashlib.sha256(data).hexdigest(),
                'basis': 'Original centerlines; rounded/angular share one skeleton; no base font loaded',
                'font_license': 'Not selected; obtain the owner’s distribution decision before sharing',
                'limitations': ['Overlapping contours retained', 'No kerning or ligatures',
                                'No accented or non-ASCII glyphs', 'Not qualified for production body text'],
                'structural_validation': 'Run check_fonts.py separately',
                'visual_validation': 'Not run by this script'}
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'Prototype-Regular.ttf').write_bytes(data)
    (args.out / 'specimen.html').write_text(page, encoding='utf-8')
    (args.out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(args.out), 'font_sha256': manifest['sha256']}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
