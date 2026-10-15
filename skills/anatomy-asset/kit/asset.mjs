// Reduced static SVG export fork; see ../PROVENANCE.json and ../LICENSE.
import { xmlText } from "./xml.mjs";
import { ISO_CSS, fitProjection } from "./iso-kit.mjs";

// ---------- colour (OKLab / OKLCH) ----------

const toLinear = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const toGamma = (c) => (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055);

export function hexToRgb(hex) {
  if (typeof hex !== "string" || !/^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(hex)) throw new TypeError("Expected a three- or six-digit hex color");
  let h = hex.slice(1);
  if (h.length === 3) h = [...h].map((c) => c + c).join("");
  const n = parseInt(h.slice(0, 6), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => v / 255);
}

const rgbToHex = (rgb) => `#${rgb.map((v) => Math.round(Math.min(1, Math.max(0, v)) * 255).toString(16).padStart(2, "0")).join("")}`;

export function hexToOklch(hex) {
  const [r, g, b] = hexToRgb(hex).map(toLinear);
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  const L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s;
  const A = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s;
  const B = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s;
  return [L, Math.hypot(A, B), Math.atan2(B, A)];
}

function oklchToRgb([L, C, H]) {
  const A = C * Math.cos(H);
  const B = C * Math.sin(H);
  const l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3;
  const m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3;
  const s = (L - 0.0894841775 * A - 1.291485548 * B) ** 3;
  return [
    4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
    -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
    -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s,
  ];
}

// Lightness is kept exactly; chroma is reduced until the colour fits sRGB.
export function oklchToHex([L, C, H]) {
  const l = Math.min(1, Math.max(0, L));
  let c = Math.max(0, C);
  for (let i = 0; i < 40; i++) {
    const rgb = oklchToRgb([l, c, H]);
    if (rgb.every((v) => v >= -1e-4 && v <= 1 + 1e-4)) return rgbToHex(rgb.map(toGamma));
    c *= 0.92;
  }
  return rgbToHex(oklchToRgb([l, 0, H]).map(toGamma));
}

export const lightnessOf = (hex) => hexToOklch(hex)[0];
export const themeFor = (paper) => (lightnessOf(paper) > 0.6 ? "light" : "dark");

// ---------- the ground: the neutral ramp, re-derived for any page colour ----------

// The kit's own token values (ISO_CSS), so a new ground keeps the same steps.
const BASE = {
  dark: {
    paper: "#131313", face: "#1b1b1b", top: "#1c1c1c",
    "shade-0": "#0f0f0f", "shade-1": "#121212", "shade-2": "#151515", "shade-3": "#181818",
    "lit-top": "#262626", "lit-shade": "#1d1d1d",
    hi: "#d4d4d4", mid: "#6a6a6a", lo: "#3e3e3e", faint: "#2a2a2a",
    halo: "#050505", dot: "#e6e6e6",
  },
  light: {
    paper: "#fbfbfa", face: "#ffffff", top: "#ffffff",
    "shade-0": "#dcdcd9", "shade-1": "#e5e5e2", "shade-2": "#ededea", "shade-3": "#f4f4f1",
    "lit-top": "#ffffff", "lit-shade": "#eeeeeb",
    hi: "#26262a", mid: "#8a8a8f", lo: "#b4b4b8", faint: "#d4d4d6",
    halo: "#8a8a80", dot: "#3a3a3e",
  },
};

const labOf = (hex) => { const [L, C, H] = hexToOklch(hex); return [L, C * Math.cos(H), C * Math.sin(H)]; };
const fromLab = ([L, A, B]) => oklchToHex([L, Math.hypot(A, B), Math.atan2(B, A)]);

// Every token keeps its own offset from the kit's paper (lightness and tint), moved by how far
// the new paper is from the kit's: in lightness fully, in colour by `tint` (0..1). Faces,
// shades and lines then sit on the page as the defaults sit on the card, and the kit's own
// papers give back the kit's own ramps.
export function groundTokens(paper, { theme = themeFor(paper), tint = 0.6 } = {}) {
  const base = BASE[theme];
  const p = labOf(paper);
  const b = labOf(base.paper);
  const shift = [p[0] - b[0], (p[1] - b[1]) * tint, (p[2] - b[2]) * tint];
  const out = {};
  for (const [name, hex] of Object.entries(base)) {
    if (name === "paper") { out.paper = paper; continue; }
    const t = labOf(hex);
    out[name] = fromLab([t[0] + shift[0], t[1] + shift[1], t[2] + shift[2]]);
  }
  out.card = paper;
  out.page = paper;
  return out;
}

const declare = (tokens) => Object.entries(tokens).map(([name, value]) => `--anatomy-${name}:${value}`).join(";");

// ---------- accents: a brand colour as a scoped token set ----------

// mode "body": the part is made of the colour; its faces, shades and lines are a ramp of it.
// mode "ink":  the part stays neutral; only its lines, dots and lit edge take the colour
//              (an engraved mark, an LED ring, a lit accent edge).
export function accentTokens(hex, { theme = "dark", mode = "body" } = {}) {
  const [L, C, H] = hexToOklch(hex);
  const at = (l, c = C) => oklchToHex([l, c, H]);
  if (mode === "ink") {
    return theme === "light"
      ? { hi: at(Math.min(L, 0.5)), mid: at(L), lo: at(L + (1 - L) * 0.45, C * 0.6), faint: at(L + (1 - L) * 0.7, C * 0.35), lit: at(Math.min(L, 0.55)), dot: at(Math.min(L, 0.55)) }
      : { hi: at(Math.max(L, 0.78), C * 0.8), mid: at(L), lo: at(L * 0.6, C * 0.7), faint: at(L * 0.42, C * 0.5), lit: at(Math.max(L, 0.85), C * 0.6), dot: at(Math.max(L, 0.8)) };
  }
  if (theme === "light") {
    const b = Math.min(Math.max(L, 0.3), 0.86);
    return {
      paper: at(b - 0.03), face: at(b + 0.04), top: at(b + 0.05, C * 0.85),
      "shade-0": at(b - 0.09), "shade-1": at(b - 0.06), "shade-2": at(b - 0.03), "shade-3": at(b),
      "lit-top": at(b + 0.08, C * 0.7), "lit-shade": at(b - 0.01),
      hi: at(Math.max(b - 0.42, 0.14), C * 0.7), mid: at(b - 0.24, C * 0.9), lo: at(b - 0.13), faint: at(b - 0.07),
      lit: at(Math.max(b - 0.5, 0.08), C * 0.6), dot: at(Math.max(b - 0.4, 0.16), C * 0.7),
    };
  }
  const b = Math.min(Math.max(L * 0.72, 0.14), 0.6);
  return {
    paper: at(b - 0.05), face: at(b + 0.02), top: at(b + 0.04),
    "shade-0": at(b - 0.1), "shade-1": at(b - 0.075), "shade-2": at(b - 0.05), "shade-3": at(b - 0.025),
    "lit-top": at(b + 0.1), "lit-shade": at(b),
    hi: at(Math.min(b + 0.36, 0.95), C * 0.6), mid: at(b + 0.16), lo: at(b - 0.12), faint: at(b - 0.17),
    lit: at(Math.min(b + 0.42, 0.97), C * 0.4), dot: at(Math.min(b + 0.36, 0.95), C * 0.6),
  };
}

// CSS for a set of accents: { orange: "#ff6a1a", led: { hex: "#38f", mode: "ink" } }.
// Wrap a part in `<g class="ac-orange">` and every kit fill, shade and line inside takes the
// ramp. Pass `scope` so two assets inlined on one page don't fight.
export function accentCss(accents = {}, { scope = "", theme } = {}) {
  const rules = [];
  for (const [name, spec] of Object.entries(accents)) {
    if (!/^[a-z][a-z0-9-]{0,31}$/.test(name)) throw new TypeError("Invalid accent name");
    const { hex, mode = "body" } = typeof spec === "string" ? { hex: spec } : spec;
    if (mode !== "body" && mode !== "ink") throw new TypeError("Invalid accent mode");
    if (theme) {
      rules.push(`${scope} .ac-${name}{${declare(accentTokens(hex, { theme, mode }))}}`);
    } else {
      rules.push(`${scope} .ac-${name}{${declare(accentTokens(hex, { theme: "dark", mode }))}}`);
      rules.push(`${scope}[data-theme="light"] .ac-${name}{${declare(accentTokens(hex, { theme: "light", mode }))}}`);
    }
  }
  return rules.join("\n");
}

// ---------- layout ----------

// fitProjection into one region of the canvas: { x, y, w, h } in viewBox units. Use it to
// keep a hero object on one side and leave the other side free for a headline.
export function fitInto(points, region, options = {}) {
  const P = fitProjection(points, region.w, region.h, options);
  return { ...P, origin: [P.origin[0] + region.x, P.origin[1] + region.y] };
}

let counter = 0;

// Only geometry produced by trusted authored source belongs in body. This is an exporter,
// not a sanitizer for uploaded SVG, arbitrary CSS, or executable scene configuration.
export function assetSvg({ width, height, label, body, paper, theme, accents = {}, tint = 0.6, weight, background = false, id }) {
  for (const [name, value] of Object.entries({ width, height })) {
    if (!Number.isFinite(value) || value <= 0 || value > 8192) throw new RangeError(`Invalid ${name}`);
  }
  if (typeof label !== "string" || !label.trim() || label.length > 500) throw new TypeError("Expected a label of 1–500 characters");
  const safeLabel = xmlText(label);
  if (paper !== undefined) hexToRgb(paper);
  const t = theme ?? (paper ? themeFor(paper) : "dark");
  if (t !== "light" && t !== "dark") throw new TypeError("Invalid theme");
  if (!Number.isFinite(tint) || tint < 0 || tint > 1) throw new RangeError("Invalid tint");
  if (weight !== undefined && (!Number.isFinite(weight) || weight < 0.1 || weight > 5)) throw new RangeError("Invalid weight");
  if (typeof background !== "boolean") throw new TypeError("Invalid background flag");
  if (!accents || typeof accents !== "object" || Array.isArray(accents) || Object.keys(accents).length > 16) throw new TypeError("Expected at most 16 named accents");
  const sid = id ?? `asset-${(++counter).toString(36)}`;
  if (typeof sid !== "string" || !/^[A-Za-z][A-Za-z0-9_-]{0,63}$/.test(sid)) throw new TypeError("Invalid SVG id");
  const pieces = Array.isArray(body) ? body : [body];
  if (!pieces.length || pieces.some(piece => typeof piece !== "string")) throw new TypeError("Expected trusted SVG strings");
  const art = pieces.join("");
  if (art.length > 10_000_000) throw new RangeError("SVG body is too large");
  const scope = `#${sid}`;
  const ground = paper ? `${scope}.iso{${declare(groundTokens(paper, { theme: t, tint }))}}` : "";
  const stroke = weight === undefined ? "" : `${scope}.iso{--anatomy-weight:${weight}px}`;
  const style = [ISO_CSS, ground, stroke, accentCss(accents, { scope, theme: t })].join("\n");
  const bg = background ? `<rect width="${width}" height="${height}" fill="var(--anatomy-paper)"/>` : "";
  return `<svg xmlns="http://www.w3.org/2000/svg" id="${sid}" class="iso-svg iso" data-theme="${t}" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" role="img" aria-label="${safeLabel}"><style><![CDATA[${style}]]></style>${bg}<g data-art="">${art}</g></svg>`;
}
