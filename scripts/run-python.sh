#!/bin/sh

set -eu

if [ -x /usr/bin/python3 ]; then
    exec /usr/bin/python3 -I -B "$@"
fi

if [ -x /opt/homebrew/bin/python3 ]; then
    exec /opt/homebrew/bin/python3 -I -B "$@"
fi

printf '%s\n' "python3 is required for CardRoulette verification." >&2
exit 127
