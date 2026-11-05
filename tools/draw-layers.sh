#!/bin/sh
# Render the five personal layers (and their combos) to SVG, then to PDF.
#
#   pip install keymap-drawer svglib reportlab
#   tools/draw-layers.sh
#
# Output: totem-layers.svg and totem-layers.pdf in the repo root.
# physical-layout.json is a clean printable grid, not the real curved
# geometry -- the board's own info.json renders as an unreadable splay.
set -e
cd "$(dirname "$0")/.."

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
python3 tools/prepare-diagram.py normal > "$tmp/totem.keymap"
keymap -c tools/keymap-drawer.yaml parse -z "$tmp/totem.keymap" \
  | keymap -c tools/keymap-drawer.yaml draw - \
      -j tools/physical-layout.json -l LAYOUT \
  > totem-layers.svg

python3 - <<'PY'
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
renderPDF.drawToFile(svg2rlg("totem-layers.svg"), "totem-layers.pdf")
print("wrote totem-layers.svg and totem-layers.pdf")
PY
