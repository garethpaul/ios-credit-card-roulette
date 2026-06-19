# Winner Action Availability

status: completed

## Context

Winner presentation already rejects empty and invalid-only participant lists,
but the visible `Pick A Winner` button does not reflect that eligibility. After
the last typed participant is removed, the control remains enabled and accepts
a tap that intentionally produces no navigation or feedback.

## Priority

Keep the primary action's visible state aligned with the existing winner
eligibility invariant. This closes a concrete interaction gap without changing
participant storage, shake handling, random selection, or navigation behavior.

## Requirements

- R1. The winner button must be enabled exactly when `canPickWinner()` is true.
- R2. Initial participant loading, successful participant addition, and
  successful participant removal must refresh the button state.
- R3. Invalid or rejected mutations must not manufacture winner eligibility.
- R4. Button and shake winner presentation guards must remain authoritative.
- R5. XCTest and portable static contracts must reject missing synchronization
  at any production participant-mutation path.

## Implementation Units

### U1. Availability synchronization

**File:** `CardRoulette/ViewController.swift`

Add one helper that derives the button's enabled state from `canPickWinner()`.
Call it after each production path that mutates the participant collection.

### U2. Regression coverage

**Files:** `CardRouletteTests/CardRouletteTests.swift`,
`scripts/check-baseline.py`

Exercise empty, typed-participant, removal, and addition transitions with a
real button outlet. Add source contracts for the helper and every mutation
site so Linux validation remains mutation-sensitive.

### U3. Maintained evidence

**Files:** `AGENTS.md`, `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
and this plan.

Document the action-availability invariant while preserving the project's
local-only data and no-payment-processing boundaries.

## Test Scenarios

- An empty or invalid-only participant collection disables the winner button.
- Adding a typed participant enables the winner button.
- Removing the final typed participant disables the winner button.
- Initial sample loading leaves the winner button enabled.
- Existing winner, shake, responder, table, and unwind tests keep passing.

## Scope Boundaries

- Do not change participant normalization, storage, table layout, random winner
  selection, segue identifiers, or winner destination data.
- Do not add payment processing, analytics, networking, persistence, or new
  dependencies.
- Do not claim physical-device shake execution from Linux validation.

## Verification

- Run all four Make gates from the repository and the absolute Makefile from an
  external directory.
- Compile the checker, validate the XCTest runner shell, and rely on the hosted
  macOS workflow for authoritative XCTest and project-build execution.
- Reject isolated mutations for the derived button state, each production
  mutation hook, test discovery, guidance, and completed plan evidence.
- Audit the exact diff, generated artifacts, changed lines for credentials, and
  project/workflow/dependency preservation before commit.

## Work Completed

- Added derived winner-button availability and synchronized it after initial
  loading, successful addition, and successful removal.
- Added XCTest and portable contracts for empty, populated, added, and removed
  participant states.
- Updated maintained guidance without changing participant storage, winner
  selection, navigation, dependencies, or project metadata.

## Verification Completed

- All four Make gates passed after the completed implementation.
- The absolute Makefile check passed from an external directory.
- `python3 -m py_compile scripts/check-baseline.py` and
  `sh -n scripts/run-tests.sh` passed.
- Eight isolated hostile mutations were rejected for the derived state, three
  production mutation hooks, two XCTest contracts, maintained guidance, and
  completed plan evidence.
- `git diff --check` passed with intended-path, generated-artifact,
  project/workflow/dependency, and changed-line credential audits.
- Local `xcodebuild was unavailable`; hosted macOS remains authoritative for
  XCTest and project builds.
