"""Exercise geometry and CLI boundaries; run actual TTF checks only if available."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/ui-font-prototype/scripts'
sys.path.insert(0, str(SCRIPTS))
from outlines import S, contours


def invoke(script, *args):
    return subprocess.run([sys.executable, '-B', str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True, timeout=30)


class FontPrototypeTests(unittest.TestCase):
    def test_promised_geometry_and_metrics(self):
        self.assertEqual(set(S), {chr(code) for code in range(33, 127)})
        for construction in ('rounded', 'angular'):
            for stroke in (40, 100):
                for width in (.7, 1.3):
                    for code in range(32, 127):
                        polygons, advance = contours(chr(code), stroke, width, construction)
                        self.assertEqual(bool(polygons), code != 32)
                        self.assertGreater(advance, 0)
                        for polygon in polygons:
                            self.assertGreaterEqual(len(polygon), 3)
                            area = sum(a[0]*b[1]-a[1]*b[0] for a, b in zip(polygon, polygon[1:]+polygon[:1]))
                            self.assertLess(area, 0, (construction, code, polygon))
                            for x, y in polygon:
                                self.assertTrue(0 <= x <= advance, (code, x, advance))
                                self.assertTrue(-300 <= y <= 900, (code, y))

    def test_fresh_preview_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'sheet.svg'
            result = invoke('preview.py', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(ET.parse(output).findall('{http://www.w3.org/2000/svg}g')), 94)
            original = output.read_bytes()
            self.assertNotEqual(invoke('preview.py', output).returncode, 0)
            self.assertEqual(output.read_bytes(), original)

    def test_bad_arguments_and_existing_outputs_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'existing'
            output.mkdir()
            sentinel = output / 'keep.txt'
            sentinel.write_text('human content')
            result = invoke('build_font.py', '--family', 'Prototype', '--out', output)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(), 'human content')
            for arguments in (['--stroke', 'nan'], ['--width', 'inf'], ['--stroke', '-1']):
                fresh = Path(directory) / 'new'
                result = invoke('build_font.py', '--family', 'Prototype', '--out', fresh, *arguments)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(fresh.exists())
            self.assertNotEqual(invoke('check_fonts.py', output).returncode, 0)

    @unittest.skipUnless(importlib.util.find_spec('fontTools'), 'FontTools absent; TTF generation/validation unrun')
    def test_binary_build_and_checker(self):
        with tempfile.TemporaryDirectory() as directory:
            for construction in ('rounded', 'angular'):
                output = Path(directory) / construction
                result = invoke('build_font.py', '--family', 'Test Geometry', '--out', output,
                                '--construction', construction)
                self.assertEqual(result.returncode, 0, result.stderr)
                result = invoke('check_fonts.py', output)
                self.assertEqual(result.returncode, 0, result.stderr)
                record = json.loads(result.stdout)['results'][0]
                self.assertEqual(record['ascii_codepoints'], 95)
                self.assertEqual(record['errors'], [])
                (output / 'bad.ttf').write_bytes(b'not a font')
                result = invoke('check_fonts.py', output)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(any(row['errors'] for row in json.loads(result.stdout)['results']))

    @unittest.skipIf(importlib.util.find_spec('fontTools'), 'FontTools available')
    def test_missing_dependency_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            fresh = Path(directory) / 'new'
            result = invoke('build_font.py', '--family', 'Prototype', '--out', fresh)
            self.assertEqual(result.returncode, 2)
            self.assertIn('FontTools is unavailable', result.stderr)
            self.assertFalse(fresh.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
