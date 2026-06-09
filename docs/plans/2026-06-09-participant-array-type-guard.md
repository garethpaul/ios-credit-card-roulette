# Participant Array Type Guard

status: completed

## Context

`ViewController` stores participants in a legacy `NSMutableArray`. Normal app
flows add `ParticipantListItem` instances, but the mutable array can still hold
other object types if future code writes to it directly. Winner selection and
row rendering should ignore unexpected entries instead of force-casting them.

## Objectives

- Add a typed participant list helper for winner selection.
- Add a guarded participant accessor for table row rendering.
- Keep malformed legacy player entries out of winner selection.
- Add XCTest and static baseline coverage for the typed participant guards.
- Preserve local-only participant behavior without adding storage, analytics, or
  payment-card handling.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
