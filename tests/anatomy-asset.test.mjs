import test from "node:test";
import assert from "node:assert/strict";
import { iso, boxCorners, slabOf, solidSvg, faceTextSvg } from "../skills/anatomy-asset/kit/iso-kit.mjs";
import { assetSvg, fitInto, hexToRgb } from "../skills/anatomy-asset/kit/asset.mjs";
import { frameAlong, disc } from "../skills/anatomy-asset/kit/lathe.mjs";
import { tubePieces, tubeSvg } from "../skills/anatomy-asset/kit/tube.mjs";
import { xmlText } from "../skills/anatomy-asset/kit/xml.mjs";
import { makeSvg } from "../skills/anatomy-asset/templates/build.mjs";

const options = () => ({ width: 640, height: 480, label: "An instrument", body: "<g/>", id: "test-asset" });
const finiteMarkup = value => {
  assert.equal(typeof value, "string");
  assert.ok(value.length > 0);
  assert.doesNotMatch(value, /NaN|Infinity|undefined/);
};

test("projection fits all box corners inside the requested region", () => {
  const points = boxCorners({ x: 0, y: 0, w: 100, d: 80 }, 0, 60);
  const region = { x: 100, y: 20, w: 500, h: 400 };
  const P = fitInto(points, region, { pad: 30 });
  for (const point of points) {
    const [x, y] = iso(point, P);
    assert.ok(x >= 130 - 1e-8 && x <= 570 + 1e-8);
    assert.ok(y >= 50 - 1e-8 && y <= 390 + 1e-8);
  }
});

test("slab and arbitrary-axis round geometry produce finite SVG paths", () => {
  const P = { origin: [320, 300], scale: 2, azimuth: 45, elevation: 30 };
  const slab = slabOf({ x: 0, y: 0, w: 30, d: 20, r: 2 }, 0, 8, P);
  finiteMarkup(solidSvg(slab));
  const F = frameAlong([0, 0, 10], [1, 0, 0]);
  finiteMarkup(solidSvg(disc(0, 12, 5, F, P)));
});

test("tube geometry and exported pipe pieces remain finite", () => {
  const P = { origin: [320, 300], scale: 2, azimuth: 45, elevation: 30 };
  const pieces = tubePieces([[0, 0, 0], [20, 0, 0], [20, 10, 5]], 1, P);
  assert.ok(pieces.length > 0);
  for (const piece of pieces) finiteMarkup(tubeSvg(piece));
});

test("labels and face text escape markup and retain valid XML boundaries", () => {
  assert.equal(xmlText('<&"\''), "&lt;&amp;&quot;&apos;");
  assert.ok(assetSvg({ ...options(), label: '<&"' }).includes('aria-label="&lt;&amp;&quot;"'));
  assert.ok(faceTextSvg("matrix(1 0 0 1 0 0)", "<label>").includes("&lt;label&gt;"));
  const valid = "x\t\n\r " + String.fromCodePoint(0xd7ff, 0xe000, 0xfffd, 0x10000, 0x10ffff);
  assert.equal(xmlText(valid), valid);
});

test("XML-forbidden text fails before export", () => {
  for (const label of ["x\0", "x\u0001", "x\ufffe", "x\uffff", "x\ud800"]) {
    assert.throws(() => assetSvg({ ...options(), label }), /XML 1.0/);
    assert.throws(() => faceTextSvg("matrix(1 0 0 1 0 0)", label), /XML 1.0/);
  }
});

test("export rejects injected IDs, invalid color inputs, and invalid dimensions", () => {
  assert.throws(() => assetSvg({ ...options(), id: 'x" onload="x' }), /id/);
  assert.throws(() => assetSvg({ ...options(), paper: "red;@import 'x'" }), /hex color/);
  assert.throws(() => assetSvg({ ...options(), accents: { 'x}': "#ffaa00" } }), /accent name/);
  assert.throws(() => assetSvg({ ...options(), accents: { brand: { hex: "#ffaa00", mode: "other" } } }), /accent mode/);
  for (const width of [NaN, Infinity, -1, 0, 9000]) assert.throws(() => assetSvg({ ...options(), width }), /width/);
  assert.throws(() => assetSvg({ ...options(), weight: NaN }), /weight/);
  assert.deepEqual(hexToRgb("#fff"), [1, 1, 1]);
});

test("one template returns deterministic static markup without resource loads", () => {
  const svg = makeSvg();
  assert.equal(svg, makeSvg());
  finiteMarkup(svg);
  assert.match(svg, /role="img"/);
  assert.match(svg, /<style><!\[CDATA\[/);
  assert.doesNotMatch(svg, /<script|<foreignObject|\bon\w+=|(?:src|href)=|@import|animation:/i);
});
