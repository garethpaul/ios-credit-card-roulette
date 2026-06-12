# Hosted XCTest

status: completed

## Context

The Swift 5 migration compiled the app and XCTest bundle on current Xcode, but
hosted CI did not execute the twelve participant normalization, array safety,
removal, unwind, and winner-destination tests because no shared scheme existed.

## Completed Scope

- Added a shared `CardRoulette` scheme containing the app and test targets.
- Added portable iPhone simulator discovery with explicit destination overrides.
- Kept `make check` as the SDK-free privacy gate and made `make test` execute
  XCTest whenever Xcode is available.
- Changed hosted macOS CI to run the complete unsigned `make test` gate.
- Preserved the local-only participant and no-payment-processing boundary.
- Rejected generic payment processor identifiers and common payment SDK surfaces.

## Verification

- `make check`
- `make test`
- `sh -n scripts/run-tests.sh`
- hosted macOS XCTest run
- hostile mutations removing the scheme, test command, simulator discovery,
  unsigned execution, or credential-free checkout must fail
- a mutation adding a quoted plain-HTTP endpoint must fail
- a mutation adding a payment processor must fail
- `git diff --check`
