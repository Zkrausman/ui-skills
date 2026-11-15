# Source contribution and review

Keep reusable skill source in `skills/<stable-package-name>/` and register it in `catalog.json`. Preserve existing paths and repository identity. Showcase application source has a separate source owner and frozen handoff; its deployment is a separate operation.

Before importing a package, identify its actual source owner, exact source revision or artifact identity, license notices and private-content boundary. Preserve original notices and record local adaptations without claiming byte-identical migration when only a text handoff exists. Do not infer an original package license from a third-party notice.

Use a scoped branch and independently reviewed draft PR. Run checks appropriate to the changed source and retain the exact reviewed head. State unrun checks and dependency limits explicitly. Merge through normal repository checks without force push, auto-merge or administrative bypass. Existing held work keeps its own approval gate.

Source storage does not authorize runtime activation, installing dependencies, operating external tools or publishing generated artifacts. Preserve installed copies unless a specific task authorizes an update. Keep credentials, personal policy/history, private notes, runtime caches and unreviewed drafts out of reusable source imports.

For documentation/catalog changes run `python3 tests/check_catalog.py`. Package-specific checks remain scoped to their package; do not run imported skill code merely to prove catalog membership.
