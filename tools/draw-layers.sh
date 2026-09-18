#!/bin/sh
# Render every layer (and the combos) to SVG, then to PDF.
#
#   pip install keymap-drawer svglib reportlab
#   tools/draw-layers.sh
#
# Output: totem-layers.svg and totem-layers.pdf in the repo root.
# physical-layout.json is a clean printable grid, not the real curved
# geometry -- the board's own info.json renders as an unreadable splay.
set -e
cd "$(dirname "$0")/.."

keymap parse -z config/totem.keymap \
  | keymap -c tools/keymap-drawer.yaml draw - \
      -j tools/physical-layout.json -l LAYOUT \
  > totem-layers.svg

python3 - <<'PY'
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
renderPDF.drawToFile(svg2rlg("totem-layers.svg"), "totem-layers.pdf")
print("wrote totem-layers.svg and totem-layers.pdf")
PY
