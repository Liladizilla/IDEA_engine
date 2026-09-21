#!/usr/bin/env bash
# One-time setup. Run from mobile/ after installing Flutter.
# Generates the android/ folder (not included here), then applies IDEA's settings.
set -euo pipefail

flutter create . --platforms=android --org com.cyberzilla --project-name idea_app
flutter pub get
dart run flutter_launcher_icons

MANIFEST=android/app/src/main/AndroidManifest.xml
# Release builds need INTERNET (debug has it already).
grep -q 'android.permission.INTERNET' "$MANIFEST" || sed -i 's#<application#<uses-permission android:name="android.permission.INTERNET"/>\n    <application#' "$MANIFEST"
sed -i 's#android:label="[^"]*"#android:label="IDEA"#' "$MANIFEST"
# Emulator talking to a local http backend needs cleartext in debug only: see docs/DEPLOYMENT.md.

echo "Done. Run: flutter run   (mock data)   or   flutter run --dart-define=USE_MOCK=false"
