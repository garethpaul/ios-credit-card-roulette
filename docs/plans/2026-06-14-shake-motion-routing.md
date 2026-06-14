# Authoritative Shake Motion Routing

status: completed

## Context

`motionEnded(_:,with:)` receives the completed motion subtype directly, but the
controller ignores that argument and checks `event?.subtype` instead. A valid
shake can therefore be ignored when the event is nil or carries different
metadata.

## Priority

Winner presentation should follow UIKit's typed motion callback contract. This
is a narrow user-input routing defect and does not require changing participant
selection or navigation data.

## Scope

1. Decide shake eligibility from the `motion` argument supplied to
   `motionEnded`.
2. Keep winner presentation gated on at least one typed participant.
3. Add deterministic XCTest coverage for shake, non-shake, and empty-player
   combinations without invoking a real segue.
4. Add mutation-sensitive static and completed-plan contracts plus synchronized
   maintenance guidance.
5. Preserve local-only participant data and the explicit no-payment-processing
   boundary.

## Verification Plan

- Run all four Make gates from the checkout and through the absolute Makefile
  path from an external directory.
- Run checker compilation and XCTest runner shell syntax.
- Reject mutations that restore event-subtype routing, remove the motion
  predicate, remove participant gating, remove XCTest coverage, or weaken plan
  evidence.
- Inspect the exact diff, generated artifacts, changed lines for credentials,
  and preservation of project/workflow/scheme/runner files.

## Risk And Rollback

The change only selects the authoritative motion input before existing winner
presentation. Rollback restores event-dependent shake routing; participant and
payment behavior remain unchanged.

## Work Completed

- Added a typed `shouldPresentWinner(for:)` predicate that accepts only
  `.motionShake` and retains the existing typed-participant eligibility check.
- Routed `motionEnded` through the callback's authoritative `motion` argument
  instead of optional event metadata.
- Added deterministic XCTest coverage, mutation-sensitive static contracts,
  and synchronized maintenance and privacy guidance.

## Verification Completed

- All four Make gates passed in an isolated completed-plan preflight copy and
  again in the implementation worktree.
- The absolute Makefile check passed from an external directory.
- `python3 -m py_compile scripts/check-baseline.py` passed; its exact generated
  bytecode path was removed before the final artifact audit.
- `sh -n scripts/run-tests.sh` passed.
- Five isolated hostile mutations were rejected: restoring event-subtype
  routing, removing motion identity, removing participant gating, removing
  XCTest discovery, or deleting required plan evidence each failed the gate.
- `git diff --check` passed, along with exact intended-path, generated-artifact,
  changed-line credential, privacy/payment, dependency, project, workflow,
  shared-scheme, and runner-preservation audits.
- Local `xcodebuild was unavailable`; no local XCTest execution is claimed.
