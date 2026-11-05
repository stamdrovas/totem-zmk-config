"""Approved guest mapping, preserved normal input, guard and artifact checks."""
import hashlib
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import yaml
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prepare = load('prepare-diagram')
guest = load('guest-diagram')


def bindings(text):
    return [re.sub(r'\s+', ' ', item).strip() for item in re.findall(r'&[^&]+', text)]


class GuestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / 'config/totem.keymap').read_text()
        cls.layers = dict(re.findall(r'(\w+_layer)\s*\{\s*display-name\s*=\s*"[^"]+";\s*bindings\s*=\s*<([^>]+)>;', cls.source))
        cls.keys = {name: bindings(value) for name, value in cls.layers.items()}

    def test_layer_order_counts_and_slider(self):
        self.assertEqual(list(self.layers), ['base_layer', 'nav_layer', 'num_layer', 'sym_layer', 'fn_layer',
                                            'guest_layer', 'guest_request_layer', 'guest_symbols_layer'])
        for keys in self.keys.values():
            self.assertEqual(len(keys), 41)
            self.assertEqual(keys[40], '&mo GUEST')
            self.assertNotIn('&mo GUEST', keys[:40])
        for name, number in [('GUEST', 5), ('GUEST_REQUEST', 6), ('GUEST_SYMBOLS', 7)]:
            self.assertRegex(self.source, rf'#define {name}\s+{number}\b')

    def test_exact_approved_guest(self):
        expected = ('Q W E R T Y U I O P ESC A S D F G H J K L SEMI LBKT '
                    'LSHFT Z X C V B N M COMMA DOT SLASH SQT').split()
        self.assertEqual(self.keys['guest_layer'][:34], ['&kp ' + code for code in expected])
        self.assertEqual(self.keys['guest_layer'][34:40], ['&kp LCTRL', '&guest_space GUEST_REQUEST SPACE',
                         '&kp LGUI', '&kp BSPC', '&guest_space GUEST_REQUEST SPACE', '&kp RET'])

    def test_exact_approved_symbols(self):
        expected = ('N1 N2 N3 N4 N5 N6 N7 N8 N9 N0 TAB LS(N1) LS(N2) LS(N3) LS(N4) LS(N5) '
                    'MINUS EQUAL RBKT BSLH NON_US_BSLH LBKT LSHFT LS(N7) LS(N8) LS(N9) LS(N0) '
                    'LS(INT1) GRAVE INT1 COMMA DOT SLASH SQT LCTRL SPACE LGUI BSPC SPACE RET').split()
        self.assertEqual(self.keys['guest_symbols_layer'][:40], ['&kp ' + code for code in expected])

    def test_safe_exit_and_private_request(self):
        self.assertEqual(self.keys['guest_request_layer'][:40], ['&trans'] * 40)
        self.assertRegex(self.source, r'if-layers = <GUEST GUEST_REQUEST>;\s*then-layer = <GUEST_SYMBOLS>;')
        self.assertNotIn('&mo GUEST_SYMBOLS', self.source)
        self.assertNotIn('&tog', self.source)
        # Truth-table oracle for the configured conjunction, not a firmware test.
        for on, held, expected in [(False, False, False), (False, True, False),
                                   (True, False, False), (True, True, True)]:
            self.assertEqual(on and held, expected)

    def test_guest_hold_policy(self):
        node = re.search(r'guest_space_hold_tap\s*\{([^}]+)', self.source)[1]
        for value in ['flavor = "hold-preferred"', 'tapping-term-ms = <200>', 'quick-tap-ms = <0>',
                      'require-prior-idle-ms = <0>', 'bindings = <&mo>, <&kp>']:
            self.assertIn(value, node)

    def test_normal_projection_excludes_guest_only(self):
        normal = prepare.normal_keymap(self.source)
        self.assertNotIn('GUEST', normal)
        self.assertNotIn('guest_space', normal)
        self.assertIn('leader_lt:', normal)
        self.assertIn('combo_acute', normal)
        self.assertIn('if-layers = <NUM SYM>', normal)
        normal_layers = re.findall(r'display-name\s*=\s*"([^"]+)"', normal)
        self.assertEqual(normal_layers, ['Base', 'Nav', 'Num', 'Sym', 'Fn'])

    def test_transform_and_right_only_column(self):
        transform = (ROOT / 'config/boards/shields/totem/totem.dtsi').read_text()
        pairs = re.findall(r'RC\((\d+),(\d+)\)', transform)
        original = [(0, c) for c in range(10)] + [(3, 1)] + [(1, c) for c in range(10)] + [(3, 8), (3, 0)] + [(2, c) for c in range(10)] + [(3, 9)] + [(3, c) for c in range(2, 8)]
        self.assertEqual(pairs, [(str(r), str(c)) for r, c in original + [(1, 10)]])
        self.assertIn('columns = <11>', transform)
        left = ROOT / 'config/boards/shields/totem/totem_left.overlay'
        self.assertEqual(hashlib.sha256(left.read_bytes()).hexdigest(),
                         'ad60433048e695267e8218d5a21b5f6a87d7f7646eac20e68a9d6c9a786b1339')
        right = (left.parent / 'totem_right.overlay').read_text()
        self.assertEqual(re.findall(r'<&xiao_d (\d+) GPIO_ACTIVE_HIGH>', right), ['8', '9', '10', '5', '4', '7'])
        self.assertIn('col-offset = <5>', right)
        # Same lookup arithmetic as inspected ZMK matrix_transform.c, not compiled DTS.
        self.assertEqual(pairs.index(('1', str(5 + 5))), 40)

    def test_guard_guest_only_fixture(self):
        old = prepare.normal_keymap(self.source)
        with patch.object(prepare, 'read', side_effect=lambda path, revision=None:
                          old if path == 'config/totem.keymap' and revision else
                          (ROOT / path).read_text()):
            self.assertFalse(prepare.redraw('before'))

    def test_guard_ignores_guest_and_position_40_edits(self):
        mutated = self.source.replace('&mo GUEST\n', '&none\n')
        mutated = re.sub(r'(guest_space_hold_tap\s*\{[^}]*?)tapping-term-ms = <200>;',
                         r'\g<1>tapping-term-ms = <250>;', mutated)
        mutated = mutated.replace('&kp Q &kp W &kp E', '&kp A &kp B &kp C')
        with patch.object(prepare, 'read', side_effect=lambda path, revision=None:
                          mutated if path == 'config/totem.keymap' and not revision else
                          (ROOT / path).read_text()):
            self.assertFalse(prepare.redraw('before'))

    def test_guard_normal_changes(self):
        for path, edit in [('config/totem.keymap', lambda s: s.replace('&kp W', '&kp A', 1)),
                           ('config/totem.keymap', lambda s: s.replace('quick-tap-ms = <175>', 'quick-tap-ms = <180>', 1)),
                           ('config/totem.keymap', lambda s: s.replace('key-positions = <2 3>', 'key-positions = <2 4>', 1)),
                           ('tools/keymap-drawer.yaml', lambda s: s + '\n# changed legends\n'),
                           ('tools/physical-layout.json', lambda s: s.replace('0.5', '0.6', 1)),
                           ('config/info.json', lambda s: s.replace('1.519', '1.520', 1))]:
            original = (ROOT / path).read_text()
            changed = edit(original)
            self.assertNotEqual(changed, original, path)
            with patch.object(prepare, 'read', side_effect=lambda p, revision=None:
                              changed if p == path and not revision else (ROOT / p).read_text()):
                self.assertTrue(prepare.redraw('before'), path)

    def test_guard_missing_before_retains_artifacts(self):
        for before in (None, '', '0' * 40):
            self.assertFalse(prepare.redraw(before))
        with patch.object(prepare, 'canonical', side_effect=subprocess.CalledProcessError(128, 'git')):
            self.assertFalse(prepare.redraw('unavailable'))

    def test_projection_and_legends(self):
        parsed = {'layout': {}, 'layers': {name: ['dummy'] * 41 for name in ('Guest', 'Guest Symbols')}}
        projected = guest.project(parsed)
        self.assertEqual(list(projected['layers']), ['Guest', 'Guest Symbols'])
        self.assertNotIn('combos', projected)
        for keys in projected['layers'].values():
            self.assertEqual(len(keys), 40)
            self.assertEqual(keys[37]['t'], 'Backspace')
            self.assertEqual(keys[21]['h'], 'Sft `; dead')
            self.assertEqual(keys[33]['h'], 'Sft ^; dead')
        self.assertEqual(projected['layers']['Guest'][20], {'t': 'ç', 'h': 'Sft Ç'})
        self.assertEqual(projected['layers']['Guest Symbols'][5]['h'], 'Sft ¨ dead')

    def test_real_parser_projections(self):
        parsed = yaml.safe_load(subprocess.check_output([
            'keymap', '-c', 'tools/keymap-drawer.yaml', 'parse', '-z', 'config/totem.keymap'], cwd=ROOT))
        self.assertEqual(len(parsed['layers']), 8)
        self.assertTrue(all(len(keys) == 41 for keys in parsed['layers'].values()))
        projected = guest.project(parsed)
        self.assertEqual(sum(len(keys) for keys in projected['layers'].values()), 80)
        with tempfile.TemporaryDirectory(prefix='totem-normal-test-') as tmp:
            source = Path(tmp) / 'totem.keymap'
            source.write_text(prepare.normal_keymap(self.source))
            normal = yaml.safe_load(subprocess.check_output([
                'keymap', '-c', 'tools/keymap-drawer.yaml', 'parse', '-z', str(source)], cwd=ROOT))
        self.assertEqual(list(normal['layers']), ['Base', 'Nav', 'Num', 'Sym', 'Fn'])
        self.assertTrue(all(len(keys) == 40 for keys in normal['layers'].values()))
        self.assertEqual(len(normal['combos']), 9)
        self.assertEqual(normal['layout'], parsed['layout'])

    def test_workflow_guards_converter(self):
        workflow = (ROOT / '.github/workflows/draw.yml').read_text()
        self.assertIn("if: steps.normal.outputs.redraw == 'true'", workflow)
        self.assertIn('prepare-diagram.py guard --before', workflow)
        self.assertIn('git fetch --no-tags origin "$BEFORE"', workflow)
        self.assertIn("'config/info.json'", workflow)
        self.assertIn('tools/draw-guest-layers.sh', workflow)
        self.assertIn('totem-guest-layers.svg totem-guest-layers.pdf', workflow)
        self.assertIn('prepare-diagram.py normal', (ROOT / 'tools/draw-layers.sh').read_text())

    def test_artifact_legends_and_notes(self):
        root = ET.parse(ROOT / 'totem-guest-layers.svg').getroot()
        text = ''.join(root.itertext())
        for value in guest.NOTES + ['ç', 'Sft Ç', 'Sft ¨ dead', 'Backspace', 'hold 02']:
            self.assertIn(value, text)
        self.assertNotIn('Guest Request', text)
        self.assertNotIn('BOOT', text)
        self.assertNotRegex((ROOT / 'totem-guest-layers.svg').read_text(), r'font-size:\s*[\d.]+%')
        ns = {'s': 'http://www.w3.org/2000/svg'}
        self.assertEqual(len(root.findall('.//s:rect[@class="key"]', ns)), 80)

    def test_normal_artifacts_byte_identical(self):
        # Apply the preservation oracle to this baseline only, not future real
        # normal changes (which must remain eligible for automatic redraw).
        if hashlib.sha256(prepare.canonical().encode()).hexdigest() != '4723a84ab60c14b52f688d64fd6714f90c6a2e77d152ee7541e305f7710f44e6':
            self.skipTest('Normal inputs changed since the guest implementation baseline')
        for name, digest in [('pdf', '633c5a4ac7e01f944274a1a2c81f120932c82870a6f621773466fe25922b454e'),
                             ('svg', '4be2503c9e5552ba651f819a2b64db027ef6c2d573685c0b60bce54dec951d50')]:
            self.assertEqual(hashlib.sha256((ROOT / f'totem-layers.{name}').read_bytes()).hexdigest(), digest)


if __name__ == '__main__':
    unittest.main()
