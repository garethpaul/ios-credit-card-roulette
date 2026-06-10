# Winner Destination Guard

status: completed

## Context

The main controller presents the winner screen from a storyboard segue. The
segue identifier was checked, but the destination controller was still
force-cast to `WinnerViewController`. A storyboard miswire could therefore crash
before the fallback winner text or typed participant filtering had a chance to
run.

## Completed Scope

- Added a `configureWinnerDestination` helper that ignores unexpected
  destinations instead of force-casting them.
- Routed the `presentWinner` segue through the helper.
- Added focused XCTest assertions for unexpected destinations, empty participant
  fallback text, and typed participant winner propagation.
- Extended the static baseline and docs so winner destination handling remains
  guarded without adding persistence, network, or payment-card handling.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
