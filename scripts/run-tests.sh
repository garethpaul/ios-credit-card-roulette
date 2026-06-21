#!/bin/sh

set -eu

PROJECT=${XCODE_PROJECT:-CardRoulette.xcodeproj}
SCHEME=${XCODE_SCHEME:-CardRoulette}
CONFIGURATION=${CONFIGURATION:-Debug}
DERIVED_DATA_PATH=${DERIVED_DATA_PATH:-${TMPDIR:-/tmp}/CardRouletteDerivedData}
XCODEBUILD=${XCODEBUILD:-/usr/bin/xcodebuild}

if [ -n "${IOS_DESTINATION:-}" ]; then
    DESTINATION=$IOS_DESTINATION
elif [ -n "${IOS_SIMULATOR_NAME:-}" ]; then
    DESTINATION="platform=iOS Simulator,name=${IOS_SIMULATOR_NAME}"
else
    SIMULATOR_NAME=$(/usr/bin/xcrun simctl list devices available | /usr/bin/awk -F '[()]' '/^[[:space:]]+iPhone/ { name=$1; sub(/^[[:space:]]+/, "", name); sub(/[[:space:]]+$/, "", name); print name; exit }')
    if [ -z "$SIMULATOR_NAME" ]; then
        printf '%s\n' "No available iPhone simulator was found." >&2
        exit 1
    fi
    DESTINATION="platform=iOS Simulator,name=${SIMULATOR_NAME}"
fi

"$XCODEBUILD" \
    -project "$PROJECT" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION" \
    -destination "$DESTINATION" \
    -derivedDataPath "$DERIVED_DATA_PATH" \
    CODE_SIGNING_ALLOWED=NO \
    test
