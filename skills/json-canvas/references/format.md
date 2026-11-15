# JSON Canvas 1.0

Authoritative reference: https://jsoncanvas.org/spec/1.0/ (2024-03-11).
Upstream skill: https://github.com/obsidianmd/obsidian-skills/tree/main/plugins/obsidian/skills/json-canvas

Top-level optional arrays: `nodes`, `edges`. New files can include both as empty arrays.

Every node needs string `id`, `type` (`text`, `file`, `link`, `group`) and integer `x`, `y`, `width`, `height`. New nodes should use positive dimensions. Preserve array order: it is back-to-front stacking order.

Type-specific required strings: text→`text`, file→`file`, link→`url`; group has optional `label`, `background`, `backgroundStyle` (`cover`, `ratio`, `repeat`). File nodes may include `subpath`, beginning with `#`.

Every edge needs string `id`, `fromNode`, `toNode`; endpoints reference existing nodes. Optional `fromSide`/`toSide`: top/right/bottom/left. Optional `fromEnd`/`toEnd`: none/arrow. Optional string `label` and `color`.

Colors are hex strings or presets `"1"` through `"6"`; exact preset appearance depends on renderer. IDs are unique strings, not necessarily fixed-length hex.

Serialize newlines, quotes and Unicode normally. JSON validity alone does not establish schema, reference, or visual correctness. Preserve extension properties when editing.
