#!/bin/sh

codesign -v --deep --force --options=runtime \
  --entitlements "$APP_ENTITLEMENTS" \
  --sign "$CODESIGN_IDENTITY" \
  --timestamp $APP_BUNDLE
