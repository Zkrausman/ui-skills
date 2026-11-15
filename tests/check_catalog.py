"""Check the source catalog without executing any registered skill code."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re


ROOT = Path(__file__).resolve().parents[1]


def local_path(value):
    if not isinstance(value, str) or not value:
        raise ValueError('Catalog paths must be nonempty relative strings')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Catalog path escapes source root: ' + value)
    result = ROOT.joinpath(*path.parts)
    if not result.exists() or not result.resolve().is_relative_to(ROOT):
        raise ValueError('Missing or escaping catalog path: ' + value)
    for parent in (result, *result.parents):
        if parent == ROOT:
            break
        if parent.is_symlink():
            raise ValueError('Catalog source path must not be a symlink: ' + value)
    return result


def main():
    catalog = json.loads((ROOT / 'catalog.json').read_text())
    if catalog['schema_version'] != 1 or catalog['repository'] != 'https://github.com/Zkrausman/ui-skills':
        raise ValueError('Unexpected catalog schema or repository identity')
    names = []
    for entry in catalog['skills']:
        name = entry['name']
        if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            raise ValueError('Invalid package name')
        names.append(name)
        if entry['path'] != 'skills/' + name:
            raise ValueError('Package path/name mismatch')
        package = local_path(entry['path'])
        skill = package / 'SKILL.md'
        text = skill.read_text()
        if not text.startswith('---\n') or '\n---\n' not in text:
            raise ValueError('Missing skill frontmatter: ' + name)
        frontmatter = text.split('\n---\n', 1)[0]
        if f'\nname: {name}\n' not in frontmatter + '\n':
            raise ValueError('Skill frontmatter name mismatch: ' + name)
        if not entry['source_kind'] or not entry['license_status']:
            raise ValueError('Missing ownership/license disposition: ' + name)
        local_path(entry['provenance'])
        for key in ('license_path', 'third_party_notice'):
            if key in entry:
                local_path(entry[key])
    actual = {path.name for path in (ROOT / 'skills').iterdir() if path.is_dir()}
    if len(names) != len(set(names)) or set(names) != actual:
        raise ValueError('Catalog has duplicate, missing or unregistered source packages')
    for entry in catalog['showcases']:
        local_path(entry['path'])
        local_path(entry['provenance'])
    provenance = json.loads((ROOT / 'skills/json-canvas/PROVENANCE.json').read_text())
    for row in provenance['files']:
        file = local_path('skills/json-canvas/' + row['path'])
        if hashlib.sha256(file.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('JSON Canvas handoff hash mismatch: ' + row['path'])
    print(json.dumps({'registered_skills': len(names), 'registered_showcases': len(catalog['showcases']),
                      'package_paths_and_notices_present': True, 'json_canvas_handoff_hashes_valid': True,
                      'skill_code_executed': False, 'activation_performed': False}))


if __name__ == '__main__':
    main()
