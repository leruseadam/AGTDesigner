#!/bin/bash
set -euo pipefail

# Build a macOS app bundle with PyInstaller using app_webview.py

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

ICON_PATH="$ROOT_DIR/assets/favicon.icns"
if [[ ! -f "$ICON_PATH" ]]; then
  ICON_PATH="$ROOT_DIR/static/favicon.icns"
fi

if [[ ! -f "$ICON_PATH" ]]; then
  echo "Warning: .icns icon not found. You can add one at assets/favicon.icns for a nicer app icon."
fi

echo "Installing build dependencies..."
python3 -m pip install --upgrade pip pyinstaller

echo "Building app..."
pyinstaller --noconfirm --clean \
  --name "AGTDesigner" \
  ${ICON_PATH:+--icon "$ICON_PATH"} \
  --add-data "$ROOT_DIR/static:static" \
  --add-data "$ROOT_DIR/templates:templates" \
  --add-data "$ROOT_DIR/assets:assets" \
  --add-data "$ROOT_DIR/src/core/generation/templates:src/core/generation/templates" \
  "$ROOT_DIR/app_webview.py"

echo "Done. App folder at: $ROOT_DIR/dist/AGTDesigner"
echo "Launch with: dist/AGTDesigner/AGTDesigner"

