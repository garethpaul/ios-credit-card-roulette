# Typed Winner Trigger Eligibility

status: completed

## Context

Winner selection filters `players` to `ParticipantListItem` values, but button
and shake triggers still allow navigation whenever the raw mutable array count
is nonzero. An invalid entry can therefore present the winner screen even
though no typed participant is eligible and the destination can only show its
fallback message.

## Priority

Navigation eligibility and winner selection should use the same participant
boundary. This avoids presenting a terminal game screen for corrupt or legacy
array contents while preserving the existing fallback as defense in depth.

## Requirements

- R1. Add one shared eligibility helper based on filtered typed participants.
- R2. Button-triggered winner navigation must require that helper.
- R3. Shake-triggered winner navigation must require both a shake event and that
  helper.
- R4. Invalid-only player arrays must not be eligible; a valid participant among
  invalid entries must remain eligible.
- R5. Preserve random winner selection, destination fallback, participant
  normalization/removal, unwind behavior, UI copy, and local-only data handling.
- R6. Add executable XCTest coverage and method-scoped static contracts.

## Implementation Units

### U1. Centralize trigger eligibility

- **File:** `CardRoulette/ViewController.swift`
- Add a typed-participant eligibility helper and use it from button and shake
  paths instead of raw array count.

### U2. Add eligibility regression coverage

- **File:** `CardRouletteTests/CardRouletteTests.swift`
- Prove empty and invalid-only arrays are rejected while mixed arrays containing
  a valid participant are accepted.

### U3. Enforce and document the boundary

- **Files:** `scripts/check-baseline.py`, `README.md`, `SECURITY.md`,
  `VISION.md`, `CHANGES.md`
- Require both trigger paths, focused tests, and completed verification evidence.

## Scope Boundaries

- Do not change navigation identifiers, storyboard wiring, random selection, or
  destination fallback behavior.
- Do not replace the legacy mutable array in this focused change.
- Do not add payment processing, persistence, networking, or analytics.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile scripts/check-baseline.py`
- `sh -n scripts/run-tests.sh`
- Parse plist, storyboard, XIB, scheme, workspace, project, and workflow metadata
  with all available local parsers.
- `git diff --check`
- Hostile mutations restoring raw count in either trigger, weakening typed
  eligibility, removing empty/invalid/mixed tests, plan status, or verification
  evidence must be rejected.

## Verification Completed

- All four Make gates (`make lint`, `make test`, `make build`, and
  `make check`) passed against the completed implementation and plan.
- `python3 -m py_compile scripts/check-baseline.py`, `sh -n
  scripts/run-tests.sh`, available plist/XML/workflow parsers, and
  `git diff --check` passed.
- A prepared baseline passed and eight hostile mutations were rejected. They
  restored raw count in either trigger, weakened the shared helper, removed the
  empty, invalid-only, or valid-participant assertions, reopened the plan, or
  removed required verification evidence.
- `xcodebuild` was unavailable on this Linux host, so the fifteen-test simulator
  suite was not executed locally. Hosted macOS remains responsible for
  executable XCTest evidence; physical shake behavior remains manual coverage.
