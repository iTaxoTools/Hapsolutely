#!/bin/sh

# Depends on: https://github.com/LinusU/node-appdmg
# npm install -g appdmg


DMG_CONFIG=$(mktemp -d -t "$APP_NAME")"/appdmg.json"

printf '
{
  "title": "'"$APP_NAME"'",
  "window": {
    "size": { "width": 600, "height": 320 }
    },
  "icon-size": 100,
  "icon": "'"$APP_ICON"'",
    "contents": [
      { "x": 400, "y": 140, "type": "link", "path": "/Applications" },
      { "x": 200, "y": 140, "type": "file", "path": "'"$APP_BUNDLE"'" }
    ],
  "format": "UDZO",
  "code-sign": {
    "signing-identity": "'"$CODESIGN_IDENTITY"'",
    "identifier": "'"$APP_IDENTIFIER"'"
  }
}
' > "$DMG_CONFIG"

rm -rf "$APP_IMAGE"
appdmg "$DMG_CONFIG" "$APP_IMAGE"
