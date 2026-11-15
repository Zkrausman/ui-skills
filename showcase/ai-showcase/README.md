# AI Skills Showcase source

Reusable static showcase source. Serve `dist/` with an existing local static-file server, for example `python3 -m http.server --directory dist 8000`, then open its local address. This package has no deployment project binding and does not deploy or alter sharing. Keep any deployment configuration outside this source import and follow its owner’s authorization.

## Included examples

- Colorfigures toaster: bundled example packaged by its Python builder.
- Anatomy dial indicator: bundled example with its module externalized to `anatomy-runtime.js` to repair script embedding.
- Isometric Foundry switchboard: generator output from `dist/demos/foundry-scene.json`.
- Typography: interactive specimen of ten OFL-licensed geometric display prototypes. The original generated-font demonstration is excluded because distribution terms were not selected. The replacement is not claimed as output of the font-generation skill.
- JSON Canvas: editable three-node example download. It is a portable board, not an embedded editor.

Figure/tool sources are vendored from the frozen handoff and based on toolkit commit `76d1fd55f76577f64b807f150eb7632493ff7941`. All fifteen vendored text files in that handoff have one additional terminal newline compared with that toolkit commit; this import preserves the handed-off bytes. See `PROVENANCE.json` for source identities, hashes, exclusions and adaptations. Canonical skill source remains under the repository’s `skills/` directory; the vendor directory is a showcase snapshot, not another activation source.

## Licensing and limits

The unmodified ZK font binaries explicitly declare SIL OFL 1.1 in their name metadata; the matching copyright and full license are retained in `dist/OFL.txt`. These related Regular-only display prototypes cover printable ASCII and retain overlap/spacing limitations. Do not describe them as qualified production prose families. The duplicate `meridian.ttf` is retained unchanged from the handoff.

MIT source notices for Anatomy, Colorfigures and the font tooling are preserved; Foundry’s third-party notice remains intact without assigning a new license to its original implementation. No blanket package license overrides component terms.

The shell supports demo tabs, a session-only light/dark toggle and editable font comparison. Examples retain their own controls and appearance. Historical checks of the earlier source do not establish browser or mobile validation of this sanitized version. Run the repository’s showcase checks for static assets, script syntax, interaction contracts and privacy boundaries; report browser/mobile rendering separately.
