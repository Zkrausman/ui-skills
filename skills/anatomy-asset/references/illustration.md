# Illustration guidance

Adapted for the reduced SVG-only fork from the pinned Anatomy Asset guidance; see the license and provenance record.

Start with placement, intended message, background color, and shown size. For software, choose a physical metaphor whose construction supports the message: a sorting cabinet for triage, a measuring instrument for precision, a tray of organized tools for focus. If the user has named the object, follow that choice. One distinct focal moment is enough: a drawer open, a tool resting on a mount, a removable cap exposing its fitting. A static asset does not need to imitate a working interactive application.

Fit the object to an art region, leaving deliberate clear space for neighboring text. A 640 × 480 feature tile can use a 32-unit margin; an 800 × 600 art-only illustration can begin with 24 units. These are starting points, not guaranteed layouts. Feed all extreme points into `fitInto`, including the top of lifted parts and the ends of round components. Shadows also consume space. Keep one camera and similar world scale across a set.

Use solids with opaque fills so nearer parts cover farther parts. Let the kit generate side shading and tops. Place every screw, wire end, foot, seam, and knob on a real mount or edge. Repeated details should explain construction rather than decorate empty space. At small display sizes, reduce tiny detail and keep the silhouette legible. The kit's non-scaling strokes allow consistent line weight; choose `weight` for the intended shown size.

Ground the neutral ramp in the page color, then place an accent on the focal component. Use `assetSvg({paper, accents: {brand: "#d98338"}})` and wrap trusted parts in `<g class="ac-brand">`. Accent ramps preserve the shaded volume. The exporter accepts only three- or six-digit hex colors and named accent tokens. It inlines the required CSS, so no web fonts or network resources are needed.

Painter order is authored. Sort comparable repeated parts with `depthOf`, split components that wrap around one another, and inspect junctions carefully. Round parts use a world-space axis frame; pipes are tessellated geometry, not thick flat screen lines. This reduced package does not include the upstream geometry-audit subsystem, so do not claim collision proof. XML validity and finite-coordinate checks are useful but cannot substitute for a visual render when one is later authorized and supported.
