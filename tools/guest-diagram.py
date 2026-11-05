#!/usr/bin/env python3
"""Guest-only projection, legends and printable operating notes."""
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import yaml
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

ROOT = Path(__file__).resolve().parents[1]
NOTES = [
    "TOTEM guest - typist's view: left half at left; thumbs along the bottom.",
    "Host prerequisite: select Brazilian ABNT2. HID output is not portable to a US input source.",
    "Small Sft legend = Shift output; dead = accent then vowel (accent + Space for a literal).",
    "Guest: either Space taps Space; hold 200 ms or press another key for Guest Symbols.",
    "Symbols: the other Space types Space; release the activating Space to return (no handover).",
    "Thumbs L: Ctrl / Space / Command. R: Backspace / Space / Enter. Dedicated left Shift.",
    "Direct shifted convenience symbols need no Shift; extra Shift has no promised alternate output.",
    "Right slider (not a typing key): intended closed = Guest, open = personal; no toggle chord.",
    "Change mode with character/modifier keys released. Guest-off condition removes Symbols even during a hold.",
    "D7 against row D1 and the closed detent are inferred: continuity/events need device verification.",
    "Boot-on, reconnect/wake and held-key exit are unverified. OFF then ON recovery is NOT proven.",
    "If the mode is wrong after reconnect, stop and verify it; do not assume slider position was synchronized.",
    "Space timing, HID accents, both-thumb release order, sleep/current and battery impact need device tests.",
]


def project(parsed):
    layers = {name: parsed['layers'][name][:40] for name in ('Guest', 'Guest Symbols')}
    common = {21: ('´', 'Sft `; dead'), 33: ('~', 'Sft ^; dead'),
              30: (',', 'Sft <'), 31: ('.', 'Sft >'), 32: (';', 'Sft :'),
              34: ('Ctrl', ''), 36: ('Cmd', ''), 37: ('Backspace', ''),
              39: ('Enter', ''), 22: ('Shift', '')}
    for name, keys in layers.items():
        overrides = dict(common)
        if name == 'Guest':
            overrides[20] = ('ç', 'Sft Ç')
            for pos in (35, 38):
                overrides[pos] = ('Space', 'hold 02')
        else:
            for pos, shifted in enumerate(('!', '@', '#', '$', '%', '¨ dead', '&', '*', '(', ')')):
                overrides[pos] = (str((pos + 1) % 10), 'Sft ' + shifted)
            overrides.update({16: ('-', 'Sft _'), 17: ('=', 'Sft +'),
                              18: ('[', 'Sft {'), 19: (']', 'Sft }'),
                              20: ('\\', 'Sft |'), 28: ("'", 'Sft "'),
                              29: ('/', 'Sft ?'), 35: ('Space', 'other thumb'),
                              38: ('Space', 'other thumb')})
        for pos, (tap, hold) in overrides.items():
            keys[pos] = {'t': tap, 'h': hold}
    return {'layout': parsed['layout'], 'layers': layers}


def main():
    parsed = yaml.safe_load(subprocess.check_output([
        'keymap', '-c', 'tools/keymap-drawer.yaml', 'parse', '-z', 'config/totem.keymap'], cwd=ROOT))
    with tempfile.TemporaryDirectory(prefix='totem-guest-draw-') as tmp:
        source = Path(tmp) / 'guest.yaml'
        source.write_text(yaml.safe_dump(project(parsed), allow_unicode=True, sort_keys=False))
        svg = subprocess.check_output(['keymap', '-c', 'tools/keymap-drawer.yaml', 'draw', str(source),
                                       '-j', 'tools/physical-layout.json', '-l', 'LAYOUT'], cwd=ROOT)
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', ns)
    root = ET.fromstring(svg)
    # Guest-only sizing also keeps the full Backspace legend inside its key.
    style = root.find(f'{{{ns}}}style')
    style.text += '\ntext.tap { font-size: 12px; }\n'
    # svglib cannot resolve percentage-sized tspans. Resolve against the
    # guest 12px tap / existing 11px hold CSS sizes.
    for text in root.iter(f'{{{ns}}}text'):
        if text.get('class') == 'label' and text.text in ('Guest:', 'Guest Symbols:'):
            text.text = ('01 ' if text.text == 'Guest:' else '02 ') + text.text
        base = 11 if 'hold' in text.get('class', '').split() else 12
        for span in text.iter(f'{{{ns}}}tspan'):
            style = span.get('style', '')
            span.set('style', re.sub(r'font-size:\s*([\d.]+)%',
                                    lambda m: f'font-size: {base * float(m[1]) / 100:g}px', style))
    width, height = float(root.attrib['width']), float(root.attrib['height'])
    extra = 40 + 20 * len(NOTES)
    root.set('height', str(height + extra))
    root.set('viewBox', f'0 0 {width} {height + extra}')
    root.insert(0, ET.Element(f'{{{ns}}}rect', {
        'width': str(width), 'height': str(height + extra), 'fill': 'white'}))
    for index, note in enumerate(NOTES):
        text = ET.SubElement(root, f'{{{ns}}}text', {
            'x': '20', 'y': str(height + 25 + 20 * index),
            'style': 'text-anchor:start;font-family:DejaVu Sans,sans-serif;font-size:12px;fill:#222'})
        text.text = note
    out = ROOT / 'totem-guest-layers.svg'
    ET.ElementTree(root).write(out, encoding='unicode', xml_declaration=True)
    renderPDF.drawToFile(svg2rlg(str(out)), str(ROOT / 'totem-guest-layers.pdf'))
    print('wrote totem-guest-layers.svg and totem-guest-layers.pdf')


if __name__ == '__main__':
    main()
