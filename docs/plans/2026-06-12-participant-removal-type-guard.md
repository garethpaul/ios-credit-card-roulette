# Participant Removal Type Guard

status: completed

## Context

Participant lookup and winner selection ignore objects that are not
`ParticipantListItem`, but `removeParticipantAtIndex` removes any in-range
object. Corrupted or legacy array entries can therefore be mutated through a
participant-only action even though the rest of the UI rejects them.

## Completed Scope

- Require the indexed object to be a `ParticipantListItem` before removal.
- Preserve existing negative and out-of-range index handling.
- Add XCTest and static coverage proving invalid typed entries remain untouched.

## Verification

- `make check`
- `git diff --check`
- A mutation removing the type check must fail the baseline.
- Hosted macOS validation must execute the CardRoulette XCTest suite.
