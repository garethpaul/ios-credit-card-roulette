# Winner Presentation Single Flight

status: planned

## Context

The winner button and completed shake callback independently call
`performSegue(withIdentifier:sender:)`. A second input can arrive after the
first segue is requested but before `viewWillDisappear` resigns first-responder
status, allowing duplicate winner presentations to be queued.

## Priority

Keep winner navigation deterministic before making broader UI changes. The
existing participant eligibility and authoritative motion-subtype checks are
correct, but both entry points need one shared transition boundary.

## Requirements

- R1. Button and shake winner actions must use one presentation method.
- R2. The first eligible action must reserve the winner transition before
  requesting the segue.
- R3. Further actions must be rejected while that transition is in progress.
- R4. Returning to the visible roulette screen must allow a later winner round.
- R5. Existing motion-subtype, participant-type, and first-responder lifecycle
  behavior must remain intact.
- R6. XCTest and portable static contracts must reject removal of the guard,
  shared routing, or visibility reset.

## Implementation Units

### U1. Single-flight transition boundary

**File:** `CardRoulette/ViewController.swift`

Add a private transition-in-progress state and a shared
`presentWinnerIfPossible()` method. Reserve the transition before performing
the segue, route both input callbacks through the method, and reset the state
when the roulette controller appears again.

### U2. Regression coverage

**Files:** `CardRouletteTests/CardRouletteTests.swift`,
`scripts/check-baseline.py`

Use a recording controller to prove the first eligible request presents once,
an immediate second request is rejected, and a new visible lifecycle permits a
later request. Add source contracts for shared routing, pre-segue reservation,
and appearance reset so Linux validation remains mutation-sensitive.

### U3. Maintained evidence

**Files:** `AGENTS.md`, `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
and this plan.

Document the navigation invariant while preserving local-only participant
data, random sample winner selection, and the no-payment-processing boundary.

## Test Scenarios

- The first eligible winner request performs exactly one winner segue.
- A second request before disappearance is rejected without another segue.
- Empty or invalid-only participant collections remain ineligible.
- A subsequent `viewDidAppear` permits a new eligible winner request.
- Button and shake callbacks both use the guarded presentation method.
- Existing responder, motion, table, unwind, and winner destination tests keep
  passing.

## Scope Boundaries

- Do not change participant normalization, storage, table behavior, random
  winner selection, segue identifiers, or destination data.
- Do not add payment processing, analytics, networking, persistence, or new
  dependencies.
- Do not claim physical-device shake execution from Linux validation.

## Verification

- Run all four Make gates from the repository and the absolute Makefile from an
  external directory.
- Compile the checker, validate the XCTest runner shell, and rely on the hosted
  macOS workflow for authoritative XCTest and project-build execution.
- Reject isolated mutations for shared callback routing, transition
  reservation ordering, duplicate suppression, appearance reset, test
  discovery, guidance, and completed plan evidence.
- Audit the exact diff, generated artifacts, changed lines for credentials, and
  project/workflow/dependency preservation before commit.
