# Verification plan for the rebuild

These checks are new for this implementation. No historical test gates or results are being reused. Run them after the source review:

1. **Skill shape:** run the local skill `quick_validate.py` against this folder; confirm frontmatter name, description, references, and no starter placeholders.
2. **Syntax:** run `python3 -m py_compile scripts/foundry.py tests/test_foundry.py`.
3. **Unit tests:** run `python3 -m unittest discover -s tests -v` for projection coordinates, frame fitting, face selection, deterministic markup, and HTML/SVG escaping.
4. **CLI round trip:** build a fresh HTML file from a small authored scene fixture; parse its SVG with Python's XML parser; verify expected part count, accessible controls, no remote `src`/stylesheet/script URLs, and byte-identical output for the same input.
5. **Negative security cases:** reject duplicate JSON keys, unknown fields, oversized documents, non-finite or out-of-range numbers, malformed colors/IDs, excessive parts/materials, path traversal/absolute output names, and output collisions. Confirm failed builds do not create or alter a destination file.
6. **Consumer check:** after the skill itself is reviewed, have a separate consumer use it for one inventive, technically coherent object and inspect the generated HTML as data. A browser run remains outside this plan while the existing browser hold is active; report that static checks do not establish rendered browser behavior.
