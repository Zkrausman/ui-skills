import contextlib
import copy
import io
import json
import math
import os
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import foundry


def example_scene():
    return {
        "version": 1,
        "title": "Relay & lamp",
        "description": "A relay routes power to an indicator.",
        "frame": {"width": 960, "height": 640, "margin": 40},
        "projection": {"azimuth": 45, "elevation": 35.264},
        "palette": {"background": "#11151b", "ink": "#eef2f7"},
        "materials": {
            "enamel": {
                "top": "#56667a",
                "x_face": "#344457",
                "y_face": "#40536a",
                "outline": "#c3cfdd",
                "glow": "#ffc765",
            }
        },
        "parts": [
            {
                "id": "relay-a",
                "label": "Relay A",
                "center": [0, 0, 0],
                "size": [120, 72, 28],
                "material": "enamel",
                "interactive": True,
                "lit": False,
            },
            {
                "id": "lamp-a",
                "label": "Lamp A",
                "center": [0, 0, 40],
                "size": [24, 24, 24],
                "material": "enamel",
                "interactive": True,
                "lit": True,
            },
        ],
    }


class SceneValidationTests(unittest.TestCase):
    def test_rejects_unknown_fields_and_duplicate_ids(self):
        scene = example_scene()
        scene["script"] = "alert(1)"
        with self.assertRaises(foundry.SceneError):
            foundry.validate_scene(scene)
        scene = example_scene()
        scene["parts"].append(copy.deepcopy(scene["parts"][0]))
        with self.assertRaises(foundry.SceneError):
            foundry.validate_scene(scene)

    def test_rejects_invalid_colors_numbers_and_bounds(self):
        scene = example_scene()
        scene["palette"]["background"] = "url(javascript:alert(1))"
        with self.assertRaises(foundry.SceneError):
            foundry.validate_scene(scene)
        scene = example_scene()
        scene["parts"][0]["center"][0] = math.inf
        with self.assertRaises(foundry.SceneError):
            foundry.validate_scene(scene)
        scene = example_scene()
        scene["frame"]["width"] = 480.5
        with self.assertRaises(foundry.SceneError):
            foundry.validate_scene(scene)

    def test_rejects_invalid_ids_unknown_materials_and_scene_limits(self):
        scene = example_scene()
        scene["parts"][0]["id"] = "bad id"
        with self.assertRaises(foundry.SceneError):
            foundry.validate_scene(scene)
        scene = example_scene()
        scene["parts"][0]["material"] = "missing"
        with self.assertRaises(foundry.SceneError):
            foundry.validate_scene(scene)
        scene = example_scene()
        scene["parts"] = [copy.deepcopy(scene["parts"][0]) for _ in range(foundry.MAX_PARTS + 1)]
        for index, part in enumerate(scene["parts"]):
            part["id"] = f"part-{index}"
        with self.assertRaises(foundry.SceneError):
            foundry.validate_scene(scene)
        scene = example_scene()
        scene["materials"] = {f"mat-{index}": copy.deepcopy(scene["materials"]["enamel"]) for index in range(foundry.MAX_MATERIALS + 1)}
        with self.assertRaises(foundry.SceneError):
            foundry.validate_scene(scene)

    def test_rejects_duplicate_json_keys_and_non_finite_json(self):
        with self.assertRaises(foundry.SceneError):
            json.loads('{"version":1,"version":1}', object_pairs_hook=foundry._pairs_no_duplicates)
        with self.assertRaises(foundry.SceneError):
            json.loads('{"x":NaN}', parse_constant=foundry._parse_constant)

    def test_rejects_deeply_nested_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested.json"
            path.write_text("[" * 1200 + "0" + "]" * 1200, encoding="utf-8")
            with self.assertRaises(foundry.SceneError):
                foundry.load_scene(path)

    def test_projection_origin_and_up_axis(self):
        x0, y0 = foundry.project((0, 0, 0), 45, 35.264)
        x1, y1 = foundry.project((0, 0, 1), 45, 35.264)
        self.assertAlmostEqual(x0, 0)
        self.assertAlmostEqual(y0, 0)
        self.assertAlmostEqual(x1, 0)
        self.assertLess(y1, y0)

    def test_camera_selects_facing_sides_and_frame_fits_margin(self):
        corners = {"x0": -1, "x1": 1, "y0": -2, "y1": 2, "z0": -3, "z1": 3}
        self.assertEqual([name for name, _ in foundry._faces(corners, 45)], ["x_face", "y_face", "top"])
        reversed_faces = foundry._faces(corners, 225)
        self.assertEqual(reversed_faces[0][1][0][0], corners["x0"])
        self.assertEqual(reversed_faces[1][1][0][1], corners["y0"])
        points = [(-10, -20), (10, 20)]
        result = foundry._svg_points(points, (-10, -20, 10, 20), {"width": 480, "height": 360, "margin": 40})
        coordinates = [tuple(map(float, pair.split(","))) for pair in result.split()]
        for x, y in coordinates:
            self.assertGreaterEqual(x, 40)
            self.assertGreaterEqual(y, 40)
            self.assertLessEqual(x, 440)
            self.assertLessEqual(y, 320)

    def test_output_filename_is_confined_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = Path.cwd()
            os.chdir(directory)
            try:
                target = Path("figure.html")
                target.write_text("keep", encoding="utf-8")
                with self.assertRaises(foundry.SceneError):
                    foundry.write_output("replacement", "figure.html")
                self.assertEqual(target.read_text(encoding="utf-8"), "keep")
                for unsafe in ("../figure.html", "/tmp/figure.html", "UPPER.html", "fig.html/other"):
                    with self.assertRaises(foundry.SceneError):
                        foundry.write_output("x", unsafe)
            finally:
                os.chdir(previous)

    def test_rejects_xml_disallowed_text_in_title_description_and_label(self):
        cases = (("title", "\x00"), ("description", "\x01"), ("label", "\uffff"), ("title", "\ufffe"), ("label", "\ud800"))
        for field, character in cases:
            with self.subTest(field=field, codepoint=ord(character)):
                scene = example_scene()
                if field == "label":
                    scene["parts"][0]["label"] = f"lamp {character}"
                else:
                    scene[field] = f"scene {character} text"
                with self.assertRaises(foundry.SceneError):
                    foundry.build_html(scene)

    def test_accepts_xml_valid_character_boundaries(self):
        boundary_text = "start\t\n\r " + "".join(chr(codepoint) for codepoint in (0x20, 0xD7FF, 0xE000, 0xFFFD, 0x10000, 0x10FFFF)) + " end"
        scene = example_scene()
        scene["title"] = boundary_text
        scene["description"] = boundary_text
        scene["parts"][0]["label"] = boundary_text
        validated = foundry.validate_scene(scene)
        self.assertTrue(validated["title"].startswith("start\t\n\r"))
        self.assertIn(chr(0x10FFFF), validated["description"])
        self.assertIn(chr(0xD7FF), validated["parts"][0]["label"])

    def test_invalid_xml_text_fails_before_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scene = example_scene()
            scene["description"] = "bad\x00text"
            scene_path = root / "scene.json"
            scene_path.write_text(json.dumps(scene), encoding="utf-8")
            previous = Path.cwd()
            os.chdir(root)
            try:
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(foundry.main([str(scene_path), "figure.html"]), 2)
                self.assertFalse((root / "figure.html").exists())
            finally:
                os.chdir(previous)


class HtmlOutputTests(unittest.TestCase):
    def test_html_is_static_escaped_accessible_and_deterministic(self):
        scene = example_scene()
        scene["title"] = "<script>alert(1)</script>"
        scene["parts"][0]["label"] = "<img src=x onerror=alert(1)>"
        first = foundry.build_html(scene)
        second = foundry.build_html(scene)
        self.assertEqual(first, second)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", first)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", first)
        self.assertNotIn('<script>alert(1)</script>', first)
        self.assertIn("aria-pressed=\"false\"", first)
        self.assertIn("id=\"reset-scene\"", first)
        self.assertIn("prefers-reduced-motion: reduce", first)
        self.assertIn("matchMedia('(prefers-reduced-motion: reduce)')", first)
        self.assertNotRegex(first, r"(?:src|href)=['\"]https?://")
        svg_text = re.search(r"(<svg\b.*?</svg>)", first, re.DOTALL).group(1)
        svg = ET.fromstring(svg_text)
        ns = {"svg": "http://www.w3.org/2000/svg"}
        self.assertEqual(len(svg.findall(".//svg:polygon", ns)), 12)
        self.assertEqual(len(svg.findall(".//svg:g[@role='button']", ns)), 2)

    def test_cli_round_trip_writes_a_new_offline_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scene_path = root / "scene.json"
            scene_path.write_text(json.dumps(example_scene()), encoding="utf-8")
            previous = Path.cwd()
            os.chdir(root)
            try:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(foundry.main([str(scene_path), "relay.html"]), 0)
                created = root / "relay.html"
                self.assertTrue(created.is_file())
                self.assertEqual(output.getvalue().strip(), str(created))
                content = created.read_text(encoding="utf-8")
                svg_text = re.search(r"(<svg\b.*?</svg>)", content, re.DOTALL).group(1)
                ET.fromstring(svg_text)
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(foundry.main([str(scene_path), "relay-copy.html"]), 0)
                self.assertEqual((root / "relay-copy.html").read_text(encoding="utf-8"), content)
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(foundry.main([str(scene_path), "relay.html"]), 2)
                self.assertEqual(created.read_text(encoding="utf-8"), content)
            finally:
                os.chdir(previous)

    def test_cli_refuses_oversized_input_without_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scene_path = root / "huge.json"
            scene_path.write_text(" " * (foundry.MAX_INPUT_BYTES + 1), encoding="utf-8")
            previous = Path.cwd()
            os.chdir(root)
            try:
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(foundry.main([str(scene_path), "figure.html"]), 2)
                self.assertFalse(Path("figure.html").exists())
            finally:
                os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
