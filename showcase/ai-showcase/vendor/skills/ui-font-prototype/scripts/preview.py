"""Write a new SVG outline sheet; this is geometry inspection, not a font render."""
import argparse
from pathlib import Path

from outlines import contours


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='New SVG file; never overwrites')
    parser.add_argument('--construction', choices=['rounded', 'angular'], default='rounded')
    args = parser.parse_args()
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1200">',
             '<rect width="1000" height="1200" fill="white"/>',
             '<text x="10" y="20" font-size="14">Original ASCII outline sheet; not a rendered font</text>']
    for index, code in enumerate(range(33, 127)):
        x, y = (index % 10) * 100, (index // 10) * 115 + 35
        polygons, _ = contours(chr(code), construction=args.construction)
        parts.append(f'<text x="{x+5}" y="{y+10}" font-size="10">U+{code:04X}</text>')
        parts.append(f'<g transform="translate({x} {y+85}) scale(.1 -.1)" fill="black">')
        for polygon in polygons:
            parts.append('<polygon points="' + ' '.join(f'{a},{b}' for a, b in polygon) + '"/>')
        parts.append('</g>')
    parts.append('</svg>')
    with args.output.open('x', encoding='utf-8') as output:
        output.write('\n'.join(parts))


if __name__ == '__main__':
    main()

