#!/bin/sh
# Package the plugin as an .xpi. manifest.json must sit at the archive root.
set -e
cd "$(dirname "$0")"

VERSION=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' manifest.json | head -1)
OUT="attachment-type-icons-${VERSION}.xpi"

rm -f "$OUT"
zip -r -q -X "$OUT" manifest.json bootstrap.js style.css icons
echo "$OUT"
