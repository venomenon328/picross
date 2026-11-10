"""Change-scoped prompt regression: actual offline JS, no browser or network."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest


class Form(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = {}
        self.select = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.elements[attrs['id']] = {'value': attrs.get('value', ''),
                                         'tagName': tag.upper(), 'options': []}
        if tag == 'select':
            self.select = self.elements[attrs['id']]
        if tag == 'option' and self.select is not None:
            self.select['options'].append({'value': attrs['value']})
            if len(self.select['options']) == 1 or 'selected' in attrs:
                self.select['value'] = attrs['value']

    def handle_endtag(self, tag):
        if tag == 'select':
            self.select = None


class AuthoringSheetTests(unittest.TestCase):
    def test_actual_step_four_default_fallback_attachment_and_saved_ref(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / 'docs/ai-workflows/Picross_Raetselproduktion_Cheat-Sheet.html').read_text(encoding='utf-8')
        authoring = (root / 'docs/ai-workflows/PUZZLE_AUTHORING.md').read_bytes()
        revision = int(re.search(rb'Dokumentrevision (\d+)', authoring)[1])
        snapshot = re.search(r'<script type="application/json" id="rulebookData">(.*?)</script>', html, re.S)[1]
        self.assertEqual(json.loads(snapshot).encode('utf-8'), authoring)
        self.assertIn('Standard: main.', html)
        version = re.search(rb'Version ([0-9.]+)', authoring)[1].decode('ascii')
        self.assertIn(f'Snapshot · {version} / Revision {revision}', html)
        form = Form()
        form.feed(html)
        form.elements['rulebookData']['textContent'] = snapshot
        # Evaluate all real definitions; stop only before UI construction/listeners.
        script = re.search(r'<script>\s*(.*?)</script>', html, re.S)[1]
        definitions, ui = script.split('\nloadSettings();\nbuild();', 1)
        self.assertTrue(ui)
        node = shutil.which('node')
        self.assertIsNotNone(node, 'tools prompt regression requires Node; no silent skip')
        harness = r"""
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const elements = input.elements, store = new Map();
for (const el of Object.values(elements)) el.classList = {toggle() {}};
const sandbox = {structuredClone, document: {getElementById: id => elements[id], documentElement: {dataset: {}}},
 localStorage: {getItem: k => store.get(k) ?? null, setItem: (k, v) => store.set(k, v)}};
vm.createContext(sandbox);
vm.runInContext(input.definitions, sandbox);
const run = code => vm.runInContext(code, sandbox);
run('loadSettings()');
assert.equal(elements.ruleSource.value, 'repo');
assert.equal(elements.ruleRef.value, 'main');
elements.workspaceRoot.value = 'E:\\Picross-work';
elements.packagePath.value = 'content/authoring/synthetic/r01/package.zip';
elements.revision.value = 'r01'; elements.inventoryRef.value = 'a'.repeat(64);
const normal = run("prompt(CARDS.find(c => c.id === 'integrate'))");
assert.deepEqual(Array.from(normal.missing), []);
assert.match(normal.text, /AGENTS\.md aus dem beauftragten Stand main /);
assert.match(normal.text, /Arbeite nach docs\/ai-workflows\/PUZZLE_AUTHORING\.md aus demselben Stand/);
assert.match(normal.text, /Standardauftrag 4/);
assert.equal(run("brief(CARDS.find(c => c.id === 'integrate')).rulebook.repo_ref"), 'main');
elements.ruleRef.value = ''; elements.rulePath.value = '';
assert.match(run('prefix()'), /Stand main /);
assert.match(run('prefix()'), /Arbeite nach docs\/ai-workflows\/PUZZLE_AUTHORING\.md /);
assert.equal(run("brief(CARDS[3]).rulebook.repo_ref"), 'main');
assert.equal(run("brief(CARDS[3]).rulebook.file"), 'docs/ai-workflows/PUZZLE_AUTHORING.md');
elements.ruleRef.value = 'feat/479-ri-b-verified-context';
elements.rulePath.value = 'docs/ai-workflows/PUZZLE_AUTHORING.md';
run('saveSettings()'); elements.ruleRef.value = 'main'; run('loadSettings()');
assert.equal(elements.ruleRef.value, 'feat/479-ri-b-verified-context');
assert.match(run('prompt(CARDS[3]).text'), /Stand feat\/479-ri-b-verified-context /);
assert.equal(run('brief(CARDS[3]).rulebook.repo_ref'), 'feat/479-ri-b-verified-context');
elements.ruleSource.value = 'attachment';
assert.match(run('prompt(CARDS[3]).text'), new RegExp('PICROSS_PUZZLE_AUTHORING.md .*Dokumentrevision ' + input.revision));
assert.equal(run('brief(CARDS[3]).rulebook.document_revision'), input.revision);
assert.equal(run('RULEBOOK'), input.authoring);
assert.throws(() => run("parseTransfer({format:'picross-background-adoption-request-v1'})"), /Eigenständige Hintergrundrevision/);
assert.equal(elements.ruleRef.value, 'feat/479-ri-b-verified-context');
console.log('PASS actual step-4 default, fallbacks, saved PR ref and attachment');
console.log(normal.text);
"""
        result = subprocess.run([node, '-e', harness], input=json.dumps({
            'elements': form.elements, 'definitions': definitions,
            'revision': revision, 'authoring': authoring.decode('utf-8')}),
            capture_output=True, text=True, encoding='utf-8', timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS actual step-4', result.stdout)
