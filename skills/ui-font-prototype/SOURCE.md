# Source and scope

This skill adapts an owner-supplied original font-prototype instruction and structural checker. The starter geometry is extracted from its original generation source: manually authored centerlines for printable ASCII. No existing font is loaded or renamed. Rounded and angular constructions share the same skeleton and are not separate mature type families.

The toolkit includes only generic instructions, reusable source and source licensing. Personal font binaries, specimens, manifests and the original archive are excluded. The supplied existing-font fitting guide was evaluated as a workflow comparison only; none of its code, instructions or font outlines are imported.

Local adaptations add fresh-output CLI boundaries, a reusable generator and SVG preview, explicit dependency checks, per-font error reporting and no-font-input failure. The source code is MIT licensed. Generated fonts have no automatically selected license; the owner must choose distribution terms before publication.

Validation distinguishes pure geometry and filesystem behavior from binary, visual and production qualification. FontTools is optional for the geometry preview but required for generating and structurally checking TTFs. Missing FontTools must be reported as unrun binary checks. No dependencies are installed by the skill or its CI.
