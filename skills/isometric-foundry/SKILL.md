---
name: isometric-foundry
description: Create original isometric object explainers as accessible, self-contained offline HTML with editable style, lighting, projection, framing, and simple interactions. Use for custom isometric scenes, product-like figures, or interactive visual explanations; not for arbitrary 3D modeling or online app frameworks.
metadata:
  short-description: Build offline isometric explainers
---

# Isometric Foundry

Build one clear object whose form or interaction helps explain the user's idea. Deliver a standalone HTML file that works from disk. This is a new implementation from the recorded brief; no historical scene schema, formula, preset, or source code was available to recover.

## Workflow

1. Identify the idea, the object that can embody it, and one useful action the viewer can perform. Use grounded values supplied by the user; mark invented values as illustrative.
2. Choose a small, legible assembly of rectangular parts. Plan their centers, dimensions, materials, light states, and back-to-front order in a JSON scene following [the scene format](references/scene-format.md).
3. Customize the palette, face colors, glow, projection angles, and framing to suit the subject. The exporter fixes stroke width, glow blur, and pulse cadence. Keep the drawing recognizable at phone width and avoid logos or copied product designs.
4. Use `python3 scripts/foundry.py <scene.json> <figure.html>` to validate the declarative scene and write a single HTML file in the current directory. Choose a new lowercase filename; the tool refuses overwrites. It accepts only bounded JSON and its documented fields; it never evaluates scene text or accepts raw SVG, CSS, or JavaScript.
5. Make interactions understandable and reversible. Keep each interactive part keyboard-operable with a visible focus ring. Include the global light toggle, reset, and pause/resume controls. Start motion paused when the system requests reduced motion.
6. Describe what the viewer can change and any important geometry limits. Do not imply arbitrary 3D, automatic hidden-surface resolution, or browser verification that was not performed.

Use the bundled format as a compact implementation aid, not as a creative limit on the object. Keep scene-specific content original. The generated page must work offline: no remote fonts, libraries, images, requests, analytics, or package installs.
