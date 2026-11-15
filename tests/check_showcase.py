"""Check public-source privacy boundaries, licenses, links and gallery contracts."""
import ast
import base64
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'showcase/ai-showcase'
DIST = SOURCE / 'dist'
FACES = ['Meridian', 'Relay', 'Bastion', 'Comet', 'Beacon', 'Aperture',
         'Ribbon', 'Facet', 'Ledger', 'Mosaic']


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.resources, self.scripts = [], [], []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
        if tag in {'script', 'img', 'iframe', 'link', 'source', 'video', 'audio', 'object', 'embed'}:
            for key in ('src', 'href', 'data', 'poster', 'srcset'):
                if attrs.get(key):
                    self.resources.append(attrs[key])
        if tag == 'script':
            self.current = {'type': attrs.get('type', ''), 'text': ''}
            self.scripts.append(self.current)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.current = None

    def handle_data(self, data):
        if self.current is not None:
            self.current['text'] += data


def font_names(data):
    tables = {}
    count = struct.unpack_from('>H', data, 4)[0]
    for index in range(count):
        tag, _, offset, length = struct.unpack_from('>4sIII', data, 12 + 16*index)
        assert offset + length <= len(data)
        tables[tag] = (offset, length)
    offset, length = tables[b'name']
    _, count, strings = struct.unpack_from('>HHH', data, offset)
    records = []
    for index in range(count):
        platform, _, _, name, size, start = struct.unpack_from('>HHHHHH', data, offset+6+12*index)
        assert strings + start + size <= length
        text = data[offset+strings+start:offset+strings+start+size].decode('utf-16-be' if platform in (0, 3) else 'mac_roman')
        records.append((name, text))
    return records


def local_reference(page, value, navigation=False):
    url = urlsplit(unquote(value))
    if url.scheme == 'data':
        return
    if url.scheme or url.netloc:
        assert navigation and url.scheme == 'https' and url.netloc in {'github.com', 'openfontlicense.org'}, value
        return
    if not url.path:
        return
    target = (page.parent / unquote(url.path)).resolve()
    assert target.is_relative_to(DIST) and target.is_file(), (page, value)


def main():
    provenance = json.loads((SOURCE / 'PROVENANCE.json').read_text())
    expected = {row['path'] for row in provenance['files']} | {'PROVENANCE.json'}
    files = [p for p in SOURCE.rglob('*') if p.is_file()]
    assert {str(p.relative_to(SOURCE)) for p in files} == expected
    assert not any(p.is_symlink() for p in SOURCE.rglob('*'))
    assert not any(p.suffix == '.pyc' or '.openai' in p.parts or '__pycache__' in p.parts for p in files)
    assert not (DIST / 'demos/font').exists()
    for row in provenance['files']:
        assert hashlib.sha256((SOURCE / row['path']).read_bytes()).hexdigest() == row['sha256']
        if row['disposition'] == 'unchanged frozen bytes':
            assert row['sha256'] == row['source_sha256']
    fonts = sorted(DIST.rglob('*.ttf'))
    assert {p.name for p in fonts} == {f'ZK-{face}-Regular.ttf' for face in FACES} | {'meridian.ttf'}
    assert len(fonts) == 11
    copyright_text = 'Copyright 2026 The ZK Original Font Project Authors.'
    assert (DIST / 'OFL.txt').read_text().startswith(copyright_text)
    for font in fonts:
        records = font_names(font.read_bytes())
        assert (0, copyright_text) in records
        assert (13, 'SIL Open Font License, Version 1.1.') in records
        assert (14, 'https://openfontlicense.org') in records
        for _, text in records:
            assert not re.search(r'/home/|/Users/|/mnt/data/|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text)
    assert (DIST/'meridian.ttf').read_bytes() == (DIST/'ZK-Meridian-Regular.ttf').read_bytes()
    assert not re.search(rb'-----BEGIN [A-Z ]*PRIVATE KEY|\bghp_[A-Za-z0-9]{20,}|\bsk-[A-Za-z0-9_-]{24,}', b'\n'.join(p.read_bytes() for p in files))
    pages = {}
    syntax_checks = 0
    with tempfile.TemporaryDirectory(prefix='public-showcase-check-') as temporary:
        scratch = Path(temporary)
        for page in DIST.rglob('*.html'):
            text = page.read_text()
            parsed = Page()
            parsed.feed(text)
            pages[str(page.relative_to(DIST))] = parsed
            for value in parsed.links:
                local_reference(page, value, navigation=True)
            for value in parsed.resources:
                local_reference(page, value)
            for value in re.findall(r'url\(\s*[\'"]?([^\)\'"\s]+)', text):
                local_reference(page, value)
            for index, script in enumerate(parsed.scripts):
                if not script['text'].strip():
                    continue
                if script['type'] not in {'', 'text/javascript', 'application/javascript', 'module'}:
                    continue
                target = scratch / f'script-{syntax_checks}.mjs'
                target.write_text(script['text'])
                subprocess.run(['node', '--check', str(target)], check=True, capture_output=True, text=True, timeout=30)
                syntax_checks += 1
        for script in list(DIST.rglob('*.js')) + list((SOURCE/'vendor').rglob('*.js')):
            target = scratch / f'file-{syntax_checks}.mjs'
            target.write_bytes(script.read_bytes())
            subprocess.run(['node', '--check', str(target)], check=True, capture_output=True, text=True, timeout=30)
            syntax_checks += 1
        for script in (SOURCE/'vendor').rglob('*.py'):
            ast.parse(script.read_text())
        # Exercise only the gallery shell and licensed specimen, using DOM stubs.
        scripts = {name: '\n'.join(s['text'] for s in pages[name].scripts) for name in ('index.html', 'demos/typography.html')}
        harness = scratch/'interactions.cjs'
        harness.write_text('''const assert=require('node:assert/strict'),vm=require('node:vm');
const programs=''' + json.dumps(scripts) + ''';
function element(value=''){return {value,style:{},dataset:{},attrs:{},textContent:'',setAttribute(k,v){this.attrs[k]=v},focus(){this.focused=true}}}
const tabs=['colorfigures.html','anatomy.html','foundry.html','typography.html'].map(d=>Object.assign(element(),{dataset:{demo:d}}));
const tiles=['Meridian','Relay','Bastion','Comet','Beacon','Aperture','Ribbon','Facet','Ledger','Mosaic'].map(f=>Object.assign(element(),{dataset:{font:f}}));
const ids=Object.fromEntries(['demoTitle','demoText','demoBadge','demoFrame','demoOpen','theme','font','sample','specimen'].map(k=>[k,element()]));ids.font.value='Meridian';ids.sample.value='Safe sample';
let light=false;const document={getElementById:k=>ids[k],querySelectorAll:s=>s==='[data-demo]'?tabs:tiles,documentElement:{classList:{toggle(){return light=!light}}}};
vm.runInNewContext(programs['index.html'],{document});
for(const tab of tabs){tab.onclick();assert.equal(ids.demoFrame.src,'demos/'+tab.dataset.demo);assert.equal(ids.demoOpen.href,ids.demoFrame.src);assert.equal(tab.attrs['aria-pressed'],'true');assert.equal(tabs.filter(t=>t.attrs['aria-pressed']==='true').length,1)}
ids.theme.onclick();assert.equal(ids.theme.textContent,'Dark mode');ids.theme.onclick();assert.equal(ids.theme.textContent,'Light mode');
ids.sample.value='<img src=x onerror=alert(1)>';ids.sample.oninput();assert.equal(ids.specimen.textContent,ids.sample.value);tiles[9].onclick();assert.equal(ids.font.value,'Mosaic');assert.ok(ids.specimen.style.fontFamily.includes('Mosaic'));
const specimen={face:element('Meridian'),copy:element('<b>literal</b>'),display:element(),body:element()};
vm.runInNewContext(programs['demos/typography.html'],{document:{getElementById:k=>specimen[k]}});assert.ok(specimen.display.textContent.startsWith('<b>literal</b>'));specimen.face.value='Relay';specimen.face.onchange();assert.ok(specimen.body.style.fontFamily.includes('Relay'));
console.log(JSON.stringify({gallery_tabs:4,theme_toggle:true,font_choices:10,literal_text_preserved:true}));
''')
        interaction = subprocess.run(['node', str(harness)], check=True, capture_output=True, text=True, timeout=30)
    canvas = json.loads((DIST/'demos/workflow.canvas').read_text())
    ids = [node['id'] for node in canvas['nodes']]
    assert len(ids) == len(set(ids))
    assert all(edge['fromNode'] in ids and edge['toNode'] in ids for edge in canvas['edges'])
    print(json.dumps({'showcase_files': len(files), 'licensed_fonts': len(fonts), 'script_syntax_checks': syntax_checks,
                      'local_assets_resolve': True, 'source_hashes_match': True,
                      'excluded_binding_cache_and_font_demo_absent': True,
                      'gallery_contracts': json.loads(interaction.stdout), 'browser_rendering': 'separate check'}))


if __name__ == '__main__':
    main()
