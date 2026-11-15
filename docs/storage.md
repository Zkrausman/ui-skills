# Source storage, deployments and artifacts

The [catalog](../catalog.json) identifies reusable AI skill and showcase source. Keep the historical repository URL and existing `skills/*` package paths stable. There is no blanket repository license overriding package notices.

## Canonical source

| Package | Source | Provenance and licensing |
| --- | --- | --- |
| Anatomy | `skills/anatomy` | Pinned upstream import; MIT license retained |
| Isometric Foundry | `skills/isometric-foundry` | Independent rebuild; third-party MIT notice retained; original package license remains unspecified |
| Colorfigures | `skills/colorfigures` | Official ZIP pin, two documented local patches and MIT notices |
| UI Font Prototype | `skills/ui-font-prototype` | Original geometric starter and tooling; MIT source; generated-font terms chosen separately |
| JSON Canvas | `skills/json-canvas` | Supplied text adaptation and independently verified upstream MIT notice; not a complete plugin migration |
| AI Skills Showcase | `showcase/ai-showcase` | Sanitized static source and licensed examples; per-file provenance and component notices |

## Deployment copies

An installed skill is a deployment copy, not a second canonical source tree. Preserve deployed copies unless a specific update is authorized. Use an exact reviewed revision and verify the resulting files. Store host-specific deployment receipts outside public reusable source. Catalog membership does not imply installation, dependencies, browser validation or availability on every machine.

The showcase is source only. Its public source excludes project bindings and deployment access metadata; storing it does not deploy a site or change another site’s access. Configure any later deployment separately with its owner’s authorization. No skills are activated by this centralization.

## Generated artifacts

Generated fonts, specimens and diagrams belong in their separately authorized artifact destinations by default. Do not add personal archives or private output merely because its generator is stored here. The showcase includes only explicitly reviewed, distributable examples; its font license is preserved separately from source-code licenses.

Runtime-managed/internal skills, credentials, application caches, user-specific operational profiles and unreviewed drafts are outside this catalog. Additional reusable source needs verified ownership, license/provenance and a private-content review before import. Keep source changes with their owner and preserve unrelated review holds.
