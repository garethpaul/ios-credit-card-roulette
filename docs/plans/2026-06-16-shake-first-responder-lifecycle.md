# Shake First-Responder Lifecycle

status: in_progress

## Context

`ViewController` implements `motionEnded(_:,with:)`, but it neither opts into
first-responder status nor acquires that status while its roulette screen is
visible. The winner-routing predicate is therefore correct in isolation while
a physical shake can remain outside the controller's responder path.

## Priority

Restore the user-visible shake trigger before pursuing broader UI changes. The
button path already provides a fallback, but the product explicitly presents
shake as an equivalent winner action and maintains dedicated routing logic for
it.

## Requirements

- R1. The roulette controller must explicitly allow first-responder status.
- R2. The controller must request first-responder status after it becomes
  visible.
- R3. The controller must relinquish first-responder status when it begins to
  disappear.
- R4. Existing authoritative motion-subtype and typed-participant winner gates
  must remain unchanged.
- R5. Deterministic tests and static contracts must reject removal or
  reordering of the visibility-scoped responder lifecycle.
- R6. Documentation must preserve the local-only participant and
  no-payment-processing boundaries.

## Implementation Units

### U1. Visibility-scoped responder ownership

**File:** `CardRoulette/ViewController.swift`

Opt the controller into first-responder status, acquire it after the visible
lifecycle begins, and relinquish it before leaving the screen. Keep motion
identity and winner eligibility in their existing helpers.

### U2. Lifecycle regression coverage

**Files:** `CardRouletteTests/CardRouletteTests.swift`,
`scripts/check-baseline.py`

Use an instrumented controller subclass to verify appearance and disappearance
request the expected responder transitions. Add source contracts that require
the opt-in and lifecycle placement so Linux validation remains
mutation-sensitive when XCTest is unavailable.

### U3. Maintained evidence

**Files:** `AGENTS.md`, `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
and this plan.

Record why physical shake delivery requires visible first-responder ownership,
while retaining the sample's local-only participant and no-payment scope.

## Test Scenarios

- A visible roulette controller requests first-responder status once per
  appearance.
- A disappearing roulette controller relinquishes first-responder status.
- Removing `canBecomeFirstResponder`, appearance acquisition, disappearance
  resignation, lifecycle tests, or completed evidence fails the portable gate.
- Existing shake/non-shake and empty/typed participant routing tests continue
  to pass.

## Scope Boundaries

- Do not change participant normalization, storage, table behavior, random
  winner selection, segue identifiers, or winner presentation data.
- Do not add payment processing, analytics, networking, persistence, or new
  dependencies.
- Do not claim physical-device shake execution from Linux validation.

## Verification

- Run all four Make gates from the repository and the absolute Makefile from an
  external directory.
- Compile the checker, validate the XCTest runner shell, and run hosted XCTest
  through the existing workflow.
- Reject isolated mutations for responder opt-in, appearance acquisition,
  disappearance resignation, lifecycle test discovery, guidance, and plan
  status.
- Audit the exact diff, generated artifacts, changed lines for credentials,
  and project/workflow/dependency preservation before commit.

## Verification Completed

Pending implementation and validation.
