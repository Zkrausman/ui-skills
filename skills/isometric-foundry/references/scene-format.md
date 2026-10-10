# Scene format v1

This format is a new, deliberately small design choice for the rebuilt skill. It describes boxes in world coordinates and lets the bundled Python standard-library script project them into SVG. It is not the missing historical schema.

## Document

```json
{
  "version": 1,
  "title": "Night-shift switchboard",
  "description": "Three relays route power to a row of lamps.",
  "frame": {"width": 960, "height": 640, "margin": 40},
  "projection": {"azimuth": 45, "elevation": 35.264},
  "palette": {"background": "#11151b", "ink": "#eef2f7"},
  "materials": {
    "enamel": {
      "top": "#56667a",
      "x_face": "#344457",
      "y_face": "#40536a",
      "outline": "#c3cfdd",
      "glow": "#ffc765"
    }
  },
  "parts": [
    {
      "id": "relay-a",
      "label": "Relay A",
      "center": [0, 0, 0],
      "size": [120, 72, 28],
      "material": "enamel",
      "interactive": true,
      "lit": false
    }
  ]
}
```

`frame.width` is 480–1600, `frame.height` is 360–1200, and `frame.margin` is 16–128 SVG units. `projection.azimuth` is degrees in `[0, 360)`; `elevation` is degrees in `[15, 75]`. These bounds keep the projection away from degenerate views. All coordinates are finite and between −1000 and 1000; box dimensions are positive and at most 500. A scene has 1–60 parts and 1–16 materials. IDs are unique lowercase kebab-case tokens. Text is plain text, limited to 120 characters for the title, 300 for the description, and 80 for each part label. Colors are six-digit hexadecimal values. Unknown fields are rejected.

## Rebuilt projection and drawing rules

For a point `(x, y, z)`, azimuth `a`, and elevation `e` (converted to radians), the camera basis is:

```text
screen_x =  cos(a) * x - sin(a) * y
screen_y =  sin(e) * (sin(a) * x + cos(a) * y) - cos(e) * z
```

The exporter projects the eight corners of every box, computes their combined bounds, and scales/translates the result into the requested frame margin. It draws the camera-facing x and y sides, then the top. Parts appear in the JSON array order; author that order from back to front. The tool does not infer occlusion between overlapping boxes, bevels, curves, arbitrary SVG, or 3D rotations. Split a complex object into simple boxes and use restrained overlap.

`palette.background` and `palette.ink` set the page; each material supplies `top`, `x_face`, `y_face`, `outline`, and `glow`. Replacing these six-digit colors is the supported style and light customization. Stroke width (1.25 SVG units), glow blur (5 units), and pulse cadence (2.8 seconds) are fixed. A part with `lit: true` begins glowing. Interactive parts can be toggled individually; page controls toggle all lights, restore the initial scene, and pause or resume the glow pulse. Reduced-motion preference starts the pulse paused. The SVG itself remains static and readable without animation.

## Safe export

The generator accepts only this JSON document; it does not evaluate expressions or embed scene data in JavaScript. Text is checked for XML 1.0 characters and escaped for HTML/SVG; IDs and colors are constrained, and the output script is fixed in the bundled helper files. The output filename must be a plain `.html` filename in the current directory. Creation uses exclusive mode and refuses to overwrite an existing file. Keep user data in the supported fields; never add event attributes, raw HTML, CSS, URLs, or script strings to the format.
