"""Non-inference checks for the reduced skill; no browser, network, or packages."""
import hashlib
import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/anatomy-asset"


def run_checks():
    provenance = json.loads((SKILL / "PROVENANCE.json").read_text())
    expected = {entry["path"] for entry in provenance["files"]} | {"PROVENANCE.json"}
    actual = {str(path.relative_to(SKILL)) for path in SKILL.rglob("*") if path.is_file()}
    assert actual == expected, (actual - expected, expected - actual)
    assert not any(path.is_symlink() for path in SKILL.rglob("*"))
    assert len(list((SKILL / "templates").glob("*"))) == 1
    for entry in provenance["files"]:
        content = (SKILL / entry["path"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == entry["sha256"], entry["path"]
        if entry["disposition"] == "unchanged":
            blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
            assert blob == entry["source_files"][0]["git_blob"], entry["path"]
    for path in (SKILL / "kit").glob("*.mjs"):
        code = path.read_text()
        assert not re.search(r"child_process|\bfetch\s*\(|\beval\s*\(|new\s+Function\b|https?://(?!www\.w3\.org/2000/svg)|\bimport\s*\(", code), path
        for target in re.findall(r'from\s+[\'"]([^\'"]+)[\'"]', code):
            assert target.startswith("./") and (path.parent / target).is_file(), (path, target)
    template = SKILL / "templates/build.mjs"
    with tempfile.TemporaryDirectory(prefix="anatomy-asset-check-") as scratch:
        target = Path(scratch) / "fresh-output"
        result = subprocess.run(["node", str(template), str(target)], capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, (result.stdout, result.stderr)
        svg_path = target / "asset.svg"
        data = svg_path.read_bytes()
        assert result.stdout.strip() == str(svg_path)
        assert {path.name for path in target.iterdir()} == {"asset.svg"}
        svg = ET.fromstring(data)
        ns = "{http://www.w3.org/2000/svg}"
        assert svg.tag == ns + "svg"
        assert svg.get("viewBox") == "0 0 640 480"
        assert svg.get("role") == "img" and svg.get("aria-label")
        assert len(list(svg.iter(ns + "path"))) >= 10
        allowed = {ns + name for name in ("svg", "g", "path", "style", "rect")}
        for element in svg.iter():
            assert element.tag in allowed, element.tag
            for key, value in element.attrib.items():
                assert not key.lower().startswith("on")
                assert key not in ("href", "src", "{http://www.w3.org/1999/xlink}href")
                assert not re.search(r"NaN|Infinity|undefined", value)
            if element.tag == ns + "style":
                assert not re.search(r"@import|url\s*\(|animation:", element.text or "", re.I)
        collision = subprocess.run(["node", str(template), str(target)], capture_output=True, text=True, timeout=30)
        assert collision.returncode != 0
        assert svg_path.read_bytes() == data
        print(json.dumps({"provenance_files": len(expected), "xml_valid": True, "paths": len(list(svg.iter(ns + 'path'))), "offline_static_template": True, "collision_preserved_output": True, "svg_sha256": hashlib.sha256(data).hexdigest()}))


if __name__ == "__main__":
    run_checks()
