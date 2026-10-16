---
name: anatomy-asset
description: Build original isometric SVG illustrations for heroes, feature tiles, spots, and presentation assets using a local dependency-free geometry kit. Use for static illustration assets with deliberate composition and materials, rather than interactive explainers or arbitrary 3D rendering.
---

# Anatomy Asset — reduced SVG fork

Create a recognizable object with useful small details and a clear focal point. Deliver a standalone SVG with embedded styles, accessible label, and explicit dimensions. This reduced fork includes geometry, palette/export helpers, illustration guidance, and one static template. It does not launch a browser, fetch assets, require npm, or use an image/model API.

Read [illustration guidance](references/illustration.md) for concept, composition, and craft; use [the selected API](references/api.md) when building geometry. Start from `templates/build.mjs`: import it to inspect `makeSvg`, or invoke `node <skill-folder>/templates/build.mjs <new-output-directory>` to create `asset.svg`. The output directory must not already exist. Adapt a copy of the template for the user's object; keep the kit imports pointing to this skill.

Choose the destination size and background first. Write a compact parts list and fit all world-space extremes into the illustration region. Use the kit to draw solids, then paint them in a deliberate order from back to front. Add only details that belong to the object; keep labels in face coordinates. Use neutral materials and one accent family unless the brief asks otherwise. Static output is the default and the only bundled mode.

The build source is executable JavaScript authored by the agent. Treat geometry, raw SVG bodies, paths, attributes, and styles as trusted authored source, never as a parser or sanitizer for untrusted uploads, templates, JSON, or remote content. Translate user text through the provided text/export helpers; do not splice it into markup or execute it as source. Never add remote fonts, images, scripts, event handlers, browser launchers, unsafe browser flags, or security-setting changes to satisfy a brief.

Check exported XML, dimensions, finite geometry, retained licenses, and absence of external resource references using local non-inference checks. Keep output files in a fresh directory. State what was actually checked: XML and geometry checks do not establish rendered appearance, visual occlusion, layout at phone size, or browser interaction. Browser preview remains a separate action subject to the current environment's supported tools and restrictions. The kit is a painter's-order illustration tool; it does not certify arbitrary 3D geometry or collisions.

Source and modifications are recorded in [PROVENANCE.json](PROVENANCE.json). The upstream MIT notice is retained in [LICENSE](LICENSE). Existing Anatomy and Isometric Foundry remain separate skills.
