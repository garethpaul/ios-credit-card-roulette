# Authoritative Shake Motion Routing

status: planned

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

Pending implementation.

## Verification Completed

Pending implementation and exact evidence.
