"""Structurally check locally generated static TrueType ASCII prototypes."""
import argparse
import json
from pathlib import Path
import sys


def inspect_font(path, loader):
    errors = []
    coverage = 0
    try:
        with loader(path, checkChecksums=2) as font:
            for table in ('glyf', 'hmtx', 'hhea', 'head', 'cmap'):
                if table not in font:
                    raise ValueError('Requires static TrueType table: ' + table)
            cmap = font.getBestCmap() or {}
            glyf = font['glyf']
            for code in range(32, 127):
                name = cmap.get(code)
                if name is None or name == '.notdef':
                    errors.append(f'missing U+{code:04X}')
                    continue
                coverage += 1
                glyph = glyf[name]
                coordinates, _, _ = glyph.getCoordinates(glyf)
                if code != 32 and not len(coordinates):
                    errors.append(f'empty U+{code:04X}')
                if code == 32 and len(coordinates):
                    errors.append('space has an outline')
                advance, _ = font['hmtx'][name]
                if advance <= 0:
                    errors.append(f'nonpositive advance U+{code:04X}')
                if len(coordinates):
                    xs, ys = zip(*coordinates)
                    if min(xs) < 0 or max(xs) > advance:
                        errors.append(f'horizontal bounds U+{code:04X}')
                    if max(ys) > font['hhea'].ascent or min(ys) < font['hhea'].descent:
                        errors.append(f'vertical bounds U+{code:04X}')
    except Exception as error:
        errors.append(f'{type(error).__name__}: {error}')
    return {'file': path.name, 'ascii_codepoints': coverage, 'errors': errors}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args(argv)
    if not args.directory.is_dir():
        parser.error('Expected an existing font directory')
    paths = sorted(args.directory.glob('*.ttf'))
    if not paths:
        parser.exit(1, 'No .ttf files found; no validation was performed.\n')
    if any(path.is_symlink() or not path.is_file() for path in paths):
        parser.exit(1, 'Only regular, non-symlink .ttf inputs are supported.\n')
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        parser.exit(2, 'FontTools is unavailable. Font validation was not run; do not install dependencies without separate authorization.\n')
    results = [inspect_font(path, TTFont) for path in paths]
    print(json.dumps({'scope': 'Static TrueType printable ASCII structure only', 'results': results}, indent=2))
    return int(any(result['errors'] for result in results))


if __name__ == '__main__':
    sys.exit(main())
