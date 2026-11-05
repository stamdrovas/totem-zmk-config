#!/bin/sh
# Same parser/drawer/PDF engine as the normal diagram; guest outputs only.
set -eu
cd "$(dirname "$0")/.."
python3 tools/guest-diagram.py
