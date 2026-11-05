#!/usr/bin/env python3
"""Canonical, forty-key diagram inputs; no generated artifacts are compared."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GUEST_NODES = ('guest_space_hold_tap', 'guest_symbols', 'guest_layer',
               'guest_request_layer', 'guest_symbols_layer')


def normal_keymap(text):
    text = re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)
    for name in GUEST_NODES:
        text = re.sub(r'(?:guest_space:\s*)?\b' + name + r'\s*\{[^{}]*\};', '', text)
    text = re.sub(r'^#define GUEST(?:_REQUEST|_SYMBOLS)?\s+\d+\s*$', '', text, flags=re.M)
    def typing_keys(match):
        keys = re.findall(r'&[^&]+', match[2])
        if len(keys) not in (40, 41):
            raise ValueError('Normal layer must contain 40 typing keys and optional slider')
        return match[1] + ' ' + ''.join(keys[:40]) + '>;'

    text = re.sub(r'((?:base|nav|num|sym|fn)_layer\s*\{[^{}]*?bindings\s*=\s*<)([^>]*?)>;',
                  typing_keys, text)
    return text


def read(path, revision=None):
    if revision:
        return subprocess.check_output(['git', 'show', f'{revision}:{path}'], cwd=ROOT).decode()
    return (ROOT / path).read_text()


def canonical(revision=None):
    keymap = normal_keymap(read('config/totem.keymap', revision))
    return json.dumps({
        'keymap': re.sub(r'\s+', ' ', keymap).strip(),
        'drawer': read('tools/keymap-drawer.yaml', revision),
        'physical': json.loads(read('tools/physical-layout.json', revision)),
        'info': json.loads(read('config/info.json', revision)),
    }, sort_keys=True, ensure_ascii=False)


def redraw(before):
    if not before or set(before) == {'0'}:
        print('No before revision: retain normal artifacts; manual normal redraw required.', file=sys.stderr)
        return False
    try:
        return canonical(before) != canonical()
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        print('Before projection unavailable: retain normal artifacts; manual normal redraw required.', file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('mode', choices=['normal', 'canonical', 'guard'])
    parser.add_argument('--before')
    args = parser.parse_args()
    if args.mode == 'normal':
        print(normal_keymap(read('config/totem.keymap')))
    elif args.mode == 'canonical':
        print(canonical(args.before))
    else:
        print('true' if redraw(args.before) else 'false')


if __name__ == '__main__':
    main()
