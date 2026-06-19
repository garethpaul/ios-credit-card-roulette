#!/bin/sh

set -eu

PROJECT=${XCODE_PROJECT:-CardRoulette.xcodeproj}
SCHEME=${XCODE_SCHEME:-CardRoulette}
CONFIGURATION=${CONFIGURATION:-Debug}
DERIVED_DATA_PATH=${DERIVED_DATA_PATH:-${TMPDIR:-/tmp}/CardRouletteDerivedData}

if ! command -v xcodebuild >/dev/null 2>&1; then
    printf '%s\n' "xcodebuild is required to run CardRoulette tests." >&2
    exit 127
fi

if [ -n "${IOS_DESTINATION:-}" ]; then
    DESTINATION=$IOS_DESTINATION
elif [ -n "${IOS_SIMULATOR_NAME:-}" ]; then
    DESTINATION="platform=iOS Simulator,name=${IOS_SIMULATOR_NAME}"
else
    SIMULATOR_NAME=$(xcrun simctl list devices available | awk -F '[()]' '/^[[:space:]]+iPhone/ { name=$1; sub(/^[[:space:]]+/, "", name); sub(/[[:space:]]+$/, "", name); print name; exit }')
    if [ -z "$SIMULATOR_NAME" ]; then
        printf '%s\n' "No available iPhone simulator was found." >&2
        exit 1
    fi
    DESTINATION="platform=iOS Simulator,name=${SIMULATOR_NAME}"
fi

xcodebuild \
    -project "$PROJECT" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION" \
    -destination "$DESTINATION" \
    -derivedDataPath "$DERIVED_DATA_PATH" \
    CODE_SIGNING_ALLOWED=NO \
    test
