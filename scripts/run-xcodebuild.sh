#!/bin/sh

set -eu

if [ "${1:-}" = "--available" ]; then
    [ -x /usr/bin/xcodebuild ]
    exit
fi

if [ ! -x /usr/bin/xcodebuild ]; then
    printf '%s\n' "xcodebuild is required to run CardRoulette tests." >&2
    exit 127
fi

exec /usr/bin/xcodebuild "$@"
