#!/usr/bin/env python3
"""Build a bounded, offline SVG figure from an Isometric Foundry scene JSON file."""

from __future__ import annotations

import html
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


MAX_INPUT_BYTES = 128 * 1024
MAX_PARTS = 60
MAX_MATERIALS = 16
COLOR = re.compile(r"#[0-9a-fA-F]{6}\Z")
TOKEN = re.compile(r"[a-z0-9][a-z0-9-]{0,31}\Z")
OUTPUT_NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\.html\Z")


class SceneError(ValueError):
    """A scene does not conform to the supported document format."""


def _object(value: Any, where: str, required: set[str], optional: set[str] | frozenset[str] = frozenset()) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SceneError(f"{where} must be an object")
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing:
        raise SceneError(f"{where} is missing: {', '.join(sorted(missing))}")
    if unknown:
        raise SceneError(f"{where} has unsupported fields: {', '.join(sorted(unknown))}")
    return value


def _text(value: Any, where: str, limit: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise SceneError(f"{where} must be non-empty text up to {limit} characters")
    value = value.strip()
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise SceneError(f"{where} must be valid UTF-8 text") from None
    return value


def _number(value: Any, where: str, low: float, high: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SceneError(f"{where} must be a finite number")
    try:
        number = float(value)
    except (OverflowError, ValueError):
        raise SceneError(f"{where} must be a finite number") from None
    if not math.isfinite(number):
        raise SceneError(f"{where} must be a finite number")
    if number < low or number > high:
        raise SceneError(f"{where} must be between {low:g} and {high:g}")
    return number


def _integer(value: Any, where: str, low: int, high: int) -> int:
    if type(value) is not int or value < low or value > high:
        raise SceneError(f"{where} must be an integer between {low} and {high}")
    return value


def _color(value: Any, where: str) -> str:
    if not isinstance(value, str) or not COLOR.fullmatch(value):
        raise SceneError(f"{where} must be a six-digit hexadecimal color")
    return value.lower()


def _vector(value: Any, where: str, low: float, high: float) -> list[float]:
    if not isinstance(value, list) or len(value) != 3:
        raise SceneError(f"{where} must contain three numbers")
    return [_number(item, f"{where}[{index}]", low, high) for index, item in enumerate(value)]


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SceneError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_constant(value: str) -> None:
    raise SceneError(f"non-finite JSON number is forbidden: {value}")


def load_scene(path: Path) -> dict[str, Any]:
    try:
        if not path.is_file():
            raise SceneError("scene input must be a regular file")
        with path.open("rb") as input_file:
            raw = input_file.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise SceneError(f"scene exceeds {MAX_INPUT_BYTES} bytes")
        source = raw.decode("utf-8")
        scene = json.loads(source, object_pairs_hook=_pairs_no_duplicates, parse_constant=_parse_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SceneError(f"cannot read scene: {error}") from error
    except RecursionError as error:
        raise SceneError("scene JSON is nested too deeply") from error
    return validate_scene(scene)


def validate_scene(scene: Any) -> dict[str, Any]:
    root = _object(scene, "scene", {"version", "title", "description", "frame", "projection", "palette", "materials", "parts"})
    if type(root["version"]) is not int or root["version"] != 1:
        raise SceneError("version must be the integer 1")
    normalized: dict[str, Any] = {
        "version": 1,
        "title": _text(root["title"], "title", 120),
        "description": _text(root["description"], "description", 300),
    }
    frame = _object(root["frame"], "frame", {"width", "height", "margin"})
    normalized["frame"] = {
        "width": _integer(frame["width"], "frame.width", 480, 1600),
        "height": _integer(frame["height"], "frame.height", 360, 1200),
        "margin": _integer(frame["margin"], "frame.margin", 16, 128),
    }
    if normalized["frame"]["margin"] * 2 >= min(normalized["frame"]["width"], normalized["frame"]["height"]):
        raise SceneError("frame.margin leaves no drawable area")
    projection = _object(root["projection"], "projection", {"azimuth", "elevation"})
    normalized["projection"] = {
        "azimuth": _number(projection["azimuth"], "projection.azimuth", 0, 359.999999),
        "elevation": _number(projection["elevation"], "projection.elevation", 15, 75),
    }
    palette = _object(root["palette"], "palette", {"background", "ink"})
    normalized["palette"] = {key: _color(palette[key], f"palette.{key}") for key in ("background", "ink")}
    materials = root["materials"]
    if not isinstance(materials, dict) or not 1 <= len(materials) <= MAX_MATERIALS:
        raise SceneError(f"materials must contain 1 to {MAX_MATERIALS} entries")
    normalized_materials: dict[str, dict[str, str]] = {}
    for key, material in materials.items():
        if not isinstance(key, str) or not TOKEN.fullmatch(key):
            raise SceneError("material names must be lowercase kebab-case tokens")
        material = _object(material, f"materials.{key}", {"top", "x_face", "y_face", "outline", "glow"})
        normalized_materials[key] = {face: _color(material[face], f"materials.{key}.{face}") for face in ("top", "x_face", "y_face", "outline", "glow")}
    normalized["materials"] = normalized_materials
    parts = root["parts"]
    if not isinstance(parts, list) or not 1 <= len(parts) <= MAX_PARTS:
        raise SceneError(f"parts must contain 1 to {MAX_PARTS} boxes")
    normalized_parts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, part in enumerate(parts):
        where = f"parts[{index}]"
        part = _object(part, where, {"id", "label", "center", "size", "material", "interactive", "lit"})
        part_id = part["id"]
        if not isinstance(part_id, str) or not TOKEN.fullmatch(part_id) or part_id in seen:
            raise SceneError(f"{where}.id must be a unique lowercase kebab-case token")
        seen.add(part_id)
        material = part["material"]
        if not isinstance(material, str) or material not in normalized_materials:
            raise SceneError(f"{where}.material must name a declared material")
        if type(part["interactive"]) is not bool or type(part["lit"]) is not bool:
            raise SceneError(f"{where}.interactive and {where}.lit must be booleans")
        normalized_parts.append({
            "id": part_id,
            "label": _text(part["label"], f"{where}.label", 80),
            "center": _vector(part["center"], f"{where}.center", -1000, 1000),
            "size": _vector(part["size"], f"{where}.size", 0.01, 500),
            "material": material,
            "interactive": part["interactive"],
            "lit": part["lit"],
        })
    normalized["parts"] = normalized_parts
    return normalized


def project(point: tuple[float, float, float], azimuth: float, elevation: float) -> tuple[float, float]:
    x, y, z = point
    a, e = math.radians(azimuth), math.radians(elevation)
    screen_x = math.cos(a) * x - math.sin(a) * y
    screen_y = math.sin(e) * (math.sin(a) * x + math.cos(a) * y) - math.cos(e) * z
    return screen_x, screen_y


def _part_corners(part: dict[str, Any]) -> dict[str, float]:
    x, y, z = part["center"]
    w, d, h = part["size"]
    return {"x0": x - w / 2, "x1": x + w / 2, "y0": y - d / 2, "y1": y + d / 2, "z0": z - h / 2, "z1": z + h / 2}


def _faces(c: dict[str, float], azimuth: float) -> list[tuple[str, list[tuple[float, float, float]]]]:
    x_face = c["x1"] if math.sin(math.radians(azimuth)) >= 0 else c["x0"]
    y_face = c["y1"] if math.cos(math.radians(azimuth)) >= 0 else c["y0"]
    return [
        ("x_face", [(x_face, c["y0"], c["z0"]), (x_face, c["y1"], c["z0"]), (x_face, c["y1"], c["z1"]), (x_face, c["y0"], c["z1"])]),
        ("y_face", [(c["x0"], y_face, c["z0"]), (c["x1"], y_face, c["z0"]), (c["x1"], y_face, c["z1"]), (c["x0"], y_face, c["z1"])]),
        ("top", [(c["x0"], c["y0"], c["z1"]), (c["x1"], c["y0"], c["z1"]), (c["x1"], c["y1"], c["z1"]), (c["x0"], c["y1"], c["z1"])]),
    ]


def _projected_parts(scene: dict[str, Any]) -> tuple[list[list[tuple[str, list[tuple[float, float]]]]], tuple[float, float, float, float]]:
    azimuth = scene["projection"]["azimuth"]
    elevation = scene["projection"]["elevation"]
    projected: list[list[tuple[str, list[tuple[float, float]]]]] = []
    all_points: list[tuple[float, float]] = []
    for part in scene["parts"]:
        corners = _part_corners(part)
        all_points.extend(
            project((x, y, z), azimuth, elevation)
            for x in (corners["x0"], corners["x1"])
            for y in (corners["y0"], corners["y1"])
            for z in (corners["z0"], corners["z1"])
        )
        faces = []
        for name, points in _faces(corners, azimuth):
            face_points = [project(point, azimuth, elevation) for point in points]
            faces.append((name, face_points))
        projected.append(faces)
    xs, ys = [point[0] for point in all_points], [point[1] for point in all_points]
    return projected, (min(xs), min(ys), max(xs), max(ys))


def _svg_points(points: list[tuple[float, float]], bounds: tuple[float, float, float, float], frame: dict[str, int]) -> str:
    min_x, min_y, max_x, max_y = bounds
    scale = min((frame["width"] - 2 * frame["margin"]) / (max_x - min_x), (frame["height"] - 2 * frame["margin"]) / (max_y - min_y))
    offset_x = (frame["width"] - (max_x - min_x) * scale) / 2 - min_x * scale
    offset_y = (frame["height"] - (max_y - min_y) * scale) / 2 - min_y * scale
    return " ".join(f"{x * scale + offset_x:.2f},{y * scale + offset_y:.2f}" for x, y in points)


def build_html(scene: Any) -> str:
    scene = validate_scene(scene)
    faces_by_part, bounds = _projected_parts(scene)
    frame = scene["frame"]
    svg_parts: list[str] = []
    for part, faces in zip(scene["parts"], faces_by_part):
        material = scene["materials"][part["material"]]
        classes = "part is-lit" if part["lit"] else "part"
        role = "button" if part["interactive"] else "group"
        tabindex = ' tabindex="0"' if part["interactive"] else ""
        pressed = f' aria-pressed="{str(part["lit"]).lower()}"' if part["interactive"] else ""
        label = html.escape(part["label"], quote=True)
        svg_parts.append(f'<g class="{classes}" data-part="{part["id"]}" data-initial-lit="{str(part["lit"]).lower()}" role="{role}" aria-label="{label}"{tabindex}{pressed}>')
        svg_parts.append(f"<title>{label}</title>")
        for face, points in faces:
            point_text = _svg_points(points, bounds, frame)
            fill = material[face]
            outline = material["outline"]
            svg_parts.append(f'<polygon class="face" points="{point_text}" fill="{fill}" stroke="{outline}"/>')
            svg_parts.append(f'<polygon class="glow" points="{point_text}" fill="{material["glow"]}" aria-hidden="true"/>')
        svg_parts.append("</g>")
    title = html.escape(scene["title"], quote=True)
    description = html.escape(scene["description"], quote=True)
    palette = scene["palette"]
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Isometric Foundry</title>
<style>
:root {{ color-scheme: dark; --paper: {palette["background"]}; --ink: {palette["ink"]}; --muted: color-mix(in srgb, var(--ink) 68%, var(--paper)); --line: color-mix(in srgb, var(--ink) 22%, transparent); --glow: 0.45; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; min-height: 100vh; background: var(--paper); color: var(--ink); font: 16px/1.5 system-ui, sans-serif; }}
main {{ width: min(100%, 1040px); margin: 0 auto; padding: clamp(1rem, 4vw, 2.5rem); }}
h1 {{ margin: 0; font-size: clamp(1.35rem, 4vw, 2.2rem); line-height: 1.15; }}
.description {{ max-width: 68ch; color: var(--muted); }}
.scene {{ width: 100%; height: auto; display: block; overflow: visible; }}
.face {{ stroke-width: 1.25; stroke-linejoin: round; vector-effect: non-scaling-stroke; }}
.glow {{ opacity: 0; filter: blur(5px); pointer-events: none; transition: opacity 180ms ease; }}
.part.is-lit .glow {{ opacity: var(--glow); animation: pulse 2.8s ease-in-out infinite alternate; }}
.part[role="button"] {{ cursor: pointer; outline: none; }}
.part[role="button"]:focus-visible .face {{ stroke: var(--ink); stroke-width: 3; }}
@keyframes pulse {{ from {{ opacity: .24; }} to {{ opacity: var(--glow); }} }}
.controls {{ display: flex; flex-wrap: wrap; gap: .65rem; margin-block: 1rem; }}
button {{ min-height: 2.75rem; border: 1px solid var(--line); border-radius: .45rem; padding: .55rem .9rem; background: transparent; color: var(--ink); font: inherit; cursor: pointer; }}
button:focus-visible {{ outline: 3px solid var(--ink); outline-offset: 3px; }}
.status {{ min-height: 1.5em; color: var(--muted); }}
.motion-paused .glow {{ animation: none !important; }}
@media (prefers-reduced-motion: reduce) {{ :root:not(.motion-opt-in) *, :root:not(.motion-opt-in) *::before, :root:not(.motion-opt-in) *::after {{ animation-duration: .01ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; transition-duration: .01ms !important; }} }}
</style>
</head>
<body>
<main>
<h1>{title}</h1>
<p class="description">{description}</p>
<div class="controls" aria-label="Figure controls">
  <button type="button" id="toggle-lights" aria-pressed="false">Turn lights on</button>
  <button type="button" id="reset-scene">Reset</button>
  <button type="button" id="toggle-motion" aria-pressed="false">Resume motion</button>
</div>
<p id="status" class="status" aria-live="polite">Use the controls or focus a marked part.</p>
<svg class="scene" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {frame["width"]} {frame["height"]}" role="group" aria-label="Interactive isometric figure: {title}">
  <title>{title}</title>
  <desc>{description}</desc>
  {''.join(svg_parts)}
</svg>
</main>
<script>
(() => {{
  const root = document.documentElement;
  const parts = [...document.querySelectorAll('[data-part]')];
  const lights = document.getElementById('toggle-lights');
  const reset = document.getElementById('reset-scene');
  const motion = document.getElementById('toggle-motion');
  const status = document.getElementById('status');
  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  let motionOn = !preference.matches;
  const setLit = (part, on) => {{
    part.classList.toggle('is-lit', on);
    if (part.getAttribute('role') === 'button') part.setAttribute('aria-pressed', String(on));
  }};
  const syncLights = () => {{
    const allLit = parts.length > 0 && parts.every((part) => part.classList.contains('is-lit'));
    lights.setAttribute('aria-pressed', String(allLit));
    lights.textContent = allLit ? 'Turn lights off' : 'Turn lights on';
  }};
  const report = (message) => {{ status.textContent = message; }};
  const syncMotion = () => {{
    root.classList.toggle('motion-paused', !motionOn);
    root.classList.toggle('motion-opt-in', motionOn && preference.matches);
    motion.setAttribute('aria-pressed', String(motionOn));
    motion.textContent = motionOn ? 'Pause motion' : (preference.matches ? 'Enable motion' : 'Resume motion');
  }};
  const togglePart = (part) => {{
    const on = !part.classList.contains('is-lit');
    setLit(part, on);
    syncLights();
    report(part.getAttribute('aria-label') + (on ? ' on' : ' off'));
  }};
  lights.addEventListener('click', () => {{
    const turnOn = parts.some((part) => !part.classList.contains('is-lit'));
    parts.forEach((part) => setLit(part, turnOn));
    syncLights();
    report(turnOn ? 'All lights on' : 'All lights off');
  }});
  reset.addEventListener('click', () => {{
    parts.forEach((part) => setLit(part, part.dataset.initialLit === 'true'));
    syncLights();
    report('Figure reset');
  }});
  motion.addEventListener('click', () => {{ motionOn = !motionOn; syncMotion(); report(motionOn ? 'Motion resumed' : 'Motion paused'); }});
  preference.addEventListener('change', (event) => {{
    if (event.matches) motionOn = false;
    syncMotion();
  }});
  document.querySelector('.scene').addEventListener('click', (event) => {{
    const part = event.target.closest('[data-part][role="button"]');
    if (part) togglePart(part);
  }});
  document.querySelector('.scene').addEventListener('keydown', (event) => {{
    const part = event.target.closest('[data-part][role="button"]');
    if (part && (event.key === 'Enter' || event.key === ' ')) {{ event.preventDefault(); part.click(); }}
  }});
  syncLights();
  syncMotion();
}})();
</script>
</body>
</html>
'''
    return doc


def write_output(html_text: str, output_name: str) -> Path:
    if not isinstance(output_name, str) or not OUTPUT_NAME.fullmatch(output_name):
        raise SceneError("output must be a plain lowercase .html filename in the current directory")
    destination = Path.cwd() / output_name
    try:
        with destination.open("x", encoding="utf-8", newline="\n") as output:
            output.write(html_text)
    except FileExistsError as error:
        raise SceneError(f"refusing to overwrite existing file: {output_name}") from error
    except OSError as error:
        raise SceneError(f"cannot create output: {error}") from error
    return destination


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("usage: python3 scripts/foundry.py SCENE.json OUTPUT.html", file=sys.stderr)
        return 2
    try:
        scene = load_scene(Path(argv[0]))
        output = write_output(build_html(scene), argv[1])
    except (SceneError, OSError, UnicodeError) as error:
        print(f"isometric-foundry: {error}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
