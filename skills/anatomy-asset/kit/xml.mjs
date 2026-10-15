// Local hardening for this reduced fork. Geometry and raw SVG remain trusted authored code.
export function xmlText(text) {
  if (typeof text !== "string") throw new TypeError("Expected XML text");
  for (const character of text) {
    const n = character.codePointAt(0);
    if (!(n === 9 || n === 10 || n === 13 || (n >= 0x20 && n <= 0xd7ff) || (n >= 0xe000 && n <= 0xfffd) || (n >= 0x10000 && n <= 0x10ffff))) {
      throw new TypeError("Text contains a character forbidden by XML 1.0");
    }
  }
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}
