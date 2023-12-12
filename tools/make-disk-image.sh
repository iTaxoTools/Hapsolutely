#!/bin/sh

# Create a disk image for a macOS .app bundle

DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Reading config..."
source "$DIR/config.sh" "$@" || exit 1
echo "Bundling $APP_NAME..."

if [ "$CODESIGN_IDENTITY" = "UNKNOWN" ]; then
  echo "No Codesigning identity provided! Abort."
  echo ""
  echo "Try running: security find-identity -v -p codesigning"
  echo "Find the hash for \"Developer ID Application\""
  echo "Then: export CODESIGN_IDENTITY=\$HASH"
  exit 1
fi

echo "Cleaning up..."
find "$APP_BUNDLE" -name .DS_Store -delete

echo "Signing bundle..."
source "$DIR/sign.sh" || exit 1

echo "Creating image..."
source "$DIR/package.sh" || exit 1

echo "Notarizing..."
source "$DIR/notarize.sh" || exit 1

echo "Success!"
