#!/bin/bash
# Script to build the macOS application bundle

# Note: For better macOS compatibility, convert icon.ico to icon.icns
# You can use online converters or tools like ImageMagick:
# magick convert icon/icon.ico icon/icon.icns

# Check if we have an .icns file, otherwise use .ico
if [ -f "icon/icon.icns" ]; then
    ICON_PATH="icon/icon.icns"
else
    ICON_PATH="icon/icon.ico"
    echo "Warning: Using .ico file. For better results, convert to .icns format"
fi

pyinstaller --name DistroLabelApp \
            --onefile \
            --windowed \
            --icon="$ICON_PATH" \
            --add-data "config/label_config.json:config" \
            --add-data "config/SimSun.ttf:config" \
            src/gui.py

echo "Build complete. Look for the app in the dist directory."
