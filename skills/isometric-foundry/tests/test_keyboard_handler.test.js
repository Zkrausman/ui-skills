const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const helperPath = path.join(__dirname, "..", "scripts", "keyboard-handler.js");
const source = fs.readFileSync(helperPath, "utf8");
const isolated = {};
vm.runInNewContext(`${source}\nthis.handler = handlePartKeydown;`, isolated);

for (const key of ["Enter", " "]) {
  test(`${JSON.stringify(key)} activates the shared part toggle`, () => {
    const part = { label: "relay" };
    let prevented = false;
    let toggled = null;
    const event = { key, preventDefault: () => { prevented = true; } };
    const result = isolated.handler(event, part, (value) => { toggled = value; });
    assert.equal(result, true);
    assert.equal(prevented, true);
    assert.equal(toggled, part);
  });
}

test("other keys and missing parts do not activate", () => {
  let prevented = false;
  let toggles = 0;
  const event = { key: "Escape", preventDefault: () => { prevented = true; } };
  assert.equal(isolated.handler(event, { label: "relay" }, () => { toggles += 1; }), false);
  assert.equal(isolated.handler({ key: "Enter", preventDefault: () => { prevented = true; } }, null, () => { toggles += 1; }), false);
  assert.equal(prevented, false);
  assert.equal(toggles, 0);
});
