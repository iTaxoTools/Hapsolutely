#!/bin/sh

xcrun notarytool submit "$APP_IMAGE" \
  --keychain-profile "AC_PASSWORD" \
  --wait
xcrun stapler staple "$APP_IMAGE"

# verify
spctl -a -t open -vvv --context context:primary-signature "$APP_IMAGE"
