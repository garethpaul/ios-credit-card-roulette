# Participant Name Normalizer Plan

status: completed

## Context

Participant names are entered from both the add-participant screen and the winner
screen. Each controller should use the same trimming and blank-input behavior so
local participant state cannot diverge between flows.

## Objectives

- Move participant-name trimming and blank rejection into a shared helper.
- Use the helper from both participant-entry controllers.
- Replace generated XCTest placeholders with focused assertions for trimmed,
  blank, and missing names.
- Keep participant data local-only and avoid introducing persistence or payment
  handling.
- Extend the static baseline so helper usage, testability wiring, and real tests
  remain visible without Xcode.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
