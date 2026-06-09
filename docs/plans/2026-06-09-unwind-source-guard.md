# Unwind Source Guard

status: completed

## Context

The list screen accepts participant items through storyboard unwind segues.
`AddParticipantViewController` and `WinnerViewController` can both produce a
`participantItem`, but the unwind action force-cast the source to only the add
participant controller. A winner-screen unwind could therefore crash before the
participant was added.

## Objectives

- Extract participant-item lookup for known unwind sources.
- Support add-participant and winner unwind sources.
- Ignore unrecognized unwind sources instead of force-casting them.
- Add XCTest and static baseline coverage for the unwind source guard.

## Verification

- `make check`
- `git diff --check`
