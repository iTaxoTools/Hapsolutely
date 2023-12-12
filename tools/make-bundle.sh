#!/bin/sh

# Build a macOS .app bundle

DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Reading config..."
source "$DIR/config.sh" "$@" || exit 1
echo "Building $APP_NAME..."

echo "Calling pyinstaller..."
pyinstaller --noconfirm "$DIR/specs/macos.spec" || exit 1

echo "Cleaning up..."
find "$APP_BUNDLE" -name .DS_Store -delete

echo "Compressing..."
cd "$(dirname "$APP_BUNDLE")"
zip -ry9 "$APP_FILENAME.zip" "$APP_NAME.app"

echo "Success!"
