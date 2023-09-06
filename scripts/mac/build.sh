#!/bin/sh

# Build the mac distributable
# Executes all other scripts in order


DIR=$(readlink -f $(dirname $0))

echo "Reading config..."
source "$DIR/config.sh" || exit 1
echo "Building $APP_NAME..."

if [ "$CODESIGN_IDENTITY" = "UNKNOWN" ]; then
  echo "No Codesigning identity provided! Abort."
  echo ""
  echo "Try running: security find-identity -v -p codesigning"
  echo "Find the hash for \"Developer ID Application\""
  echo "Then: export CODESIGN_IDENTITY=\$HASH"
  exit 1
fi

echo "Calling pyinstaller..."
pyinstaller --noconfirm "$DIR/bundle.spec" || exit 1

echo "Cleaning up..."
find "$APP_BUNDLE" -name .DS_Store -delete

echo "Signing bundle..."
source "$DIR/sign.sh" || exit 1

echo "Creating image..."
source "$DIR/package.sh" || exit 1

echo "Notarizing..."
source "$DIR/notarize.sh" || exit 1

echo "Success!"
