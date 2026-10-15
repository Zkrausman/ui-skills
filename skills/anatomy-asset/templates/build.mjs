// One local SVG template for the reduced fork. Adapt a copy; do not execute remote source.
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve, join } from "node:path";
import { fileURLToPath } from "node:url";
import { boxCorners, slabOf, cylinder, solidSvg } from "../kit/iso-kit.mjs";
import { fitInto, assetSvg } from "../kit/asset.mjs";

export function makeSvg() {
  const base = { x: 0, y: 0, w: 110, d: 74, r: 5 };
  const casePlan = { x: 15, y: 12, w: 80, d: 50, r: 4 };
  const extremes = [...boxCorners(base, 0, 9), ...boxCorners(casePlan, 9, 42), ...boxCorners({ x: 43, y: 25, w: 24, d: 24 }, 42, 49)];
  const P = fitInto(extremes, { x: 0, y: 0, w: 640, h: 480 }, { pad: 46 });
  const body = [
    solidSvg(slabOf(base, 0, 9, P), { tone: "lo", halo: true }),
    solidSvg(slabOf(casePlan, 9, 33, P), { tone: "mid" }),
    '<g class="ac-brass">' + solidSvg(cylinder(55, 37, 12, 42, 7, P), { tone: "hi" }) + '</g>',
  ];
  return assetSvg({ width: 640, height: 480, label: "A compact instrument with a brass dial on a rounded case", body, paper: "#f5f1e8", theme: "light", accents: { brass: "#b67d32" }, weight: 0.7, id: "instrument-asset" });
}

export function writeTemplate(outputDirectory) {
  if (typeof outputDirectory !== "string" || !outputDirectory) throw new TypeError("Choose a new output directory");
  const svg = makeSvg();
  const directory = resolve(outputDirectory);
  mkdirSync(directory);
  const destination = join(directory, "asset.svg");
  writeFileSync(destination, svg, { encoding: "utf8", flag: "wx" });
  return destination;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv.length !== 3) {
    console.error("usage: node templates/build.mjs NEW_OUTPUT_DIRECTORY");
    process.exitCode = 2;
  } else {
    try { console.log(writeTemplate(process.argv[2])); }
    catch (error) { console.error(error.message); process.exitCode = 1; }
  }
}
