#!/usr/bin/env bash
set -euo pipefail

# Script to build the macOS application bundle
# NOTE: Run this on macOS. PyInstaller does not cross-compile from Linux to macOS.

# Prefer .icns for macOS apps
if [[ -f "icon/icon.icns" ]]; then
  ICON_PATH="icon/icon.icns"
else
  ICON_PATH="icon/icon.ico"
  echo "Warning: Using .ico file. Convert to .icns for best results (e.g., with ImageMagick)."
fi

# Ensure required files exist
[[ -f "config/label_config.json" ]] || { echo "Missing config/label_config.json"; exit 1; }
[[ -f "src/gui.py" ]] || { echo "Missing src/gui.py"; exit 1; }

# Build
pyinstaller --name DistroLabelApp \
  --onefile \
  --windowed \
  --icon="$ICON_PATH" \
  --add-data "config/label_config.json:config" \
  --add-data "config/SimSun.ttf:config" \
  src/gui.py

echo "Build complete. Look in the dist directory."
