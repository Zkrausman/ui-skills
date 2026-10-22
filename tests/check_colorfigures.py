"""Check the pinned package and build trusted examples only into new scratch outputs.

Uses standard-library Python and existing Node syntax checking. No browser or package
installation, and no execution of the bundled browser JavaScript.
"""
import ast
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/colorfigures"
PIN = "c5f05302d78db757859f7e9c563f20a5482f3cd07e5a44050486289e7fd80143"
FILES = {
    "LICENSE", "README.md", "SKILL.md", "assets/core.js", "assets/examples/claw.html",
    "assets/examples/lamp.html", "assets/examples/toaster.html", "scripts/build.py",
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.styles = []
        self.resource_attributes = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script":
            self.current = {"attrs": attrs, "text": ""}
            self.scripts.append(self.current)
        elif tag == "style":
            self.current = {"text": ""}
            self.styles.append(self.current)
        if tag in {"script", "link", "img", "iframe", "source", "video", "audio", "object", "embed", "image", "use"}:
            for key in ("src", "srcset", "href", "xlink:href", "data", "poster"):
                if attrs.get(key):
                    self.resource_attributes.append((tag, key, attrs[key]))

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.current = None

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"] += data


def run(command):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise AssertionError({"command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    return result


def main():
    manifest = json.loads((SKILL / "PROVENANCE.json").read_text())
    assert manifest["source_zip_sha256"] == PIN
    assert manifest["source_zip_bytes"] == 80750
    assert {row["path"] for row in manifest["files"]} == FILES
    assert len(manifest["files"]) == 8
    actual = {str(p.relative_to(SKILL)) for p in SKILL.rglob("*") if p.is_file()}
    assert actual == FILES | {"PROVENANCE.json"}
    assert not any(p.is_symlink() for p in SKILL.rglob("*"))
    for row in manifest["files"]:
        data = (SKILL / row["path"]).read_bytes()
        assert len(data) == row["bytes"], row["path"]
        assert hashlib.sha256(data).hexdigest() == row["sha256"], row["path"]
        if row["path"] != "SKILL.md":
            assert row["sha256"] == row["source_sha256"], row["path"]
        else:
            text = data.decode()
            front, body = text.split("\n---\n", 1)
            description = json.loads(next(line.removeprefix("description: ") for line in front.splitlines() if line.startswith("description: ")))
            assert hashlib.sha256(description.encode()).hexdigest() == row["source_description_sha256"]
            assert hashlib.sha256(body.encode()).hexdigest() == row["source_body_sha256"]
    assert sum(row["source_bytes"] for row in manifest["files"]) == 217209
    license_text = (SKILL / "LICENSE").read_text()
    assert "MIT License" in license_text and "April Zhu" in license_text and "Tolga Cohce" in license_text
    builder = SKILL / "scripts/build.py"
    tree = ast.parse(builder.read_text())
    imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    assert imports == {"os", "re", "sys"}
    assert not any(isinstance(node, ast.ImportFrom) for node in ast.walk(tree))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"exec", "eval", "compile", "__import__"}
    core = SKILL / "assets/core.js"
    run(["node", "--check", str(core)])
    builds = []
    with tempfile.TemporaryDirectory(prefix="colorfigures-gate-") as scratch_name:
        scratch = Path(scratch_name)
        for name in ("claw", "lamp", "toaster"):
            source = SKILL / f"assets/examples/{name}.html"
            output = scratch / f"{name}-built.html"
            assert not output.exists()
            result = run([sys.executable, str(builder), str(source), str(output)])
            assert output.is_file() and result.stdout.strip() == f"wrote {output}"
            page = output.read_text()
            parsed = Page()
            parsed.feed(page)
            assert parsed.scripts and all(not item["attrs"].get("src") for item in parsed.scripts)
            assert all(value.startswith("#") for _, _, value in parsed.resource_attributes), parsed.resource_attributes
            assert not re.search(r"@import|url\s*\(\s*['\"]?(?:https?:|//)", "\n".join(s["text"] for s in parsed.styles), re.I)
            assert all(item["attrs"].get("type", "text/javascript") in ("text/javascript", "application/javascript", "") for item in parsed.scripts)
            script = scratch / f"{name}-syntax.js"
            script.write_text("\n;\n".join(item["text"] for item in parsed.scripts))
            run(["node", "--check", str(script)])
            assert not re.search(r"\bfetch\s*\(|\bXMLHttpRequest\b|\bWebSocket\b|\beval\s*\(|new\s+Function\b|\b(?:localStorage|sessionStorage|indexedDB)\b", script.read_text())
            builds.append({"example": name, "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "inline_scripts": len(parsed.scripts), "node_syntax_exit_code": 0})
        invalid = scratch / "missing-marker.html"
        invalid.write_text("<!doctype html><title>Invalid fixture</title>")
        rejected = scratch / "must-not-be-created.html"
        assert not rejected.exists()
        result = subprocess.run([sys.executable, str(builder), str(invalid), str(rejected)], cwd=scratch, capture_output=True, text=True, timeout=30)
        assert result.returncode != 0 and not rejected.exists()
    print(json.dumps({"vendor_files_unchanged": 7, "skill_frontmatter_quoted_only": True, "provenance_valid": True, "license_notices_retained": True, "builds": builds, "missing_marker_rejected_without_output": True, "all_build_targets_were_fresh": True, "browser_js_executed": False, "browser_validation": "unrun"}))


if __name__ == "__main__":
    main()
